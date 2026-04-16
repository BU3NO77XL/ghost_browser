"""Target management MCP tools for managing browser targets (pages, workers, iframes) via CDP."""

from typing import Dict, List, Optional

from core.login_guard import check_pending_login_guard
from core.target_handler import TargetHandler


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("target-management")
    async def target_get_targets(instance_id: str) -> List[Dict]:
        """
        Get all browser targets (pages, workers, iframes), excluding browser-type targets.

        Args:
            instance_id: Browser instance ID.

        Returns:
            List of dicts with target_id, type, title, url, attached, opener_id.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await TargetHandler.get_targets(tab)

    @section_tool("target-management")
    async def target_get_target_info(instance_id: str, target_id: str) -> Dict:
        """
        Get info for a specific browser target.

        Args:
            instance_id: Browser instance ID.
            target_id: The target ID to query.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await TargetHandler.get_target_info(tab, target_id)

    @section_tool("target-management")
    async def target_create_target(
        instance_id: str,
        url: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        new_window: bool = False,
    ) -> Dict:
        """
        Create a new browser target (tab/window).

        Args:
            instance_id: Browser instance ID.
            url: URL to open in the new target.
            width: Optional viewport width.
            height: Optional viewport height.
            new_window: Whether to open in a new window. Defaults to False.

        Returns:
            Dict with 'target_id' (str).
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await TargetHandler.create_target(tab, url, width, height, new_window)

    @section_tool("target-management")
    async def target_close_target(instance_id: str, target_id: str) -> Dict:
        """
        Close a browser target.

        Args:
            instance_id: Browser instance ID.
            target_id: The target ID to close.

        Returns:
            Dict with 'success' (bool).
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await TargetHandler.close_target(tab, target_id)

    @section_tool("target-management")
    async def target_activate_target(instance_id: str, target_id: str) -> bool:
        """
        Activate (focus) a browser target.

        Args:
            instance_id: Browser instance ID.
            target_id: The target ID to activate.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await TargetHandler.activate_target(tab, target_id)

    @section_tool("target-management")
    async def target_attach_to_target(
        instance_id: str,
        target_id: str,
        flatten: bool = True,
    ) -> Dict:
        """
        Attach to a browser target to create a debugging session.

        Args:
            instance_id: Browser instance ID.
            target_id: The target ID to attach to.
            flatten: Whether to use flat session protocol. Defaults to True.

        Returns:
            Dict with 'session_id' (str).
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await TargetHandler.attach_to_target(tab, target_id, flatten)

    @section_tool("target-management")
    async def target_detach_from_target(instance_id: str, session_id: str) -> bool:
        """
        Detach from a browser target session.

        Args:
            instance_id: Browser instance ID.
            session_id: The session ID to detach from.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await TargetHandler.detach_from_target(tab, session_id)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
