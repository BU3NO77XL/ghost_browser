"""
CDP Attribute Contract Tests
============================

Verifies that every attribute accessed on nodriver CDP objects in the cloner
modules actually exists on those objects. This catches the class of bug where
code uses `obj.tag_name` but nodriver exposes `obj.node_name`.

Strategy:
  1. Instantiate real CDP objects with minimal data
  2. Assert every attribute access used in the source code is valid
  3. Run a live browser extraction and assert no "has no attribute" errors appear

No mocking — we test against the real nodriver classes.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import nodriver as uc


# ─────────────────────────────────────────────────────────────────────────────
# 1. Static contract — verify field names on CDP dataclasses
# ─────────────────────────────────────────────────────────────────────────────

class TestCDPObjectContracts:
    """Verify every attribute used in cloner code exists on the CDP objects."""

    # ── dom.Node ─────────────────────────────────────────────────────────────
    def test_dom_node_has_node_name(self):
        fields = uc.cdp.dom.Node.__dataclass_fields__
        assert "node_name" in fields, "dom.Node must have node_name"

    def test_dom_node_has_local_name(self):
        assert "local_name" in uc.cdp.dom.Node.__dataclass_fields__

    def test_dom_node_has_node_value(self):
        assert "node_value" in uc.cdp.dom.Node.__dataclass_fields__

    def test_dom_node_has_node_id(self):
        assert "node_id" in uc.cdp.dom.Node.__dataclass_fields__

    def test_dom_node_has_attributes(self):
        assert "attributes" in uc.cdp.dom.Node.__dataclass_fields__

    def test_dom_node_has_children(self):
        assert "children" in uc.cdp.dom.Node.__dataclass_fields__

    def test_dom_node_has_node_type(self):
        assert "node_type" in uc.cdp.dom.Node.__dataclass_fields__

    def test_dom_node_has_pseudo_identifier(self):
        assert "pseudo_identifier" in uc.cdp.dom.Node.__dataclass_fields__

    def test_dom_node_no_tag_name(self):
        """tag_name does NOT exist — code must use node_name instead."""
        assert "tag_name" not in uc.cdp.dom.Node.__dataclass_fields__, \
            "dom.Node has no tag_name — use node_name"

    # ── css.CSSStyle ─────────────────────────────────────────────────────────
    def test_css_style_has_css_text(self):
        assert "css_text" in uc.cdp.css.CSSStyle.__dataclass_fields__

    def test_css_style_has_css_properties(self):
        assert "css_properties" in uc.cdp.css.CSSStyle.__dataclass_fields__

    def test_css_style_has_style_sheet_id(self):
        assert "style_sheet_id" in uc.cdp.css.CSSStyle.__dataclass_fields__

    def test_css_style_no_css_text_underscore(self):
        """css_text_ does NOT exist — trailing underscore is wrong."""
        assert "css_text_" not in uc.cdp.css.CSSStyle.__dataclass_fields__, \
            "CSSStyle has no css_text_ — use css_text"

    def test_css_style_no_css_properties_underscore(self):
        """css_properties_ does NOT exist."""
        assert "css_properties_" not in uc.cdp.css.CSSStyle.__dataclass_fields__, \
            "CSSStyle has no css_properties_ — use css_properties"

    # ── css.CSSProperty ──────────────────────────────────────────────────────
    def test_css_property_has_name(self):
        assert "name" in uc.cdp.css.CSSProperty.__dataclass_fields__

    def test_css_property_has_value(self):
        assert "value" in uc.cdp.css.CSSProperty.__dataclass_fields__

    def test_css_property_has_important(self):
        assert "important" in uc.cdp.css.CSSProperty.__dataclass_fields__

    def test_css_property_has_implicit(self):
        assert "implicit" in uc.cdp.css.CSSProperty.__dataclass_fields__

    def test_css_property_has_text(self):
        assert "text" in uc.cdp.css.CSSProperty.__dataclass_fields__

    def test_css_property_has_parsed_ok(self):
        assert "parsed_ok" in uc.cdp.css.CSSProperty.__dataclass_fields__

    def test_css_property_has_disabled(self):
        assert "disabled" in uc.cdp.css.CSSProperty.__dataclass_fields__

    # ── css.CSSComputedStyleProperty ─────────────────────────────────────────
    def test_computed_style_prop_has_name(self):
        assert "name" in uc.cdp.css.CSSComputedStyleProperty.__dataclass_fields__

    def test_computed_style_prop_has_value(self):
        assert "value" in uc.cdp.css.CSSComputedStyleProperty.__dataclass_fields__

    # ── css.RuleMatch ─────────────────────────────────────────────────────────
    def test_rule_match_has_rule(self):
        assert "rule" in uc.cdp.css.RuleMatch.__dataclass_fields__

    def test_rule_match_has_matching_selectors(self):
        assert "matching_selectors" in uc.cdp.css.RuleMatch.__dataclass_fields__

    # ── css.CSSRule ───────────────────────────────────────────────────────────
    def test_css_rule_has_selector_list(self):
        assert "selector_list" in uc.cdp.css.CSSRule.__dataclass_fields__

    def test_css_rule_has_origin(self):
        assert "origin" in uc.cdp.css.CSSRule.__dataclass_fields__

    def test_css_rule_has_style(self):
        assert "style" in uc.cdp.css.CSSRule.__dataclass_fields__

    def test_css_rule_has_style_sheet_id(self):
        assert "style_sheet_id" in uc.cdp.css.CSSRule.__dataclass_fields__

    def test_css_rule_no_style_sheet_id_underscore(self):
        """style_sheet_id_ does NOT exist."""
        assert "style_sheet_id_" not in uc.cdp.css.CSSRule.__dataclass_fields__, \
            "CSSRule has no style_sheet_id_ — use style_sheet_id"

    # ── css.SelectorList ──────────────────────────────────────────────────────
    def test_selector_list_has_text(self):
        assert "text" in uc.cdp.css.SelectorList.__dataclass_fields__

    def test_selector_list_has_selectors(self):
        assert "selectors" in uc.cdp.css.SelectorList.__dataclass_fields__

    # ── css.PseudoElementMatches ──────────────────────────────────────────────
    def test_pseudo_element_has_pseudo_type(self):
        assert "pseudo_type" in uc.cdp.css.PseudoElementMatches.__dataclass_fields__

    def test_pseudo_element_has_matches(self):
        assert "matches" in uc.cdp.css.PseudoElementMatches.__dataclass_fields__

    def test_pseudo_element_has_pseudo_identifier(self):
        assert "pseudo_identifier" in uc.cdp.css.PseudoElementMatches.__dataclass_fields__

    def test_pseudo_element_no_matches_underscore(self):
        """matches_ does NOT exist."""
        assert "matches_" not in uc.cdp.css.PseudoElementMatches.__dataclass_fields__, \
            "PseudoElementMatches has no matches_ — use matches"

    def test_pseudo_element_no_pseudo_identifier_underscore(self):
        """pseudo_identifier_ does NOT exist."""
        assert "pseudo_identifier_" not in uc.cdp.css.PseudoElementMatches.__dataclass_fields__, \
            "PseudoElementMatches has no pseudo_identifier_ — use pseudo_identifier"

    # ── css.InheritedStyleEntry ───────────────────────────────────────────────
    def test_inherited_style_has_inline_style(self):
        assert "inline_style" in uc.cdp.css.InheritedStyleEntry.__dataclass_fields__

    def test_inherited_style_has_matched_css_rules(self):
        assert "matched_css_rules" in uc.cdp.css.InheritedStyleEntry.__dataclass_fields__

    # ── dom_debugger.EventListener ────────────────────────────────────────────
    def test_event_listener_has_type_(self):
        assert "type_" in uc.cdp.dom_debugger.EventListener.__dataclass_fields__

    def test_event_listener_has_use_capture(self):
        assert "use_capture" in uc.cdp.dom_debugger.EventListener.__dataclass_fields__

    def test_event_listener_has_passive(self):
        assert "passive" in uc.cdp.dom_debugger.EventListener.__dataclass_fields__

    def test_event_listener_has_once(self):
        assert "once" in uc.cdp.dom_debugger.EventListener.__dataclass_fields__

    def test_event_listener_has_script_id(self):
        assert "script_id" in uc.cdp.dom_debugger.EventListener.__dataclass_fields__

    def test_event_listener_has_line_number(self):
        assert "line_number" in uc.cdp.dom_debugger.EventListener.__dataclass_fields__

    def test_event_listener_has_column_number(self):
        assert "column_number" in uc.cdp.dom_debugger.EventListener.__dataclass_fields__

    def test_event_listener_has_handler(self):
        assert "handler" in uc.cdp.dom_debugger.EventListener.__dataclass_fields__

    def test_event_listener_has_original_handler(self):
        assert "original_handler" in uc.cdp.dom_debugger.EventListener.__dataclass_fields__

    def test_event_listener_has_backend_node_id(self):
        assert "backend_node_id" in uc.cdp.dom_debugger.EventListener.__dataclass_fields__

    # ── runtime.RemoteObject ──────────────────────────────────────────────────
    def test_remote_object_has_object_id(self):
        assert "object_id" in uc.cdp.runtime.RemoteObject.__dataclass_fields__

    def test_remote_object_has_value(self):
        assert "value" in uc.cdp.runtime.RemoteObject.__dataclass_fields__

    def test_remote_object_has_deep_serialized_value(self):
        assert "deep_serialized_value" in uc.cdp.runtime.RemoteObject.__dataclass_fields__

    def test_remote_object_has_type_(self):
        assert "type_" in uc.cdp.runtime.RemoteObject.__dataclass_fields__

    # ── css.CSSStyleSheetHeader ───────────────────────────────────────────────
    def test_stylesheet_header_has_style_sheet_id(self):
        assert "style_sheet_id" in uc.cdp.css.CSSStyleSheetHeader.__dataclass_fields__

    def test_stylesheet_header_has_source_url(self):
        assert "source_url" in uc.cdp.css.CSSStyleSheetHeader.__dataclass_fields__

    def test_stylesheet_header_has_origin(self):
        assert "origin" in uc.cdp.css.CSSStyleSheetHeader.__dataclass_fields__

    def test_stylesheet_header_has_disabled(self):
        assert "disabled" in uc.cdp.css.CSSStyleSheetHeader.__dataclass_fields__

    # ── dom.BackendNode ───────────────────────────────────────────────────────
    def test_backend_node_has_node_type(self):
        assert "node_type" in uc.cdp.dom.BackendNode.__dataclass_fields__

    def test_backend_node_has_node_name(self):
        assert "node_name" in uc.cdp.dom.BackendNode.__dataclass_fields__

    def test_backend_node_has_backend_node_id(self):
        assert "backend_node_id" in uc.cdp.dom.BackendNode.__dataclass_fields__


# ─────────────────────────────────────────────────────────────────────────────
# 2. Instantiation tests — create real objects and access attributes
# ─────────────────────────────────────────────────────────────────────────────

class TestCDPObjectInstantiation:
    """Create real CDP objects and verify attribute access doesn't raise."""

    def test_css_style_attribute_access(self):
        """CSSStyle attributes used in _css_style_to_dict must be accessible."""
        style = uc.cdp.css.CSSStyle(
            css_properties=[],
            shorthand_entries=[],
        )
        # These are the exact accesses in _css_style_to_dict
        _ = style.css_text        # was css_text_ — FIXED
        _ = style.css_properties  # was css_properties_ — FIXED
        assert True

    def test_css_property_attribute_access(self):
        """CSSProperty attributes used in _css_style_to_dict must be accessible."""
        prop = uc.cdp.css.CSSProperty(name="color", value="red")
        _ = prop.name
        _ = prop.value
        _ = prop.important
        _ = prop.implicit
        _ = prop.text
        _ = prop.parsed_ok
        _ = prop.disabled
        assert True

    def test_computed_style_property_access(self):
        """CSSComputedStyleProperty used in _get_computed_styles_cdp."""
        prop = uc.cdp.css.CSSComputedStyleProperty(name="display", value="block")
        assert prop.name == "display"
        assert prop.value == "block"

    def test_pseudo_element_matches_access(self):
        """PseudoElementMatches attributes used in _pseudo_element_to_dict."""
        pe = uc.cdp.css.PseudoElementMatches(
            pseudo_type=uc.cdp.dom.PseudoType.BEFORE,
            matches=[],
        )
        _ = pe.pseudo_type
        _ = pe.matches          # was matches_ — FIXED
        _ = pe.pseudo_identifier  # was pseudo_identifier_ — FIXED
        assert True

    def test_inherited_style_entry_access(self):
        """InheritedStyleEntry attributes used in _inherited_style_to_dict."""
        entry = uc.cdp.css.InheritedStyleEntry(matched_css_rules=[])
        _ = entry.inline_style
        _ = entry.matched_css_rules
        assert True

    def test_dom_node_no_tag_name_raises(self):
        """Accessing tag_name on Node must raise AttributeError."""
        node = uc.cdp.dom.Node(
            node_id=uc.cdp.dom.NodeId(1),
            backend_node_id=uc.cdp.dom.BackendNodeId(1),
            node_type=1,
            node_name="BODY",
            local_name="body",
            node_value="",
        )
        with pytest.raises(AttributeError):
            _ = node.tag_name  # This is the bug that was fixed

    def test_dom_node_node_name_works(self):
        """node_name is the correct attribute (not tag_name)."""
        node = uc.cdp.dom.Node(
            node_id=uc.cdp.dom.NodeId(1),
            backend_node_id=uc.cdp.dom.BackendNodeId(1),
            node_type=1,
            node_name="BODY",
            local_name="body",
            node_value="",
        )
        assert node.node_name == "BODY"
        assert node.local_name == "body"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Live browser tests — run actual extraction and check for attribute errors
