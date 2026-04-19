"""CSS domain handler for style retrieval and manipulation via CDP."""

import asyncio
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.debug_logger import debug_logger


class CSSHandler:
    """Handles CSS operations via CDP CSS domain."""

    @staticmethod
    async def enable_css_domain(tab: Tab) -> None:
        """
        Enable the CSS domain for the given tab.

        Args:
            tab (Tab): The browser tab object.
        """
        try:
            await tab.send(cdp.dom.enable())
            await tab.send(cdp.css.enable())
        except Exception as e:
            error_msg = str(e).lower()
            if "already enabled" in error_msg:
                return
            raise

    @staticmethod
    async def _get_node_id_from_selector(tab: Tab, selector: str) -> int:
        """
        Resolve a CSS selector to a CDP DOM nodeId.

        Args:
            tab (Tab): The browser tab object.
            selector (str): CSS selector string.

        Returns:
            int: The DOM nodeId.

        Raises:
            Exception: If the selector matches no element.
        """
        doc = await tab.send(cdp.dom.get_document())
        node_id = await tab.send(cdp.dom.query_selector(node_id=doc.node_id, selector=selector))
        if not node_id:
            raise Exception(f"No element found for selector: {selector}")
        return node_id

    @staticmethod
    async def get_matched_styles(tab: Tab, selector: str) -> Dict[str, Any]:
        """
        Get all matched CSS styles for an element.

        Args:
            tab (Tab): The browser tab object.
            selector (str): CSS selector for the target element.

        Returns:
            Dict[str, Any]: Matched styles including inline, attribute, and rule styles.
        """
        debug_logger.log_info(
            "CSSHandler", "get_matched_styles", f"Getting matched styles for: {selector}"
        )
        try:
            await CSSHandler.enable_css_domain(tab)
            node_id = await CSSHandler._get_node_id_from_selector(tab, selector)
            result = await tab.send(cdp.css.get_matched_styles_for_node(node_id=node_id))
            inline_style, _, matched_css_rules = (
                result[:3]
                if isinstance(result, (tuple, list))
                else (
                    getattr(result, "inline_style", None),
                    getattr(result, "attributes_style", None),
                    getattr(result, "matched_css_rules", None),
                )
            )
            matched = []
            if matched_css_rules:
                for rule_match in matched_css_rules:
                    rule = rule_match.rule
                    matched.append(
                        {
                            "selector": rule.selector_list.text if rule.selector_list else "",
                            "properties": [
                                {"name": p.name, "value": p.value, "important": p.important}
                                for p in (rule.style.css_properties if rule.style else [])
                            ],
                        }
                    )
            inline = {}
            if inline_style and inline_style.css_properties:
                inline = {p.name: p.value for p in inline_style.css_properties if p.value}
            return {"matched_rules": matched, "inline_style": inline}
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("CSSHandler", "get_matched_styles", e, {"selector": selector})
            raise

    @staticmethod
    async def get_inline_styles(tab: Tab, selector: str) -> Dict[str, str]:
        """
        Get inline CSS styles for an element.

        Args:
            tab (Tab): The browser tab object.
            selector (str): CSS selector for the target element.

        Returns:
            Dict[str, str]: Inline style properties as key-value pairs.
        """
        debug_logger.log_info(
            "CSSHandler", "get_inline_styles", f"Getting inline styles for: {selector}"
        )
        try:
            await CSSHandler.enable_css_domain(tab)
            node_id = await CSSHandler._get_node_id_from_selector(tab, selector)
            result = await tab.send(cdp.css.get_inline_styles_for_node(node_id=node_id))
            inline_style = (
                result[0] if isinstance(result, (tuple, list)) else getattr(result, "inline_style", None)
            )
            if not inline_style or not inline_style.css_properties:
                return {}
            return {p.name: p.value for p in inline_style.css_properties if p.value is not None}
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("CSSHandler", "get_inline_styles", e, {"selector": selector})
            raise

    @staticmethod
    async def get_computed_style(tab: Tab, selector: str) -> Dict[str, str]:
        """
        Get computed CSS styles for an element.

        Args:
            tab (Tab): The browser tab object.
            selector (str): CSS selector for the target element.

        Returns:
            Dict[str, str]: Computed style properties as key-value pairs.
        """
        debug_logger.log_info(
            "CSSHandler", "get_computed_style", f"Getting computed style for: {selector}"
        )
        try:
            await CSSHandler.enable_css_domain(tab)
            node_id = await CSSHandler._get_node_id_from_selector(tab, selector)
            result = await tab.send(cdp.css.get_computed_style_for_node(node_id=node_id))
            computed_style = (
                result[0]
                if isinstance(result, (tuple, list))
                else getattr(result, "computed_style", None)
            )
            if not computed_style:
                return {}
            return {p.name: p.value for p in computed_style}
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("CSSHandler", "get_computed_style", e, {"selector": selector})
            raise

    @staticmethod
    async def get_stylesheet_text(tab: Tab, stylesheet_id: str) -> str:
        """
        Get the text content of a stylesheet.

        Args:
            tab (Tab): The browser tab object.
            stylesheet_id (str): The stylesheet ID (from CDP).

        Returns:
            str: The stylesheet text content.
        """
        debug_logger.log_info(
            "CSSHandler", "get_stylesheet_text", f"Getting stylesheet: {stylesheet_id}"
        )
        try:
            await CSSHandler.enable_css_domain(tab)
            result = await tab.send(
                cdp.css.get_style_sheet_text(style_sheet_id=cdp.css.StyleSheetId(stylesheet_id))
            )
            return result if isinstance(result, str) else getattr(result, "text", None) or ""
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
                "CSSHandler", "get_stylesheet_text", e, {"stylesheet_id": stylesheet_id}
            )
            raise

    @staticmethod
    async def set_stylesheet_text(tab: Tab, stylesheet_id: str, text: str) -> bool:
        """
        Set the text content of a stylesheet.

        Args:
            tab (Tab): The browser tab object.
            stylesheet_id (str): The stylesheet ID (from CDP).
            text (str): The new stylesheet text.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "CSSHandler", "set_stylesheet_text", f"Setting stylesheet: {stylesheet_id}"
        )
        try:
            await CSSHandler.enable_css_domain(tab)
            await tab.send(
                cdp.css.set_style_sheet_text(
                    style_sheet_id=cdp.css.StyleSheetId(stylesheet_id),
                    text=text,
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
                "CSSHandler", "set_stylesheet_text", e, {"stylesheet_id": stylesheet_id}
            )
            raise

    @staticmethod
    async def get_media_queries(tab: Tab) -> List[Dict[str, Any]]:
        """
        Get all media queries from the page's stylesheets.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            List[Dict[str, Any]]: List of media query objects with text and expressions.
        """
        debug_logger.log_info("CSSHandler", "get_media_queries", "Getting all media queries")
        try:
            await CSSHandler.enable_css_domain(tab)
            result = await tab.send(cdp.css.get_media_queries())
            medias = []
            media_items = result if isinstance(result, list) else getattr(result, "medias", None) or []
            for media in media_items:
                expressions = []
                if media.media_list:
                    for query in media.media_list:
                        query_expressions = getattr(query, "expressions", None) or [query]
                        for expr in query_expressions:
                            expressions.append(
                                {
                                    "value": expr.value,
                                    "unit": expr.unit,
                                    "feature": expr.feature,
                                    "active": getattr(query, "active", None),
                                }
                            )
                medias.append(
                    {
                        "text": media.text,
                        "source": media.source,
                        "expressions": expressions,
                    }
                )
            return medias
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("CSSHandler", "get_media_queries", e, {})
            raise
