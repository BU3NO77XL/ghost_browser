"""CSS management MCP tools for style retrieval and manipulation."""

from typing import Any, Dict, List

from core.css_handler import CSSHandler
from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("css-management")
    async def get_matched_styles(instance_id: str, selector: str) -> Dict[str, Any]:
        """
        Get all matched CSS styles for an element.

        Example:
            get_matched_styles("abc123", "h1.title")
            # Returns matched rules and inline styles for the element

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the target element.

        Returns:
            Dict[str, Any]: Matched rules and inline styles.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await CSSHandler.get_matched_styles(tab, selector)

    @section_tool("css-management")
    async def get_inline_styles(instance_id: str, selector: str) -> Dict[str, str]:
        """
        Get inline CSS styles for an element.

        Example:
            get_inline_styles("abc123", "#my-div")
            # Returns {"color": "red", "font-size": "16px"}

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the target element.

        Returns:
            Dict[str, str]: Inline style properties as key-value pairs.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await CSSHandler.get_inline_styles(tab, selector)

    @section_tool("css-management")
    async def get_computed_style(instance_id: str, selector: str) -> Dict[str, str]:
        """
        Get computed CSS styles for an element (all resolved values).

        Example:
            get_computed_style("abc123", "body")
            # Returns all computed CSS properties for the body element

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the target element.

        Returns:
            Dict[str, str]: Computed style properties as key-value pairs.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await CSSHandler.get_computed_style(tab, selector)

    @section_tool("css-management")
    async def get_stylesheet_text(instance_id: str, stylesheet_id: str) -> str:
        """
        Get the full text content of a stylesheet by its ID.

        Example:
            get_stylesheet_text("abc123", "1")
            # Returns the raw CSS text of the stylesheet

        Args:
            instance_id (str): Browser instance ID.
            stylesheet_id (str): The stylesheet ID (obtained from CDP or browser devtools).

        Returns:
            str: The stylesheet text content.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await CSSHandler.get_stylesheet_text(tab, stylesheet_id)

    @section_tool("css-management")
    async def set_stylesheet_text(instance_id: str, stylesheet_id: str, text: str) -> bool:
        """
        Replace the full text content of a stylesheet.

        Example:
            set_stylesheet_text("abc123", "1", "body { background: blue; }")
            # Replaces the stylesheet content

        Args:
            instance_id (str): Browser instance ID.
            stylesheet_id (str): The stylesheet ID to modify.
            text (str): The new CSS text to set.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await CSSHandler.set_stylesheet_text(tab, stylesheet_id, text)

    @section_tool("css-management")
    async def get_media_queries(instance_id: str) -> List[Dict[str, Any]]:
        """
        Get all media queries from the page's stylesheets.

        Example:
            get_media_queries("abc123")
            # Returns list of media queries like @media (max-width: 768px)

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            List[Dict[str, Any]]: List of media query objects with text and expressions.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await CSSHandler.get_media_queries(tab)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
