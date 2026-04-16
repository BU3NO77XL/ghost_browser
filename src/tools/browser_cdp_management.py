"""Browser CDP management MCP tools for window management, permissions, and downloads via CDP."""

from typing import Dict, List, Optional

from core.browser_cdp_handler import BrowserCDPHandler
from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("browser-cdp-management")
    async def browser_get_window_for_target(instance_id: str) -> Dict:
        """
        Get the browser window ID and bounds for the current target.

        Args:
            instance_id: Browser instance ID.

        Returns:
            Dict with 'window_id' (int) and 'bounds' (dict with left, top, width, height, window_state).
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await BrowserCDPHandler.get_window_for_target(tab)

    @section_tool("browser-cdp-management")
    async def browser_set_window_bounds(
        instance_id: str,
        window_id: int,
        bounds: Dict,
    ) -> bool:
        """
        Set the bounds (position/size/state) of a browser window.

        Args:
            instance_id: Browser instance ID.
            window_id: The window ID to update.
            bounds: Dict with optional keys: left, top, width, height, window_state
                    (window_state values: 'normal', 'minimized', 'maximized', 'fullscreen').
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await BrowserCDPHandler.set_window_bounds(tab, window_id, bounds)

    @section_tool("browser-cdp-management")
    async def browser_get_window_bounds(instance_id: str, window_id: int) -> Dict:
        """
        Get the bounds of a browser window.

        Args:
            instance_id: Browser instance ID.
            window_id: The window ID to query.

        Returns:
            Dict with left, top, width, height, window_state.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await BrowserCDPHandler.get_window_bounds(tab, window_id)

    @section_tool("browser-cdp-management")
    async def browser_grant_permissions(
        instance_id: str,
        permissions: List[str],
        origin: Optional[str] = None,
    ) -> bool:
        """
        Grant browser permissions for an origin.

        Args:
            instance_id: Browser instance ID.
            permissions: List of permission names (e.g. ['geolocation', 'notifications']).
            origin: Optional origin to grant permissions for (e.g. 'https://example.com').
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await BrowserCDPHandler.grant_permissions(tab, permissions, origin)

    @section_tool("browser-cdp-management")
    async def browser_reset_permissions(
        instance_id: str,
        origin: Optional[str] = None,
    ) -> bool:
        """
        Reset all browser permissions, optionally for a specific origin.

        Args:
            instance_id: Browser instance ID.
            origin: Optional origin to reset permissions for. If None, resets all.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await BrowserCDPHandler.reset_permissions(tab, origin)

    @section_tool("browser-cdp-management")
    async def browser_set_download_behavior(
        instance_id: str,
        behavior: str,
        download_path: Optional[str] = None,
    ) -> bool:
        """
        Set the download behavior for the browser.

        Args:
            instance_id: Browser instance ID.
            behavior: One of 'deny', 'allow', 'allowAndName', 'default'.
                      'allow' and 'allowAndName' require download_path.
            download_path: Directory path for downloads (required when behavior is 'allow' or 'allowAndName').
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await BrowserCDPHandler.set_download_behavior(tab, behavior, download_path)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
