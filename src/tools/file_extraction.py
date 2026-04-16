"""
File-based element extraction tools.

All tools require an explicit output_path pointing to a location inside the
client workspace.  Content is written directly there — it never touches any
server-side directory.
"""

import json
from typing import Any, Dict, List, Optional

from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]
    file_based_element_cloner = deps["file_based_element_cloner"]

    @section_tool("file-extraction")
    async def clone_element_to_file(
        instance_id: str,
        selector: str,
        output_path: str,
        extraction_options: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Clone element completely and save directly to output_path in the workspace.

        The file is written by the server process without passing content through
        the MCP protocol, so there is no payload size limit.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            output_path (str): Absolute path inside the workspace where the JSON
                file should be written, e.g.
                "C:/Users/user/Desktop/project/element.json".
                Parent directories are created automatically.
            extraction_options (Optional[str]): JSON string with extraction options.

        Returns:
            Dict[str, Any]: file_path and extraction summary.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        parsed_options = None
        if extraction_options:
            try:
                parsed_options = json.loads(extraction_options)
            except json.JSONDecodeError:
                return {"error": "Invalid extraction_options JSON"}
        return await file_based_element_cloner.clone_element_complete_to_file(
            tab,
            output_path=output_path,
            selector=selector,
            extraction_options=parsed_options,
            instance_id=instance_id,
        )

    @section_tool("file-extraction")
    async def extract_complete_element_to_file(
        instance_id: str,
        selector: str,
        output_path: str,
        include_children: bool = True,
    ) -> Dict[str, Any]:
        """
        Extract complete element via comprehensive cloner and save to output_path.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            output_path (str): Absolute path inside the workspace.
            include_children (bool): Whether to include child elements.

        Returns:
            Dict[str, Any]: file_path and concise summary.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await file_based_element_cloner.extract_complete_element_to_file(
            tab, selector, output_path, include_children=include_children, instance_id=instance_id
        )

    @section_tool("file-extraction")
    async def extract_element_styles_to_file(
        instance_id: str,
        selector: str,
        output_path: str,
        include_computed: bool = True,
        include_css_rules: bool = True,
        include_pseudo: bool = True,
        include_inheritance: bool = False,
    ) -> Dict[str, Any]:
        """
        Extract element styles and save to output_path.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            output_path (str): Absolute path inside the workspace.
            include_computed (bool): Include computed styles.
            include_css_rules (bool): Include matching CSS rules.
            include_pseudo (bool): Include pseudo-element styles.
            include_inheritance (bool): Include style inheritance chain.

        Returns:
            Dict[str, Any]: file_path and summary of extracted styles.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await file_based_element_cloner.extract_element_styles_to_file(
            tab,
            selector=selector,
            output_path=output_path,
            include_computed=include_computed,
            include_css_rules=include_css_rules,
            include_pseudo=include_pseudo,
            include_inheritance=include_inheritance,
            instance_id=instance_id,
        )

    @section_tool("file-extraction")
    async def extract_element_structure_to_file(
        instance_id: str,
        selector: str,
        output_path: str,
        include_children: bool = False,
        include_attributes: bool = True,
        include_data_attributes: bool = True,
        max_depth: int = 3,
    ) -> Dict[str, Any]:
        """
        Extract element structure and save to output_path.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            output_path (str): Absolute path inside the workspace.
            include_children (bool): Include child elements.
            include_attributes (bool): Include all attributes.
            include_data_attributes (bool): Include data-* attributes.
            max_depth (int): Maximum depth for children extraction.

        Returns:
            Dict[str, Any]: file_path and summary of extracted structure.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await file_based_element_cloner.extract_element_structure_to_file(
            tab,
            output_path=output_path,
            selector=selector,
            include_children=include_children,
            include_attributes=include_attributes,
            include_data_attributes=include_data_attributes,
            max_depth=max_depth,
            instance_id=instance_id,
        )

    @section_tool("file-extraction")
    async def extract_element_events_to_file(
        instance_id: str,
        selector: str,
        output_path: str,
        include_inline: bool = True,
        include_listeners: bool = True,
        include_framework: bool = True,
        analyze_handlers: bool = True,
    ) -> Dict[str, Any]:
        """
        Extract element events and save to output_path.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            output_path (str): Absolute path inside the workspace.
            include_inline (bool): Include inline event handlers.
            include_listeners (bool): Include addEventListener handlers.
            include_framework (bool): Include framework-specific handlers.
            analyze_handlers (bool): Analyze handler functions.

        Returns:
            Dict[str, Any]: file_path and summary of extracted events.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await file_based_element_cloner.extract_element_events_to_file(
            tab,
            output_path=output_path,
            selector=selector,
            include_inline=include_inline,
            include_listeners=include_listeners,
            include_framework=include_framework,
            analyze_handlers=analyze_handlers,
            instance_id=instance_id,
        )

    @section_tool("file-extraction")
    async def extract_element_animations_to_file(
        instance_id: str,
        selector: str,
        output_path: str,
        include_css_animations: bool = True,
        include_transitions: bool = True,
        include_transforms: bool = True,
        analyze_keyframes: bool = True,
    ) -> Dict[str, Any]:
        """
        Extract element animations and save to output_path.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            output_path (str): Absolute path inside the workspace.
            include_css_animations (bool): Include CSS animations.
            include_transitions (bool): Include CSS transitions.
            include_transforms (bool): Include CSS transforms.
            analyze_keyframes (bool): Analyze keyframe rules.

        Returns:
            Dict[str, Any]: file_path and summary of extracted animations.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await file_based_element_cloner.extract_element_animations_to_file(
            tab,
            output_path=output_path,
            selector=selector,
            include_css_animations=include_css_animations,
            include_transitions=include_transitions,
            include_transforms=include_transforms,
            analyze_keyframes=analyze_keyframes,
            instance_id=instance_id,
        )

    @section_tool("file-extraction")
    async def extract_element_assets_to_file(
        instance_id: str,
        selector: str,
        output_path: str,
        include_images: bool = True,
        include_backgrounds: bool = True,
        include_fonts: bool = True,
        fetch_external: bool = False,
    ) -> Dict[str, Any]:
        """
        Extract element assets and save to output_path.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            output_path (str): Absolute path inside the workspace.
            include_images (bool): Include images.
            include_backgrounds (bool): Include background images.
            include_fonts (bool): Include font information.
            fetch_external (bool): Fetch external assets.

        Returns:
            Dict[str, Any]: file_path and summary of extracted assets.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await file_based_element_cloner.extract_element_assets_to_file(
            tab,
            output_path=output_path,
            selector=selector,
            include_images=include_images,
            include_backgrounds=include_backgrounds,
            include_fonts=include_fonts,
            fetch_external=fetch_external,
            instance_id=instance_id,
        )

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
