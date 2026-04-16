"""DOM snapshot management MCP tools for capturing full DOM snapshots with computed styles via CDP."""

from typing import List, Optional

from core.dom_snapshot_handler import DOMSnapshotHandler
from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("dom-snapshot-management")
    async def dom_snapshot_enable(instance_id: str) -> bool:
        """Enable the DOMSnapshot domain for a browser instance."""
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DOMSnapshotHandler.enable_dom_snapshot(tab)

    @section_tool("dom-snapshot-management")
    async def dom_snapshot_disable(instance_id: str) -> bool:
        """Disable the DOMSnapshot domain for a browser instance."""
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DOMSnapshotHandler.disable_dom_snapshot(tab)

    @section_tool("dom-snapshot-management")
    async def dom_snapshot_capture(
        instance_id: str,
        computed_styles: Optional[List[str]] = None,
        include_dom_rects: bool = False,
        include_blended_background_colors: bool = False,
    ) -> dict:
        """
        Capture a full DOM snapshot of the current page including computed styles.

        Args:
            instance_id: Browser instance ID.
            computed_styles: List of CSS property names to include in the snapshot.
                             Defaults to ['display', 'visibility', 'color', 'background-color',
                             'font-size', 'font-family', 'width', 'height', 'position', 'z-index'].
            include_dom_rects: Whether to include DOM rect data. Defaults to False.
            include_blended_background_colors: Whether to include blended background colors. Defaults to False.

        Returns:
            Dict with 'documents', 'strings', and 'node_count' fields.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DOMSnapshotHandler.capture_snapshot(
            tab,
            computed_styles=computed_styles,
            include_dom_rects=include_dom_rects,
            include_blended_background_colors=include_blended_background_colors,
        )

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
