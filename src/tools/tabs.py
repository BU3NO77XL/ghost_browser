"""Tab management tools."""

from typing import Any, Dict, List

from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("tabs")
    async def list_tabs(instance_id: str) -> List[Dict[str, str]]:
        """
        List all tabs for a browser instance.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            List[Dict[str, str]]: List of tabs with their details.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        return await browser_manager.list_tabs(instance_id)

    @section_tool("tabs")
    async def switch_tab(instance_id: str, tab_id: str) -> bool:
        """
        Switch to a specific tab by bringing it to front.

        Args:
            instance_id (str): Browser instance ID.
            tab_id (str): Target tab ID to switch to.

        Returns:
            bool: True if switched successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        return await browser_manager.switch_to_tab(instance_id, tab_id)

    @section_tool("tabs")
    async def close_tab(instance_id: str, tab_id: str) -> bool:
        """
        Close a specific tab.

        Args:
            instance_id (str): Browser instance ID.
            tab_id (str): Tab ID to close.

        Returns:
            bool: True if closed successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        return await browser_manager.close_tab(instance_id, tab_id)

    @section_tool("tabs")
    async def get_active_tab(instance_id: str) -> Dict[str, Any]:
        """
        Get information about the currently active tab.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Dict[str, Any]: Active tab information.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_active_tab(instance_id)
        if not tab:
            return {"error": "No active tab found"}
        return {
            "tab_id": str(tab.target.target_id),
            "url": getattr(tab, "url", "") or "",
            "title": getattr(tab.target, "title", "") or "Untitled",
            "type": getattr(tab.target, "type_", "page"),
        }

    @section_tool("tabs")
    async def new_tab(instance_id: str, url: str = "about:blank") -> Dict[str, Any]:
        """
        Open a new tab in the browser instance.

        Args:
            instance_id (str): Browser instance ID.
            url (str): URL to open in the new tab.

        Returns:
            Dict[str, Any]: New tab information.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        browser = await browser_manager.get_browser(instance_id)
        if not browser:
            raise Exception(f"Instance not found: {instance_id}")
        try:
            new_tab_obj = await browser.get(url, new_tab=True)
            await new_tab_obj
            return {
                "tab_id": str(new_tab_obj.target.target_id),
                "url": getattr(new_tab_obj, "url", "") or url,
                "title": getattr(new_tab_obj.target, "title", "") or "New Tab",
                "type": getattr(new_tab_obj.target, "type_", "page"),
            }
        except Exception as e:
            raise Exception(f"Failed to create new tab: {str(e)}")

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
