"""Overlay management MCP tools for visual highlighting and overlay controls via CDP."""

from typing import Dict, List, Optional

from core.login_guard import check_pending_login_guard
from core.overlay_handler import OverlayHandler


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("overlay-management")
    async def overlay_enable(instance_id: str) -> bool:
        """
        Enable the Overlay domain for a browser instance.

        Must be called before overlay operations such as node highlighting are
        used. Activates the CDP Overlay domain on the connected tab.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await OverlayHandler.enable_overlay(tab)

    @section_tool("overlay-management")
    async def overlay_disable(instance_id: str) -> bool:
        """
        Disable the Overlay domain for a browser instance.

        Deactivates the CDP Overlay domain, stopping any active overlays.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await OverlayHandler.disable_overlay(tab)

    @section_tool("overlay-management")
    async def overlay_highlight_node(
        instance_id: str,
        highlight_config: Dict,
        node_id: Optional[int] = None,
        backend_node_id: Optional[int] = None,
    ) -> bool:
        """
        Highlight a DOM node with the given highlight configuration.

        Either node_id or backend_node_id must be provided (not both). The
        highlight_config dict is converted to a CDP HighlightConfig object.

        Example:
            overlay_highlight_node("abc123", {"show_info": True}, node_id=42)

        Args:
            instance_id (str): Browser instance ID.
            highlight_config (Dict): Highlight configuration. Supported keys
                include ``show_info`` (bool), ``show_styles`` (bool),
                ``show_rulers`` (bool), ``show_extension_lines`` (bool),
                ``content_color`` (dict), ``padding_color`` (dict),
                ``border_color`` (dict), ``margin_color`` (dict).
            node_id (Optional[int]): The DOM node ID to highlight.
            backend_node_id (Optional[int]): The backend node ID to highlight.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await OverlayHandler.highlight_node(
            tab,
            highlight_config=highlight_config,
            node_id=node_id,
            backend_node_id=backend_node_id,
        )

    @section_tool("overlay-management")
    async def overlay_hide_highlight(instance_id: str) -> bool:
        """
        Hide any active highlight on a browser instance.

        Removes any currently displayed node or rect highlight from the page.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await OverlayHandler.hide_highlight(tab)

    @section_tool("overlay-management")
    async def overlay_highlight_rect(
        instance_id: str,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> bool:
        """
        Highlight a rectangular area on the page.

        Draws a highlight overlay over the specified rectangle in page
        coordinates.

        Args:
            instance_id (str): Browser instance ID.
            x (int): X coordinate of the top-left corner of the rectangle.
            y (int): Y coordinate of the top-left corner of the rectangle.
            width (int): Width of the rectangle in pixels.
            height (int): Height of the rectangle in pixels.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await OverlayHandler.highlight_rect(tab, x=x, y=y, width=width, height=height)

    @section_tool("overlay-management")
    async def overlay_set_show_grid_overlays(
        instance_id: str,
        configs: List[Dict],
    ) -> bool:
        """
        Show CSS grid overlays for the specified nodes.

        Each config dict must contain a ``node_id`` key (int) and may
        optionally contain a ``grid_highlight_config`` key (dict) with
        grid-specific highlight settings.

        Example:
            overlay_set_show_grid_overlays("abc123", [
                {"node_id": 42, "grid_highlight_config": {"show_grid_extension_lines": True}}
            ])

        Args:
            instance_id (str): Browser instance ID.
            configs (List[Dict]): List of grid highlight config dicts. Each
                dict must have a ``node_id`` key and optionally a
                ``grid_highlight_config`` key.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await OverlayHandler.set_show_grid_overlays(tab, configs=configs)

    @section_tool("overlay-management")
    async def overlay_set_show_flex_overlays(
        instance_id: str,
        configs: List[Dict],
    ) -> bool:
        """
        Show CSS flexbox overlays for the specified nodes.

        Each config dict must contain a ``node_id`` key (int) and may
        optionally contain a ``flex_container_highlight_config`` key (dict)
        with flex-specific highlight settings.

        Example:
            overlay_set_show_flex_overlays("abc123", [
                {"node_id": 7, "flex_container_highlight_config": {}}
            ])

        Args:
            instance_id (str): Browser instance ID.
            configs (List[Dict]): List of flex highlight config dicts. Each
                dict must have a ``node_id`` key and optionally a
                ``flex_container_highlight_config`` key.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await OverlayHandler.set_show_flex_overlays(tab, configs=configs)

    @section_tool("overlay-management")
    async def overlay_set_show_scroll_snap_overlays(
        instance_id: str,
        configs: List[Dict],
    ) -> bool:
        """
        Show scroll snap overlays for the specified nodes.

        Each config dict must contain a ``node_id`` key (int) and may
        optionally contain a ``scroll_snap_container_highlight_config`` key
        (dict) with scroll-snap-specific highlight settings.

        Example:
            overlay_set_show_scroll_snap_overlays("abc123", [
                {"node_id": 15, "scroll_snap_container_highlight_config": {}}
            ])

        Args:
            instance_id (str): Browser instance ID.
            configs (List[Dict]): List of scroll snap highlight config dicts.
                Each dict must have a ``node_id`` key and optionally a
                ``scroll_snap_container_highlight_config`` key.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await OverlayHandler.set_show_scroll_snap_overlays(tab, configs=configs)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
