"""Element extraction tools: styles, structure, events, animations, assets."""

import json
from typing import Any, Dict, Optional

from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]
    element_cloner = deps["element_cloner"]
    comprehensive_element_cloner = deps["comprehensive_element_cloner"]
    response_handler = deps["response_handler"]

    @section_tool("element-extraction")
    async def extract_element_styles(
        instance_id: str,
        selector: str,
        include_computed: bool = True,
        include_css_rules: bool = True,
        include_pseudo: bool = True,
        include_inheritance: bool = False,
    ) -> Dict[str, Any]:
        """
        Extract complete styling information from an element.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            include_computed (bool): Include computed styles.
            include_css_rules (bool): Include matching CSS rules.
            include_pseudo (bool): Include pseudo-element styles (::before, ::after).
            include_inheritance (bool): Include style inheritance chain.

        Returns:
            Dict[str, Any]: Complete styling data.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await element_cloner.extract_element_styles(
            tab,
            selector=selector,
            include_computed=include_computed,
            include_css_rules=include_css_rules,
            include_pseudo=include_pseudo,
            include_inheritance=include_inheritance,
        )

    @section_tool("element-extraction")
    async def extract_element_structure(
        instance_id: str,
        selector: str,
        include_children: bool = False,
        include_attributes: bool = True,
        include_data_attributes: bool = True,
        max_depth: int = 3,
    ) -> Dict[str, Any]:
        """
        Extract complete HTML structure and DOM information.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            include_children (bool): Include child elements.
            include_attributes (bool): Include all attributes.
            include_data_attributes (bool): Include data-* attributes specifically.
            max_depth (int): Maximum depth for children extraction.

        Returns:
            Dict[str, Any]: HTML structure, attributes, position, and children data.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await element_cloner.extract_element_structure(
            tab,
            selector=selector,
            include_children=include_children,
            include_attributes=include_attributes,
            include_data_attributes=include_data_attributes,
            max_depth=max_depth,
        )

    @section_tool("element-extraction")
    async def extract_element_events(
        instance_id: str,
        selector: str,
        include_inline: bool = True,
        include_listeners: bool = True,
        include_framework: bool = True,
        analyze_handlers: bool = False,
    ) -> Dict[str, Any]:
        """
        Extract complete event listener and JavaScript handler information.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            include_inline (bool): Include inline event handlers.
            include_listeners (bool): Include addEventListener attached handlers.
            include_framework (bool): Include framework-specific handlers.
            analyze_handlers (bool): Analyze handler functions for full details.

        Returns:
            Dict[str, Any]: Event listeners, inline handlers, framework handlers.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await element_cloner.extract_element_events(
            tab,
            selector=selector,
            include_inline=include_inline,
            include_listeners=include_listeners,
            include_framework=include_framework,
            analyze_handlers=analyze_handlers,
        )

    @section_tool("element-extraction")
    async def extract_element_animations(
        instance_id: str,
        selector: str,
        include_css_animations: bool = True,
        include_transitions: bool = True,
        include_transforms: bool = True,
        analyze_keyframes: bool = True,
    ) -> Dict[str, Any]:
        """
        Extract CSS animations, transitions, and transforms.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            include_css_animations (bool): Include CSS @keyframes animations.
            include_transitions (bool): Include CSS transitions.
            include_transforms (bool): Include CSS transforms.
            analyze_keyframes (bool): Analyze keyframe rules.

        Returns:
            Dict[str, Any]: Animation data, transition data, transform data.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await element_cloner.extract_element_animations(
            tab,
            selector=selector,
            include_css_animations=include_css_animations,
            include_transitions=include_transitions,
            include_transforms=include_transforms,
            analyze_keyframes=analyze_keyframes,
        )

    @section_tool("element-extraction")
    async def extract_element_assets(
        instance_id: str,
        selector: str,
        include_images: bool = True,
        include_backgrounds: bool = True,
        include_fonts: bool = True,
        fetch_external: bool = False,
    ) -> Dict[str, Any]:
        """
        Extract all assets related to an element (images, fonts, etc.).

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            include_images (bool): Include img src and related images.
            include_backgrounds (bool): Include background images.
            include_fonts (bool): Include font information.
            fetch_external (bool): Whether to fetch external assets for analysis.

        Returns:
            Dict[str, Any]: Images, background images, fonts, icons, videos, audio assets.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        result = await element_cloner.extract_element_assets(
            tab,
            selector=selector,
            include_images=include_images,
            include_backgrounds=include_backgrounds,
            include_fonts=include_fonts,
            fetch_external=fetch_external,
        )
        return response_handler.handle_response(
            result, f"element_assets_{instance_id}_{selector.replace(' ', '_')}"
        )

    @section_tool("element-extraction")
    async def extract_element_styles_cdp(
        instance_id: str,
        selector: str,
        include_computed: bool = True,
        include_css_rules: bool = True,
        include_pseudo: bool = True,
        include_inheritance: bool = False,
    ) -> Dict[str, Any]:
        """
        Extract element styles using direct CDP calls (no JavaScript evaluation).

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            include_computed (bool): Include computed styles.
            include_css_rules (bool): Include matching CSS rules.
            include_pseudo (bool): Include pseudo-element styles.
            include_inheritance (bool): Include style inheritance chain.

        Returns:
            Dict[str, Any]: Styling data extracted using CDP.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await element_cloner.extract_element_styles_cdp(
            tab,
            selector=selector,
            include_computed=include_computed,
            include_css_rules=include_css_rules,
            include_pseudo=include_pseudo,
            include_inheritance=include_inheritance,
        )

    @section_tool("element-extraction")
    async def extract_related_files(
        instance_id: str,
        analyze_css: bool = True,
        analyze_js: bool = True,
        follow_imports: bool = False,
        max_depth: int = 2,
    ) -> Dict[str, Any]:
        """
        Discover and analyze related CSS/JS files for context.

        Args:
            instance_id (str): Browser instance ID.
            analyze_css (bool): Analyze linked CSS files.
            analyze_js (bool): Analyze linked JS files.
            follow_imports (bool): Follow @import and module imports.
            max_depth (int): Maximum depth for following imports.

        Returns:
            Dict[str, Any]: Stylesheets, scripts, imports, modules, framework detection.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        result = await element_cloner.extract_related_files(
            tab,
            analyze_css=analyze_css,
            analyze_js=analyze_js,
            follow_imports=follow_imports,
            max_depth=max_depth,
        )
        return response_handler.handle_response(result, f"related_files_{instance_id}")

    @section_tool("element-extraction")
    async def clone_element_complete(
        instance_id: str, selector: str, extraction_options: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Master function that extracts ALL element data using specialized functions.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            extraction_options (Optional[str]): JSON string with extraction options.

        Returns:
            Dict[str, Any]: Complete element clone with styles, structure, events, animations, assets.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        parsed_options = None
        if extraction_options:
            try:
                parsed_options = json.loads(extraction_options)
            except json.JSONDecodeError:
                raise Exception(f"Invalid JSON in extraction_options: {extraction_options}")
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        result = await comprehensive_element_cloner.extract_complete_element(
            tab,
            selector=selector,
            include_children=(
                parsed_options.get("structure", {}).get("include_children", True)
                if parsed_options
                else True
            ),
        )
        return response_handler.handle_response(
            result,
            fallback_filename_prefix="complete_clone",
            metadata={
                "selector": selector,
                "extraction_options": parsed_options,
                "url": getattr(tab, "url", "unknown"),
            },
        )

    @section_tool("element-extraction")
    async def extract_complete_element_cdp(
        instance_id: str, selector: str, include_children: bool = True
    ) -> Dict[str, Any]:
        """
        Extract complete element using native CDP methods for 100% accuracy.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the element.
            include_children (bool): Whether to include child elements.

        Returns:
            Dict[str, Any]: Complete element data with 100% accuracy.
        """
        from core.cdp_element_cloner import CDPElementCloner

        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        cdp_cloner = CDPElementCloner()
        return await cdp_cloner.extract_complete_element_cdp(tab, selector, include_children)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
