"""Progressive element cloning tools."""

from typing import Any, Dict, List, Optional

from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]
    progressive_element_cloner = deps["progressive_element_cloner"]
    response_handler = deps["response_handler"]

    @section_tool("progressive-cloning")
    async def clone_element_progressive(
        instance_id: str, selector: str, include_children: bool = True
    ) -> Dict[str, Any]:
        """
        Clone element progressively - returns lightweight base structure with element_id.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            include_children (bool): Whether to extract child elements.

        Returns:
            Dict[str, Any]: Base structure with element_id for progressive expansion.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await progressive_element_cloner.clone_element_progressive(
            tab, selector, include_children
        )

    @section_tool("progressive-cloning")
    async def expand_styles(
        element_id: str,
        categories: Optional[List[str]] = None,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Expand styles data for a stored element.

        Args:
            element_id (str): Element ID from clone_element_progressive().
            categories (Optional[List[str]]): Style categories to include.
            properties (Optional[List[str]]): Specific CSS property names to include.

        Returns:
            Dict[str, Any]: Filtered styles data.
        """
        return progressive_element_cloner.expand_styles(element_id, categories, properties)

    @section_tool("progressive-cloning")
    async def expand_events(
        element_id: str, event_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Expand event listeners data for a stored element.

        Args:
            element_id (str): Element ID from clone_element_progressive().
            event_types (Optional[List[str]]): Event types or sources to include.

        Returns:
            Dict[str, Any]: Filtered event listeners data.
        """
        return progressive_element_cloner.expand_events(element_id, event_types)

    @section_tool("progressive-cloning")
    async def expand_children(
        element_id: str,
        depth_range: Optional[List] = None,
        max_count: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Expand children data for a stored element.

        Args:
            element_id (str): Element ID from clone_element_progressive().
            depth_range (Optional[List]): [min_depth, max_depth] range to include.
            max_count (Optional[Any]): Maximum number of children to return.

        Returns:
            Dict[str, Any]: Filtered children data.
        """
        if isinstance(max_count, str):
            try:
                max_count = int(max_count) if max_count else None
            except ValueError:
                return {"error": f"Invalid max_count value: {max_count}"}

        if isinstance(depth_range, list):
            try:
                depth_range = [int(x) if isinstance(x, str) else x for x in depth_range]
            except ValueError:
                return {"error": f"Invalid depth_range values: {depth_range}"}

        depth_tuple = tuple(depth_range) if depth_range else None
        result = progressive_element_cloner.expand_children(element_id, depth_tuple, max_count)
        return response_handler.handle_response(result, f"expand_children_{element_id}")

    @section_tool("progressive-cloning")
    async def expand_css_rules(
        element_id: str, source_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Expand CSS rules data for a stored element.

        Args:
            element_id (str): Element ID from clone_element_progressive().
            source_types (Optional[List[str]]): CSS rule sources to include.

        Returns:
            Dict[str, Any]: Filtered CSS rules data.
        """
        return progressive_element_cloner.expand_css_rules(element_id, source_types)

    @section_tool("progressive-cloning")
    async def expand_pseudo_elements(element_id: str) -> Dict[str, Any]:
        """
        Expand pseudo-elements data for a stored element.

        Args:
            element_id (str): Element ID from clone_element_progressive().

        Returns:
            Dict[str, Any]: Pseudo-elements data (::before, ::after, etc.).
        """
        return progressive_element_cloner.expand_pseudo_elements(element_id)

    @section_tool("progressive-cloning")
    async def expand_animations(element_id: str) -> Dict[str, Any]:
        """
        Expand animations and fonts data for a stored element.

        Args:
            element_id (str): Element ID from clone_element_progressive().

        Returns:
            Dict[str, Any]: Animations, transitions, and fonts data.
        """
        return progressive_element_cloner.expand_animations(element_id)

    @section_tool("progressive-cloning")
    async def list_stored_elements() -> Dict[str, Any]:
        """
        List all stored elements with their basic info.

        Returns:
            Dict[str, Any]: List of stored elements with metadata.
        """
        return progressive_element_cloner.list_stored_elements()

    @section_tool("progressive-cloning")
    async def clear_stored_element(element_id: str) -> Dict[str, Any]:
        """
        Clear a specific stored element.

        Args:
            element_id (str): Element ID to clear.

        Returns:
            Dict[str, Any]: Success/error message.
        """
        return progressive_element_cloner.clear_stored_element(element_id)

    @section_tool("progressive-cloning")
    async def clear_all_elements() -> Dict[str, Any]:
        """
        Clear all stored elements.

        Returns:
            Dict[str, Any]: Success message.
        """
        return progressive_element_cloner.clear_all_elements()

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
