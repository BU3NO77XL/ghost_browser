"""Browser management tools: spawn, navigate, login, tabs navigation."""

import asyncio
from typing import Any, Dict, List, Optional

from core.cookie_manager import inject_cookies_from_file, wait_for_target_host
from core.login_guard import check_pending_login_guard
from core.models import BrowserOptions


def normalize_sandbox_option(sandbox: Optional[Any]) -> bool:
    """Normalize MCP sandbox inputs into nodriver's sandbox boolean."""
    from core.platform_utils import should_disable_browser_sandbox

    if sandbox is None:
        return not should_disable_browser_sandbox()

    if isinstance(sandbox, dict):
        if "no_sandbox" in sandbox:
            return not bool(sandbox["no_sandbox"])
        if "enabled" in sandbox:
            return bool(sandbox["enabled"])
        if "sandbox" in sandbox:
            return bool(sandbox["sandbox"])
        return True

    if isinstance(sandbox, str):
        value = sandbox.strip().lower()
        if value in ("false", "0", "no", "off", "disabled", "no-sandbox", "no_sandbox"):
            return False
        return value in ("true", "1", "yes", "on", "enabled", "sandbox")

    return bool(sandbox)


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]
    network_interceptor = deps["network_interceptor"]
    manual_login_handler = deps["manual_login_handler"]
    persistent_storage = deps["persistent_storage"]

    @section_tool("browser-management")
    async def spawn_browser(
        headless: bool = False,
        user_agent: Optional[str] = None,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        proxy: Optional[str] = None,
        block_resources: List[str] = None,
        extra_headers: Dict[str, str] = None,
        user_data_dir: Optional[str] = None,
        sandbox: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Spawn a new browser instance.

        Args:
            headless (bool): Run in headless mode.
            user_agent (Optional[str]): Custom user agent string.
            viewport_width (int): Viewport width in pixels.
            viewport_height (int): Viewport height in pixels.
            proxy (Optional[str]): Proxy server URL.
            block_resources (List[str]): List of resource types to block.
            extra_headers (Dict[str, str]): Additional HTTP headers.
            user_data_dir (Optional[str]): Path to user data directory for persistent sessions.
            sandbox (Optional[Any]): Enable browser sandbox.

        Returns:
            Dict[str, Any]: Instance information including instance_id.
        """
        try:
            sandbox = normalize_sandbox_option(sandbox)

            options = BrowserOptions(
                headless=headless,
                user_agent=user_agent,
                viewport_width=viewport_width,
                viewport_height=viewport_height,
                proxy=proxy,
                block_resources=block_resources or [],
                extra_headers=extra_headers or {},
                user_data_dir=user_data_dir,
                sandbox=sandbox,
            )
            instance = await browser_manager.spawn_browser(options)
            tab = await browser_manager.get_tab(instance.instance_id)
            if tab:
                await network_interceptor.setup_interception(
                    tab, instance.instance_id, block_resources
                )
            return {
                "instance_id": instance.instance_id,
                "state": instance.state,
                "headless": instance.headless,
                "viewport": instance.viewport,
            }
        except Exception as e:
            raise Exception(f"Failed to spawn browser: {str(e)}")

    @section_tool("browser-management")
    async def list_instances() -> List[Dict[str, Any]]:
        """
        List all active browser instances.

        Returns:
            List[Dict[str, Any]]: List of browser instances with their current state.
        """
        memory_instances = await browser_manager.list_instances()
        storage_instances = persistent_storage.list_instances()
        result = []
        for inst in memory_instances:
            result.append(
                {
                    "instance_id": inst.instance_id,
                    "state": inst.state,
                    "current_url": inst.current_url,
                    "title": inst.title,
                    "source": "active",
                }
            )
        memory_ids = {inst.instance_id for inst in memory_instances}
        for instance_id, inst_data in storage_instances.get("instances", {}).items():
            if instance_id not in memory_ids:
                result.append(
                    {
                        "instance_id": inst_data["instance_id"],
                        "state": inst_data["state"] + " (stored)",
                        "current_url": inst_data["current_url"],
                        "title": inst_data["title"],
                        "source": "stored",
                    }
                )
        return result

    @section_tool("browser-management")
    async def close_instance(instance_id: str) -> bool:
        """
        Close a browser instance.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            bool: True if closed successfully.
        """
        success = await browser_manager.close_instance(instance_id)
        if success:
            await network_interceptor.clear_instance_data(instance_id)
        return success

    @section_tool("browser-management")
    async def get_instance_state(instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed state of a browser instance.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Optional[Dict[str, Any]]: Complete state information.
        """
        state = await browser_manager.get_page_state(instance_id)
        if state:
            return state.model_dump(mode="json")
        return None

    @section_tool("browser-management")
    async def check_instance_health(instance_id: str) -> Dict[str, Any]:
        """
        Check if browser instance is healthy and WebSocket connection is alive.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Dict[str, Any]: Health status with 'healthy', 'reason', and 'can_recover'.
        """
        return await browser_manager.check_instance_health(instance_id)

    @section_tool("browser-management")
    async def navigate(
        instance_id: str,
        url: str,
        wait_until: str = "load",
        timeout: int = 30000,
        referrer: Optional[str] = None,
        inject_cookies: bool = True,
        cookies_file: str = "cookies.txt",
    ) -> Dict[str, Any]:
        """
        Navigate to a URL.

        Args:
            instance_id (str): Browser instance ID.
            url (str): URL to navigate to.
            wait_until (str): Wait condition - 'load', 'domcontentloaded', or 'networkidle'.
            timeout (int): Navigation timeout in milliseconds.
            referrer (Optional[str]): Referrer URL.
            inject_cookies (bool): If True, inject cookies from cookies_file.
            cookies_file (str): Path to cookies file in Netscape cookies.txt format.

        Returns:
            Dict[str, Any]: Navigation result with final URL, title, and cookie injection status.

        MANDATORY BEHAVIOR when response contains login_required=true:
            You MUST immediately STOP and send a message asking the user to log in manually.
            You MUST WAIT for the user to reply confirming they finished logging in.
            You MUST then call 'confirm_manual_login' with the SAME instance_id.
        """
        if isinstance(timeout, str):
            timeout = int(timeout)
        import nodriver as uc

        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        try:
            cookie_injection = {
                "attempted": False,
                "reason": "disabled",
                "file_path": cookies_file,
                "cookies_injected": 0,
            }

            if referrer:
                await tab.send(
                    uc.cdp.network.set_extra_http_headers(
                        headers=uc.cdp.network.Headers({"Referer": referrer})
                    )
                )

            pre_injected = False
            if inject_cookies:
                cookie_injection = await inject_cookies_from_file(
                    tab, url, network_interceptor, cookies_file
                )
                pre_injected = cookie_injection.get("cookies_injected", 0) > 0

            await tab.get(url)
            if wait_until == "networkidle":
                await asyncio.sleep(2)
            # For 'load' and 'domcontentloaded', tab.get() already handles navigation
            # tab.wait() can block indefinitely on some pages, so we skip it

            if inject_cookies and not pre_injected:
                wait_result = await wait_for_target_host(
                    tab,
                    url,
                    max_wait_ms=max(1000, min(timeout, 15000)),
                )
                if wait_result.get("matched"):
                    cookie_injection = await inject_cookies_from_file(
                        tab, url, network_interceptor, cookies_file
                    )
                    cookie_injection["target_wait"] = wait_result

                    if cookie_injection.get("cookies_injected", 0) > 0:
                        await tab.reload()
                        if wait_until == "networkidle":
                            await asyncio.sleep(2)
                else:
                    cookie_injection = {
                        "attempted": False,
                        "reason": "target_url_not_reached",
                        "file_path": cookies_file,
                        "cookies_injected": 0,
                        "target_wait": wait_result,
                    }

            final_url = await tab.evaluate("window.location.href")
            title = await tab.evaluate("document.title")
            await browser_manager.update_instance_state(instance_id, final_url, title)

            is_login_page = await manual_login_handler.detect_login_page(tab)

            if is_login_page:
                await manual_login_handler.register_pending_login(
                    instance_id=instance_id,
                    tab=tab,
                    url=final_url,
                )
                pending_info = await manual_login_handler.get_pending_info(instance_id) or {}
                manual_login_url = pending_info.get("manual_login_url")
                login_location = (
                    f"Open this remote browser URL so the user can log in: {manual_login_url}. "
                    if manual_login_url
                    else "A login page was detected. The browser window is OPEN and VISIBLE to the user. "
                )
                return {
                    "url": final_url,
                    "title": title,
                    "success": True,
                    "cookie_injection": cookie_injection,
                    "login_required": True,
                    "instance_id": instance_id,
                    "action_required": "STOP_AND_WAIT_FOR_USER",
                    "manual_login_url": manual_login_url,
                    "remote_browser_access": pending_info.get("remote_browser_access"),
                    "next_step": f"Ask user to log in manually, WAIT for their reply, then call confirm_manual_login(instance_id='{instance_id}')",
                    "message": (
                        "STOP — MANUAL LOGIN REQUIRED. "
                        f"{login_location}"
                        "You MUST follow this EXACT protocol: "
                        "(1) Send the manual login location to the user and ask them to finish login. "
                        "(2) STOP and WAIT for the user to reply confirming they logged in. "
                        "DO NOT take any other action until the user responds. "
                        f"(3) After user confirms, call confirm_manual_login(instance_id='{instance_id}'). "
                        "PROHIBITED: opening new browser, closing this browser, filling login forms, "
                        "trying alternative URLs, or concluding this task is impossible. "
                        "The user WILL log in manually. Your ONLY job is to WAIT."
                    ),
                }

            return {
                "url": final_url,
                "title": title,
                "success": True,
                "cookie_injection": cookie_injection,
                "login_required": False,
            }
        except Exception:
            raise

    @section_tool("browser-management")
    async def confirm_manual_login(instance_id: str) -> Dict[str, Any]:
        """
        Confirm that the user completed manual login and recover the browser instance.

        Args:
            instance_id (str): The instance_id from navigate's login_required response.

        Returns:
            Dict: success=true + current_url means instance is ready to use.
        """
        from core.login_watcher import login_watcher

        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(
                f"Instância não encontrada: {instance_id}. Verifique com list_instances."
            )

        watcher_detected = await login_watcher.consume_detected(instance_id)

        result = await manual_login_handler.confirm_login(
            instance_id=instance_id,
            tab=tab,
            skip_login_check=watcher_detected,
        )

        if result.get("success"):
            await login_watcher.stop_watching(instance_id)
            current_url = result.get("current_url", "")
            if current_url and current_url != "unknown":
                try:
                    title = await asyncio.wait_for(tab.evaluate("document.title"), timeout=3.0)
                except Exception:
                    title = "Browser Instance"
                await browser_manager.update_instance_state(instance_id, current_url, title)
        else:
            is_still_pending = await manual_login_handler.is_pending_login(instance_id)
            if is_still_pending:
                await login_watcher.start_watching(instance_id, tab)

        return result

    @section_tool("browser-management")
    async def check_login_status(instance_id: str) -> Dict[str, Any]:
        """
        Check if the user has completed login on an open browser instance.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Dict[str, Any]: Login status information.
        """
        from core.login_watcher import login_watcher

        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instância não encontrada: {instance_id}")

        is_pending = await manual_login_handler.is_pending_login(instance_id)
        is_detected = await login_watcher.is_login_detected(instance_id)

        try:
            current_url = await asyncio.wait_for(tab.evaluate("window.location.href"), timeout=3.0)
        except Exception:
            current_url = "unknown"

        if is_detected:
            return {
                "instance_id": instance_id,
                "current_url": current_url,
                "is_login_page": False,
                "is_authenticated": True,
                "pending_manual_login": is_pending,
                "message": "Login detectado pelo watcher. Chame confirm_manual_login para continuar.",
            }

        if not is_pending:
            return {
                "instance_id": instance_id,
                "current_url": current_url,
                "is_login_page": False,
                "is_authenticated": True,
                "pending_manual_login": False,
                "message": "Instância pronta.",
            }

        pending_info = await manual_login_handler.get_pending_info(instance_id) or {}
        return {
            "instance_id": instance_id,
            "current_url": current_url,
            "is_login_page": True,
            "is_authenticated": False,
            "pending_manual_login": True,
            "manual_login_url": pending_info.get("manual_login_url"),
            "remote_browser_access": pending_info.get("remote_browser_access"),
            "message": "Aguardando login manual. O watcher detectará automaticamente quando o usuário fizer login.",
        }

    @section_tool("browser-management")
    async def go_back(instance_id: str) -> bool:
        """Navigate back in history."""
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        await tab.back()
        return True

    @section_tool("browser-management")
    async def go_forward(instance_id: str) -> bool:
        """Navigate forward in history."""
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        await tab.forward()
        return True

    @section_tool("browser-management")
    async def reload_page(instance_id: str, ignore_cache: bool = False) -> bool:
        """Reload the current page."""
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        await tab.reload()
        return True

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
