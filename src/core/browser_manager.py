"""Browser instance management with nodriver."""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import nodriver as uc
from nodriver import Browser, Tab

from core.debug_logger import debug_logger
from core.dynamic_hook_system import dynamic_hook_system
from core.models import BrowserInstance, BrowserOptions, BrowserState, PageState
from core.persistent_storage import persistent_storage
from core.platform_utils import check_browser_executable, get_platform_info, merge_browser_args
from core.process_cleanup import process_cleanup


class BrowserManager:
    """Manages multiple browser instances."""

    def __init__(self):
        self._instances: Dict[str, dict] = {}
        self._lock = asyncio.Lock()

    async def spawn_browser(self, options: BrowserOptions) -> BrowserInstance:
        """
        Spawn a new browser instance with given options.

        Args:
            options (BrowserOptions): Options for browser configuration.

        Returns:
            BrowserInstance: The spawned browser instance.
        """
        instance_id = str(uuid.uuid4())

        instance = BrowserInstance(
            instance_id=instance_id,
            headless=options.headless,
            user_agent=options.user_agent,
            viewport={"width": options.viewport_width, "height": options.viewport_height},
        )

        try:
            platform_info = get_platform_info()

            # Detect the best available browser executable (Chrome, Chromium, or Edge)
            browser_executable = check_browser_executable()
            if not browser_executable:
                raise Exception("No compatible browser found (Chrome, Chromium, or Microsoft Edge)")

            # Identify browser type for logging
            browser_type = "Unknown"
            if "edge" in browser_executable.lower() or "msedge" in browser_executable.lower():
                browser_type = "Microsoft Edge"
            elif "chromium" in browser_executable.lower():
                browser_type = "Chromium"
            elif "chrome" in browser_executable.lower():
                browser_type = "Google Chrome"

            debug_logger.log_info(
                "browser_manager",
                "spawn_browser",
                f"Platform: {platform_info['system']} | Root: {platform_info['is_root']} | Container: {platform_info['is_container']} | Sandbox: {options.sandbox} | Browser: {browser_type} ({browser_executable})",
            )

            config = uc.Config(
                headless=options.headless,
                user_data_dir=options.user_data_dir,
                sandbox=options.sandbox,
                browser_executable_path=browser_executable,
                browser_args=merge_browser_args(),
            )

            browser = await uc.start(config=config)
            tab = browser.main_tab

            if hasattr(browser, "_process") and browser._process:
                process_cleanup.track_browser_process(instance_id, browser._process)
            else:
                debug_logger.log_warning(
                    "browser_manager",
                    "spawn_browser",
                    f"Browser {instance_id} has no process to track",
                )

            if options.user_agent:
                await tab.send(
                    uc.cdp.emulation.set_user_agent_override(user_agent=options.user_agent)
                )

            if options.extra_headers:
                await tab.send(uc.cdp.network.set_extra_http_headers(headers=options.extra_headers))

            await tab.set_window_size(
                left=0, top=0, width=options.viewport_width, height=options.viewport_height
            )
            debug_logger.log_info(
                "browser_manager",
                "spawn_browser",
                f"Viewport set to {options.viewport_width}x{options.viewport_height}",
            )

            await self._setup_dynamic_hooks(tab, instance_id)

            async with self._lock:
                self._instances[instance_id] = {
                    "browser": browser,
                    "tab": tab,
                    "instance": instance,
                    "options": options,
                    "network_data": [],
                }

            instance.state = BrowserState.READY
            instance.update_activity()

            persistent_storage.store_instance(
                instance_id,
                {
                    "state": instance.state.value,
                    "created_at": instance.created_at.isoformat(),
                    "current_url": getattr(tab, "url", ""),
                    "title": "Browser Instance",
                },
            )

        except Exception as e:
            instance.state = BrowserState.ERROR
            raise Exception(f"Failed to spawn browser: {str(e)}")

        return instance

    async def _setup_dynamic_hooks(self, tab: Tab, instance_id: str):
        """Setup dynamic hook system for browser instance."""
        try:
            dynamic_hook_system.add_instance(instance_id)

            await dynamic_hook_system.setup_interception(tab, instance_id)

            debug_logger.log_info(
                "browser_manager",
                "_setup_dynamic_hooks",
                f"Dynamic hook system setup complete for instance {instance_id}",
            )

        except Exception as e:
            debug_logger.log_error(
                "browser_manager",
                "_setup_dynamic_hooks",
                f"Failed to setup dynamic hooks for {instance_id}: {e}",
            )

    async def check_instance_health(self, instance_id: str) -> Dict[str, Any]:
        """
        Check if browser instance is healthy and WebSocket connection is alive.

        Args:
            instance_id (str): The ID of the browser instance.

        Returns:
            Dict with 'healthy' (bool), 'reason' (str), and 'can_recover' (bool)
        """
        tab = await self.get_tab(instance_id)
        if not tab:
            return {"healthy": False, "reason": "Tab not found", "can_recover": False}

        try:
            # Quick health check - try to evaluate simple expression
            result = await asyncio.wait_for(tab.evaluate("1+1"), timeout=3.0)
            if result == 2:
                return {"healthy": True, "reason": "Connection is alive", "can_recover": True}
        except asyncio.TimeoutError:
            return {
                "healthy": False,
                "reason": "WebSocket timeout - connection may be dead",
                "can_recover": False,
                "recommendation": "Close this instance and create a new one",
            }
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg or "connection" in error_msg:
                return {
                    "healthy": False,
                    "reason": f"WebSocket connection lost: {str(e)}",
                    "can_recover": False,
                    "recommendation": "Close this instance and create a new one. The browser process may have crashed.",
                }
            return {
                "healthy": False,
                "reason": f"Unknown error: {str(e)}",
                "can_recover": False,
                "recommendation": "Try closing and recreating the instance",
            }

    async def get_instance(self, instance_id: str) -> Optional[dict]:
        """
        Get browser instance by ID.

        Args:
            instance_id (str): The ID of the browser instance.

        Returns:
            Optional[dict]: The browser instance data if found, else None.
        """
        async with self._lock:
            return self._instances.get(instance_id)

    async def list_instances(self) -> List[BrowserInstance]:
        """
        List all browser instances.

        Returns:
            List[BrowserInstance]: List of all browser instances.
        """
        async with self._lock:
            return [data["instance"] for data in self._instances.values()]

    async def close_instance(self, instance_id: str) -> bool:
        """
        Close and remove a browser instance.

        Args:
            instance_id (str): The ID of the browser instance to close.

        Returns:
            bool: True if closed successfully, False otherwise.
        """
        import asyncio

        async def _do_close():
            async with self._lock:
                if instance_id not in self._instances:
                    return False

                data = self._instances[instance_id]
                browser = data["browser"]
                instance = data["instance"]

                try:
                    if hasattr(browser, "tabs") and browser.tabs:
                        for tab in browser.tabs[:]:
                            try:
                                await tab.close()
                            except Exception as e:
                                debug_logger.log_warning(
                                    "browser_manager", "close_instance", f"Failed to close tab: {e}"
                                )
                except Exception as e:
                    debug_logger.log_warning(
                        "browser_manager", "close_instance", f"Tab closing block failed: {e}"
                    )

                try:
                    if hasattr(browser, "connection") and browser.connection:
                        # Avoid unhandled task exceptions during shutdown by awaiting disconnect.
                        try:
                            await asyncio.wait_for(browser.connection.disconnect(), timeout=2.0)
                            debug_logger.log_info(
                                "browser_manager",
                                "close_connection",
                                "closed connection with await and timeout",
                            )
                        except (asyncio.TimeoutError, Exception) as e:
                            debug_logger.log_info(
                                "browser_manager",
                                "close_connection",
                                f"connection disconnect failed or timed out: {e}",
                            )
                except Exception as e:
                    debug_logger.log_info(
                        "browser_manager", "close_connection", f"connection disconnect failed: {e}"
                    )

                try:
                    import nodriver.cdp.browser as cdp_browser

                    if hasattr(browser, "connection") and browser.connection:
                        await browser.connection.send(cdp_browser.close())
                except Exception as e:
                    debug_logger.log_warning(
                        "browser_manager", "close_instance", f"Failed to send CDP close: {e}"
                    )

                try:
                    await browser.stop()
                except Exception as e:
                    debug_logger.log_warning(
                        "browser_manager", "close_instance", f"Failed to stop browser: {e}"
                    )

                if (
                    hasattr(browser, "_process")
                    and browser._process
                    and browser._process.returncode is None
                ):
                    import os

                    for attempt in range(3):
                        try:
                            browser._process.terminate()
                            debug_logger.log_info(
                                "browser_manager",
                                "terminate_process",
                                f"terminated browser with pid {browser._process.pid} successfully on attempt {attempt + 1}",
                            )
                            break
                        except Exception:
                            try:
                                browser._process.kill()
                                debug_logger.log_info(
                                    "browser_manager",
                                    "kill_process",
                                    f"killed browser with pid {browser._process.pid} successfully on attempt {attempt + 1}",
                                )
                                break
                            except Exception:
                                try:
                                    if hasattr(browser, "_process_pid") and browser._process_pid:
                                        os.kill(browser._process_pid, 15)
                                        debug_logger.log_info(
                                            "browser_manager",
                                            "kill_process",
                                            f"killed browser with pid {browser._process_pid} using signal 15 successfully on attempt {attempt + 1}",
                                        )
                                        break
                                except (PermissionError, ProcessLookupError) as e:
                                    debug_logger.log_info(
                                        "browser_manager",
                                        "kill_process",
                                        f"browser already stopped or no permission to kill: {e}",
                                    )
                                    break
                                except Exception as e:
                                    if attempt == 2:
                                        debug_logger.log_error("browser_manager", "kill_process", e)
                    # Give asyncio a chance to close subprocess transports cleanly.
                    try:
                        await asyncio.wait_for(browser._process.wait(), timeout=3.0)
                    except Exception as e:
                        debug_logger.log_warning(
                            "browser_manager", "close_instance", f"Process wait failed: {e}"
                        )

                try:
                    if hasattr(browser, "_process"):
                        browser._process = None
                    if hasattr(browser, "_process_pid"):
                        browser._process_pid = None

                    instance.state = BrowserState.CLOSED
                except Exception as e:
                    debug_logger.log_warning(
                        "browser_manager", "close_instance", f"Failed to cleanup browser state: {e}"
                    )

                del self._instances[instance_id]

                persistent_storage.remove_instance(instance_id)
                try:
                    process_cleanup.untrack_browser_process(instance_id)
                except Exception as e:
                    debug_logger.log_warning(
                        "browser_manager", "close_instance", f"Failed to untrack process: {e}"
                    )

                # Schedule deferred deletion of all temp files associated with
                # this instance (files are deleted after a grace period, not immediately).
                try:
                    from core.temp_file_manager import temp_file_manager

                    temp_file_manager.schedule_instance_cleanup(instance_id)
                except Exception as e:
                    debug_logger.log_warning(
                        "browser_manager",
                        "close_instance",
                        f"Failed to schedule instance temp file cleanup: {e}",
                    )

                return True

        try:
            return await asyncio.wait_for(_do_close(), timeout=5.0)
        except asyncio.TimeoutError:
            debug_logger.log_info(
                "browser_manager",
                "close_instance",
                f"Close timeout for {instance_id}, forcing cleanup",
            )
            try:
                async with self._lock:
                    if instance_id in self._instances:
                        data = self._instances[instance_id]
                        data["instance"].state = BrowserState.CLOSED
                        del self._instances[instance_id]
                        persistent_storage.remove_instance(instance_id)
            except Exception as e:
                debug_logger.log_warning(
                    "browser_manager", "close_instance", f"Forced cleanup failed: {e}"
                )
            return True
        except Exception as e:
            debug_logger.log_error("browser_manager", "close_instance", e)
            return False

    async def get_tab(self, instance_id: str) -> Optional[Tab]:
        """
        Get the main tab for a browser instance.

        Args:
            instance_id (str): The ID of the browser instance.

        Returns:
            Optional[Tab]: The main tab if found, else None.
        """
        data = await self.get_instance(instance_id)
        if data:
            return data["tab"]
        return None

    async def get_browser(self, instance_id: str) -> Optional[Browser]:
        """
        Get the browser object for an instance.

        Args:
            instance_id (str): The ID of the browser instance.

        Returns:
            Optional[Browser]: The browser object if found, else None.
        """
        data = await self.get_instance(instance_id)
        if data:
            return data["browser"]
        return None

    async def list_tabs(self, instance_id: str) -> List[Dict[str, str]]:
        """
        List all tabs for a browser instance.

        Args:
            instance_id (str): The ID of the browser instance.

        Returns:
            List[Dict[str, str]]: List of tab information dictionaries.
        """
        browser = await self.get_browser(instance_id)
        if not browser:
            return []

        await browser.update_targets()

        tabs = []
        for tab in browser.tabs:
            tabs.append(
                {
                    "tab_id": str(tab.target.target_id),
                    "url": getattr(tab, "url", "") or "",
                    "title": getattr(tab.target, "title", "") or "Untitled",
                    "type": getattr(tab.target, "type_", "page"),
                }
            )

        return tabs

    async def switch_to_tab(self, instance_id: str, tab_id: str) -> bool:
        """
        Switch to a specific tab by bringing it to front.

        Args:
            instance_id (str): The ID of the browser instance.
            tab_id (str): The target ID of the tab to switch to.

        Returns:
            bool: True if switched successfully, False otherwise.
        """
        browser = await self.get_browser(instance_id)
        if not browser:
            return False

        await browser.update_targets()

        target_tab = None
        for tab in browser.tabs:
            if str(tab.target.target_id) == tab_id:
                target_tab = tab
                break

        if not target_tab:
            return False

        try:
            await target_tab.bring_to_front()
            async with self._lock:
                if instance_id in self._instances:
                    self._instances[instance_id]["tab"] = target_tab

            return True
        except Exception:
            return False

    async def get_active_tab(self, instance_id: str) -> Optional[Tab]:
        """
        Get the currently active tab.

        Args:
            instance_id (str): The ID of the browser instance.

        Returns:
            Optional[Tab]: The active tab if found, else None.
        """
        return await self.get_tab(instance_id)

    async def close_tab(self, instance_id: str, tab_id: str) -> bool:
        """
        Close a specific tab.

        Args:
            instance_id (str): The ID of the browser instance.
            tab_id (str): The target ID of the tab to close.

        Returns:
            bool: True if closed successfully, False otherwise.
        """
        browser = await self.get_browser(instance_id)
        if not browser:
            return False

        target_tab = None
        for tab in browser.tabs:
            if str(tab.target.target_id) == tab_id:
                target_tab = tab
                break

        if not target_tab:
            return False

        try:
            await target_tab.close()
            return True
        except Exception:
            return False

    async def update_instance_state(self, instance_id: str, url: str = None, title: str = None):
        """
        Update instance state after navigation or action.

        Args:
            instance_id (str): The ID of the browser instance.
            url (str, optional): The current URL to update.
            title (str, optional): The title to update.
        """
        async with self._lock:
            if instance_id in self._instances:
                instance = self._instances[instance_id]["instance"]
                if url:
                    instance.current_url = url
                if title:
                    instance.title = title
                instance.update_activity()

    async def get_page_state(self, instance_id: str) -> Optional[PageState]:
        """
        Get complete page state for an instance.

        Args:
            instance_id (str): The ID of the browser instance.

        Returns:
            Optional[PageState]: The page state if available, else None.
        """
        tab = await self.get_tab(instance_id)
        if not tab:
            return None

        try:
            # Single JS call to collect all page state at once — avoids multiple
            # round-trips over CDP which can accumulate timeouts on slow connections.
            # IMPORTANT: We JSON.stringify and parse back to avoid nodriver serialization issues
            result_json = await asyncio.wait_for(
                tab.evaluate("""
                (function() {
                    var ls = {}, ss = {};
                    try {
                        var lsKeys = Object.keys(localStorage);
                        for (var i = 0; i < lsKeys.length; i++) {
                            ls[lsKeys[i]] = localStorage.getItem(lsKeys[i]);
                        }
                    } catch(e) {}
                    try {
                        var ssKeys = Object.keys(sessionStorage);
                        for (var i = 0; i < ssKeys.length; i++) {
                            ss[ssKeys[i]] = sessionStorage.getItem(ssKeys[i]);
                        }
                    } catch(e) {}
                    return JSON.stringify({
                        url: window.location.href,
                        title: document.title,
                        ready_state: document.readyState,
                        local_storage: ls,
                        session_storage: ss,
                        viewport: {
                            width: window.innerWidth,
                            height: window.innerHeight,
                            devicePixelRatio: window.devicePixelRatio
                        }
                    });
                })()
                """),
                timeout=5.0,  # Reduced from 10.0 to 5.0
            )

            # Parse the JSON string to dict
            import json

            if isinstance(result_json, str):
                result = json.loads(result_json)
            else:
                # If somehow already a dict/list, use as-is
                result = result_json

            if not isinstance(result, dict):
                debug_logger.log_info(
                    "browser_manager",
                    "get_page_state",
                    f"JS returned {type(result)}, returning minimal state",
                )
                # When JS returns unexpected type, skip fallback to avoid blocking
                # Use minimal state - the important fields are url and title
                url = ""
                title = ""
                ready_state = "unknown"
                local_storage = {}
                session_storage = {}
                viewport = {"width": 1920, "height": 1080, "devicePixelRatio": 1}
            else:
                url = result.get("url", "")
                title = result.get("title", "")
                ready_state = result.get("ready_state", "complete")
                local_storage = result.get("local_storage", {})
                session_storage = result.get("session_storage", {})
                viewport = result.get(
                    "viewport", {"width": 1920, "height": 1080, "devicePixelRatio": 1}
                )

            if not isinstance(viewport, dict):
                viewport = {"width": 1920, "height": 1080, "devicePixelRatio": 1}

            # DISABLED: Cookies CDP call causing hangs in nodriver
            # cookies = []
            # try:
            #     cookies_result = await asyncio.wait_for(
            #         tab.send(uc.cdp.storage.get_cookies(browser_context_id=None)), timeout=2.0
            #     )
            #     cookies = (
            #         cookies_result.get("cookies", []) if isinstance(cookies_result, dict) else []
            #     )
            # except Exception:
            #     pass
            cookies = []  # Skip cookies to avoid nodriver hangs

            return PageState(
                instance_id=instance_id,
                url=url,
                title=title,
                ready_state=ready_state,
                cookies=cookies,
                local_storage=local_storage,
                session_storage=session_storage,
                viewport=viewport,
            )

        except asyncio.TimeoutError:
            raise Exception(
                f"Timeout ao obter estado da página - a conexão WebSocket pode estar perdida"
            )
        except Exception as e:
            # Check if it's a WebSocket error
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    f"Conexão WebSocket perdida - o browser pode ter crashado. Feche e recrie a instância. Erro: {str(e)}"
                )
            raise Exception(f"Failed to get page state: {str(e)}")

    async def cleanup_inactive(self, timeout_minutes: int = 30):
        """
        Clean up inactive browser instances.

        Args:
            timeout_minutes (int, optional): Timeout in minutes to consider an instance inactive. Defaults to 30.
        """
        now = datetime.now()
        timeout = timedelta(minutes=timeout_minutes)

        to_close = []
        async with self._lock:
            for instance_id, data in self._instances.items():
                instance = data["instance"]
                if now - instance.last_activity > timeout:
                    to_close.append(instance_id)

        for instance_id in to_close:
            await self.close_instance(instance_id)

    async def close_all(self):
        """
        Close all browser instances.

        Closes all currently managed browser instances.
        """
        instance_ids = list(self._instances.keys())
        for instance_id in instance_ids:
            await self.close_instance(instance_id)
