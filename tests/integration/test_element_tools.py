"""
Tests for element_extraction.py and element_interaction.py tools.

Verifies:
- Element cloners (CDP, JS-based, comprehensive, progressive)
- CDP attribute contracts (no AttributeError on real objects)
- Element extraction methods
"""

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import nodriver as uc

import server as _srv

spawn_browser = _srv.spawn_browser
close_instance = _srv.close_instance
navigate = _srv.navigate


async def _spawn() -> str:
    r = await spawn_browser(headless=True, viewport_width=1280, viewport_height=720)
    return r["instance_id"]


async def _close(iid: str):
    try:
        await close_instance(iid)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# CDP Attribute Contracts (from test_cdp_attributes.py)
# ─────────────────────────────────────────────────────────────────────────────


class TestCDPObjectContracts:
    """Verify every attribute used in cloner code exists on the CDP objects."""

    def test_dom_node_has_node_name(self):
        fields = uc.cdp.dom.Node.__dataclass_fields__
        assert "node_name" in fields

    def test_dom_node_no_tag_name(self):
        """tag_name does NOT exist — code must use node_name instead."""
        assert "tag_name" not in uc.cdp.dom.Node.__dataclass_fields__

    def test_css_style_has_css_text(self):
        assert "css_text" in uc.cdp.css.CSSStyle.__dataclass_fields__

    def test_css_style_has_css_properties(self):
        assert "css_properties" in uc.cdp.css.CSSStyle.__dataclass_fields__

    def test_css_property_has_name(self):
        assert "name" in uc.cdp.css.CSSProperty.__dataclass_fields__

    def test_css_rule_has_selector_list(self):
        assert "selector_list" in uc.cdp.css.CSSRule.__dataclass_fields__

    def test_pseudo_element_has_pseudo_type(self):
        assert "pseudo_type" in uc.cdp.css.PseudoElementMatches.__dataclass_fields__

    def test_event_listener_has_type_(self):
        assert "type_" in uc.cdp.dom_debugger.EventListener.__dataclass_fields__


# ─────────────────────────────────────────────────────────────────────────────
# CDPElementCloner (from test_element_cloners.py)
# ─────────────────────────────────────────────────────────────────────────────


class TestCDPElementCloner:

    @pytest.mark.asyncio
    async def test_extract_complete_element_body(self):
        from core.cdp_element_cloner import CDPElementCloner

        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False, timeout=10000)

        cloner = CDPElementCloner()
        result = await cloner.extract_complete_element_cdp(tab, "body")

        assert result is not None
        assert isinstance(result, dict)
        assert "error" not in result or "tag_name" in result
        await _close(iid)

    @pytest.mark.asyncio
    async def test_extract_complete_element_nonexistent(self):
        from core.cdp_element_cloner import CDPElementCloner

        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False, timeout=10000)

        cloner = CDPElementCloner()
        result = await cloner.extract_complete_element_cdp(tab, "#does-not-exist-xyz")

        assert isinstance(result, dict)
        assert "error" in result
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# ElementCloner (JS-based) (from test_element_cloners.py)
# ─────────────────────────────────────────────────────────────────────────────


class TestElementCloner:

    @pytest.mark.asyncio
    async def test_extract_element_styles(self):
        from core.element_cloner import element_cloner

        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False, timeout=10000)

        result = await element_cloner.extract_element_styles(tab, "body")

        assert isinstance(result, dict)
        assert len(result) > 0
        await _close(iid)

    @pytest.mark.asyncio
    async def test_extract_element_structure(self):
        from core.element_cloner import element_cloner

        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False, timeout=10000)

        result = await element_cloner.extract_element_structure(tab, "body")

        assert isinstance(result, dict)
        assert len(result) > 0
        await _close(iid)

    @pytest.mark.asyncio
    async def test_clone_element_complete(self):
        from core.element_cloner import element_cloner

        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False, timeout=10000)

        result = await element_cloner.clone_element_complete(tab, "body")

        assert isinstance(result, dict)
        assert len(result) > 0
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# ProgressiveElementCloner (from test_element_cloners.py)
# ─────────────────────────────────────────────────────────────────────────────


class TestProgressiveElementClonerBrowser:

    @pytest.mark.asyncio
    async def test_clone_element_progressive_returns_element_id(self):
        from core.progressive_element_cloner import progressive_element_cloner

        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False, timeout=10000)

        result = await progressive_element_cloner.clone_element_progressive(tab, "body")

        assert isinstance(result, dict)
        assert "element_id" in result
        element_id = result["element_id"]
        assert element_id is not None

        progressive_element_cloner.clear_stored_element(element_id)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_list_stored_elements_after_clone(self):
        from core.persistent_storage import persistent_storage
        from core.progressive_element_cloner import progressive_element_cloner

        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False, timeout=10000)

        clone_result = await progressive_element_cloner.clone_element_progressive(tab, "body")
        element_id = clone_result["element_id"]

        # Verify element is in the store
        store = persistent_storage.get("progressive_elements", {})
        assert element_id in store

        progressive_element_cloner.clear_stored_element(element_id)
        await _close(iid)
