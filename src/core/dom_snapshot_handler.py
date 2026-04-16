"""DOMSnapshot domain handler for capturing full DOM snapshots with computed styles via CDP."""

import asyncio
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.debug_logger import debug_logger

DEFAULT_COMPUTED_STYLES = [
    "display",
    "visibility",
    "color",
    "background-color",
    "font-size",
    "font-family",
    "width",
    "height",
    "position",
    "z-index",
]


class DOMSnapshotHandler:
    """Handles DOM snapshot operations via CDP DOMSnapshot domain."""

    @staticmethod
    async def enable_dom_snapshot(tab: Tab) -> bool:
        debug_logger.log_info(
            "DOMSnapshotHandler", "enable_dom_snapshot", "Enabling DOMSnapshot domain"
        )
        try:
            await tab.send(cdp.dom_snapshot.enable())
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
            debug_logger.log_error("DOMSnapshotHandler", "enable_dom_snapshot", e, {})
            raise

    @staticmethod
    async def disable_dom_snapshot(tab: Tab) -> bool:
        debug_logger.log_info(
            "DOMSnapshotHandler", "disable_dom_snapshot", "Disabling DOMSnapshot domain"
        )
        try:
            await tab.send(cdp.dom_snapshot.disable())
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
            debug_logger.log_error("DOMSnapshotHandler", "disable_dom_snapshot", e, {})
            raise

    @staticmethod
    async def capture_snapshot(
        tab: Tab,
        computed_styles: Optional[List[str]] = None,
        include_dom_rects: bool = False,
        include_blended_background_colors: bool = False,
    ) -> Dict[str, Any]:
        debug_logger.log_info(
            "DOMSnapshotHandler", "capture_snapshot", "Capturing DOM snapshot"
        )
        # Apply default computed styles when empty or None
        if not computed_styles:
            computed_styles = DEFAULT_COMPUTED_STYLES

        try:
            result = await tab.send(
                cdp.dom_snapshot.capture_snapshot(
                    computed_styles=computed_styles,
                    include_dom_rects=include_dom_rects,
                    include_blended_background_colors=include_blended_background_colors,
                )
            )
            documents = getattr(result, "documents", [])
            strings = getattr(result, "strings", [])

            # Compute node_count from first document
            node_count = 0
            if documents:
                first_doc = documents[0]
                nodes = getattr(first_doc, "nodes", None)
                if nodes is not None:
                    node_type = getattr(nodes, "node_type", [])
                    node_count = len(node_type) if node_type else 0

            return {
                "documents": documents,
                "strings": strings,
                "node_count": node_count,
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
            debug_logger.log_error("DOMSnapshotHandler", "capture_snapshot", e, {})
            raise