# ─────────────────────────────────────────────────────────────────────────────

class TestCDPLiveExtraction:
    """Run real CDP extraction and verify no attribute errors occur."""

    @pytest.mark.asyncio
    async def test_cdp_cloner_no_attribute_errors(self):
        """
        Full CDP extraction must complete without any 'has no attribute' errors.
        This catches regressions where new attribute bugs are introduced.
        """
        import server as _srv
        from debug_logger import debug_logger

        iid = None
        try:
            result = await _srv.spawn_browser(headless=False, viewport_width=1280, viewport_height=720)
            iid = result["instance_id"]
            await _srv.navigate(iid, "https://httpbin.org/html", inject_cookies=False)

            tab = await _srv.browser_manager.get_tab(iid)
            from cdp_element_cloner import CDPElementCloner
            cloner = CDPElementCloner()

            extraction = await cloner.extract_complete_element_cdp(tab, "body", include_children=False)

            # Must not be an error
            assert "error" not in extraction, f"CDP extraction returned error: {extraction.get('error')}"

            # Must have expected structure
            assert "element" in extraction
            assert "extraction_stats" in extraction

            # HTML section must have tagName (not error)
            html = extraction["element"]["html"]
            assert "error" not in html, f"_get_element_html failed: {html.get('error')}"
            assert "tagName" in html
            assert html["tagName"] != ""

            # Computed styles must be a dict (not empty due to attribute error)
            computed = extraction["element"]["computed_styles"]
            assert isinstance(computed, dict)
            assert len(computed) > 0, "Computed styles should not be empty for body element"

            # Matched styles must have expected keys
            matched = extraction["element"]["matched_styles"]
            assert isinstance(matched, dict)
            assert "matchedCSSRules" in matched
            assert "inlineStyle" in matched

            # Event listeners must be a list
            listeners = extraction["element"]["event_listeners"]
            assert isinstance(listeners, list)

            # Stats must be non-negative numbers
            stats = extraction["extraction_stats"]
            assert stats["computed_styles_count"] > 0
            assert stats["css_rules_count"] >= 0
            assert stats["event_listeners_count"] >= 0

        finally:
            if iid:
                try:
                    await _srv.close_instance(iid)
                except Exception:
                    pass

    @pytest.mark.asyncio
    async def test_cdp_cloner_with_children_no_errors(self):
        """CDP extraction with children must not produce attribute errors."""
        import server as _srv
        from cdp_element_cloner import CDPElementCloner

        iid = None
        try:
            result = await _srv.spawn_browser(headless=False, viewport_width=1280, viewport_height=720)
            iid = result["instance_id"]
            await _srv.navigate(iid, "https://httpbin.org/html", inject_cookies=False)

            tab = await _srv.browser_manager.get_tab(iid)
            cloner = CDPElementCloner()

            extraction = await cloner.extract_complete_element_cdp(tab, "body", include_children=True)

            assert "error" not in extraction
            children = extraction["element"]["children"]
            assert isinstance(children, list)

            # Each child must have html and computed_styles without errors
            for child in children[:3]:  # check first 3 children
                assert "html" in child
                assert "error" not in child.get("html", {})

        finally:
            if iid:
                try:
                    await _srv.close_instance(iid)
                except Exception:
                    pass

    @pytest.mark.asyncio
    async def test_element_cloner_styles_cdp_no_errors(self):
        """element_cloner.extract_element_styles_cdp must not produce attribute errors."""
        import server as _srv
        from element_cloner import element_cloner

        iid = None
        try:
            result = await _srv.spawn_browser(headless=False, viewport_width=1280, viewport_height=720)
            iid = result["instance_id"]
            await _srv.navigate(iid, "https://httpbin.org/html", inject_cookies=False)

            tab = await _srv.browser_manager.get_tab(iid)

            styles = await element_cloner.extract_element_styles_cdp(tab, selector="body")

            assert isinstance(styles, dict)
            assert "error" not in styles
            # Must have computed styles
            assert "computed_styles" in styles
            assert len(styles["computed_styles"]) > 0

        finally:
            if iid:
                try:
                    await _srv.close_instance(iid)
                except Exception:
                    pass

    @pytest.mark.asyncio
    async def test_comprehensive_cloner_no_errors(self):
        """comprehensive_element_cloner must complete without errors."""
        import server as _srv
        from comprehensive_element_cloner import comprehensive_element_cloner

        iid = None
        try:
            result = await _srv.spawn_browser(headless=False, viewport_width=1280, viewport_height=720)
            iid = result["instance_id"]
            await _srv.navigate(iid, "https://httpbin.org/html", inject_cookies=False)

            tab = await _srv.browser_manager.get_tab(iid)

            extraction = await comprehensive_element_cloner.extract_complete_element(
                tab, "body", include_children=False
            )

            assert isinstance(extraction, dict)
            assert "error" not in extraction
            # Must have element data
            assert "element" in extraction or "html" in extraction

        finally:
            if iid:
                try:
                    await _srv.close_instance(iid)
                except Exception:
                    pass
