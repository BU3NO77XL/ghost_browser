"""Overlay domain handler for visual highlighting and overlay controls via CDP."""

import asyncio
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.debug_logger import debug_logger


class OverlayHandler:
    """Handles visual overlay operations via CDP Overlay domain."""

    @staticmethod
    async def enable_overlay(tab: Tab) -> bool:
        """
        Enable the Overlay domain.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info("OverlayHandler", "enable_overlay", "Enabling Overlay domain")
        try:
            await tab.send(cdp.overlay.enable())
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
            debug_logger.log_error("OverlayHandler", "enable_overlay", e, {})
            raise

    @staticmethod
    async def disable_overlay(tab: Tab) -> bool:
        """
        Disable the Overlay domain.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info("OverlayHandler", "disable_overlay", "Disabling Overlay domain")
        try:
            await tab.send(cdp.overlay.disable())
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
            debug_logger.log_error("OverlayHandler", "disable_overlay", e, {})
            raise

    @staticmethod
    async def highlight_node(
        tab: Tab,
        highlight_config: Dict[str, Any],
        node_id: Optional[int] = None,
        backend_node_id: Optional[int] = None,
    ) -> bool:
        """
        Highlight a DOM node with the given highlight configuration.

        Either node_id or backend_node_id must be provided (not both).

        Args:
            tab (Tab): The browser tab object.
            highlight_config (Dict[str, Any]): Highlight configuration dict.
            node_id (Optional[int]): The DOM node ID to highlight.
            backend_node_id (Optional[int]): The backend node ID to highlight.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "OverlayHandler",
            "highlight_node",
            f"Highlighting node (node_id={node_id}, backend_node_id={backend_node_id})",
        )
        try:
            cdp_highlight_config = cdp.overlay.HighlightConfig(**highlight_config)
            cdp_node_id = cdp.dom.NodeId(node_id) if node_id is not None else None
            cdp_backend_node_id = (
                cdp.dom.BackendNodeId(backend_node_id) if backend_node_id is not None else None
            )
            await tab.send(
                cdp.overlay.highlight_node(
                    highlight_config=cdp_highlight_config,
                    node_id=cdp_node_id,
                    backend_node_id=cdp_backend_node_id,
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
                "OverlayHandler",
                "highlight_node",
                e,
                {"node_id": node_id, "backend_node_id": backend_node_id},
            )
            raise

    @staticmethod
    async def hide_highlight(tab: Tab) -> bool:
        """
        Hide any active highlight.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info("OverlayHandler", "hide_highlight", "Hiding highlight")
        try:
            await tab.send(cdp.overlay.hide_highlight())
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
            debug_logger.log_error("OverlayHandler", "hide_highlight", e, {})
            raise

    @staticmethod
    async def highlight_rect(tab: Tab, x: int, y: int, width: int, height: int) -> bool:
        """
        Highlight a rectangular area on the page.

        Args:
            tab (Tab): The browser tab object.
            x (int): X coordinate of the rectangle.
            y (int): Y coordinate of the rectangle.
            width (int): Width of the rectangle.
            height (int): Height of the rectangle.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "OverlayHandler",
            "highlight_rect",
            f"Highlighting rect at ({x}, {y}) size {width}x{height}",
        )
        try:
            await tab.send(cdp.overlay.highlight_rect(x=x, y=y, width=width, height=height))
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
                "OverlayHandler",
                "highlight_rect",
                e,
                {"x": x, "y": y, "width": width, "height": height},
            )
            raise

    @staticmethod
    async def set_show_grid_overlays(tab: Tab, configs: List[Dict[str, Any]]) -> bool:
        """
        Show CSS grid overlays for the specified nodes.

        Args:
            tab (Tab): The browser tab object.
            configs (List[Dict[str, Any]]): List of grid highlight config dicts.
                Each dict must have a 'node_id' key and optionally a
                'grid_highlight_config' key.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "OverlayHandler",
            "set_show_grid_overlays",
            f"Setting grid overlays for {len(configs)} node(s)",
        )
        try:
            cdp_configs = []
            for config in configs:
                node_id = cdp.dom.NodeId(config["node_id"])
                grid_highlight_config = config.get("grid_highlight_config", {})
                cdp_configs.append(
                    cdp.overlay.GridNodeHighlightConfig(
                        node_id=node_id,
                        grid_highlight_config=cdp.overlay.GridHighlightConfig(
                            **grid_highlight_config
                        ),
                    )
                )
            await tab.send(
                cdp.overlay.set_show_grid_overlays(grid_node_highlight_configs=cdp_configs)
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
                "OverlayHandler", "set_show_grid_overlays", e, {"configs": configs}
            )
            raise

    @staticmethod
    async def set_show_flex_overlays(tab: Tab, configs: List[Dict[str, Any]]) -> bool:
        """
        Show CSS flexbox overlays for the specified nodes.

        Args:
            tab (Tab): The browser tab object.
            configs (List[Dict[str, Any]]): List of flex highlight config dicts.
                Each dict must have a 'node_id' key and optionally a
                'flex_container_highlight_config' key.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "OverlayHandler",
            "set_show_flex_overlays",
            f"Setting flex overlays for {len(configs)} node(s)",
        )
        try:
            cdp_configs = []
            for config in configs:
                node_id = cdp.dom.NodeId(config["node_id"])
                flex_highlight_config = config.get("flex_container_highlight_config", {})
                cdp_configs.append(
                    cdp.overlay.FlexNodeHighlightConfig(
                        node_id=node_id,
                        flex_container_highlight_config=cdp.overlay.FlexContainerHighlightConfig(
                            **flex_highlight_config
                        ),
                    )
                )
            await tab.send(
                cdp.overlay.set_show_flex_overlays(flex_node_highlight_configs=cdp_configs)
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
                "OverlayHandler", "set_show_flex_overlays", e, {"configs": configs}
            )
            raise

    @staticmethod
    async def set_show_scroll_snap_overlays(tab: Tab, configs: List[Dict[str, Any]]) -> bool:
        """
        Show scroll snap overlays for the specified nodes.

        Args:
            tab (Tab): The browser tab object.
            configs (List[Dict[str, Any]]): List of scroll snap highlight config dicts.
                Each dict must have a 'node_id' key and optionally a
                'scroll_snap_container_highlight_config' key.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "OverlayHandler",
            "set_show_scroll_snap_overlays",
            f"Setting scroll snap overlays for {len(configs)} node(s)",
        )
        try:
            cdp_configs = []
            for config in configs:
                node_id = cdp.dom.NodeId(config["node_id"])
                snap_highlight_config = config.get("scroll_snap_container_highlight_config", {})
                cdp_configs.append(
                    cdp.overlay.ScrollSnapHighlightConfig(
                        node_id=node_id,
                        scroll_snap_container_highlight_config=cdp.overlay.ScrollSnapContainerHighlightConfig(
                            **snap_highlight_config
                        ),
                    )
                )
            await tab.send(
                cdp.overlay.set_show_scroll_snap_overlays(scroll_snap_highlight_configs=cdp_configs)
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
                "OverlayHandler",
                "set_show_scroll_snap_overlays",
                e,
                {"configs": configs},
            )
            raise
