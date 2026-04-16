"""Browser CDP domain handler for window management, permissions, and downloads via CDP."""

import asyncio
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.debug_logger import debug_logger


class BrowserCDPHandler:
    """Handles browser-level operations via CDP Browser domain."""

    @staticmethod
    async def get_window_for_target(tab: Tab) -> Dict[str, Any]:
        debug_logger.log_info(
            "BrowserCDPHandler", "get_window_for_target", "Getting window for target"
        )
        try:
            window_id, bounds = await tab.send(cdp.browser.get_window_for_target())
            return {
                "window_id": int(window_id),
                "bounds": {
                    "left": getattr(bounds, "left", None),
                    "top": getattr(bounds, "top", None),
                    "width": getattr(bounds, "width", None),
                    "height": getattr(bounds, "height", None),
                    "window_state": getattr(bounds, "window_state", None),
                },
            }
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("BrowserCDPHandler", "get_window_for_target", e, {})
            raise

    @staticmethod
    async def set_window_bounds(
        tab: Tab, window_id: int, bounds: Dict[str, Any]
    ) -> bool:
        debug_logger.log_info(
            "BrowserCDPHandler",
            "set_window_bounds",
            f"Setting bounds for window {window_id}",
        )
        try:
            cdp_bounds = cdp.browser.Bounds(
                left=bounds.get("left"),
                top=bounds.get("top"),
                width=bounds.get("width"),
                height=bounds.get("height"),
                window_state=cdp.browser.WindowState(bounds["window_state"])
                if bounds.get("window_state")
                else None,
            )
            await tab.send(
                cdp.browser.set_window_bounds(
                    window_id=cdp.browser.WindowID(window_id),
                    bounds=cdp_bounds,
                )
            )
            return True
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "BrowserCDPHandler",
                "set_window_bounds",
                e,
                {"window_id": window_id},
            )
            raise

    @staticmethod
    async def get_window_bounds(tab: Tab, window_id: int) -> Dict[str, Any]:
        debug_logger.log_info(
            "BrowserCDPHandler",
            "get_window_bounds",
            f"Getting bounds for window {window_id}",
        )
        try:
            bounds = await tab.send(
                cdp.browser.get_window_bounds(
                    window_id=cdp.browser.WindowID(window_id)
                )
            )
            return {
                "left": getattr(bounds, "left", None),
                "top": getattr(bounds, "top", None),
                "width": getattr(bounds, "width", None),
                "height": getattr(bounds, "height", None),
                "window_state": getattr(bounds, "window_state", None),
            }
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "BrowserCDPHandler",
                "get_window_bounds",
                e,
                {"window_id": window_id},
            )
            raise

    @staticmethod
    async def grant_permissions(
        tab: Tab,
        permissions: List[str],
        origin: Optional[str] = None,
    ) -> bool:
        debug_logger.log_info(
            "BrowserCDPHandler",
            "grant_permissions",
            f"Granting permissions: {permissions}",
        )
        try:
            cdp_permissions = [cdp.browser.PermissionType(p) for p in permissions]
            await tab.send(
                cdp.browser.grant_permissions(
                    permissions=cdp_permissions,
                    origin=origin,
                )
            )
            return True
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "BrowserCDPHandler",
                "grant_permissions",
                e,
                {"permissions": permissions},
            )
            raise

    @staticmethod
    async def reset_permissions(tab: Tab, origin: Optional[str] = None) -> bool:
        debug_logger.log_info(
            "BrowserCDPHandler", "reset_permissions", "Resetting permissions"
        )
        try:
            # Note: cdp.browser.reset_permissions() doesn't accept origin parameter
            await tab.send(cdp.browser.reset_permissions())
            return True
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("BrowserCDPHandler", "reset_permissions", e, {})
            raise

    @staticmethod
    async def set_download_behavior(
        tab: Tab,
        behavior: str,
        download_path: Optional[str] = None,
    ) -> bool:
        debug_logger.log_info(
            "BrowserCDPHandler",
            "set_download_behavior",
            f"Setting download behavior to '{behavior}'",
        )
        if behavior in ("allow", "allowAndName") and not download_path:
            raise ValueError(
                "download_path is required when behavior is 'allow' or 'allowAndName'"
            )
        try:
            await tab.send(
                cdp.browser.set_download_behavior(
                    behavior=behavior,  # Pass string directly instead of enum
                    download_path=download_path,
                )
            )
            return True
        except ValueError:
            raise
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "BrowserCDPHandler",
                "set_download_behavior",
                e,
                {"behavior": behavior},
            )
            raise
