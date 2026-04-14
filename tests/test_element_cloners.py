"""
Tests for element cloner modules that require a live browser:
- cdp_element_cloner.py
- element_cloner.py
- comprehensive_element_cloner.py
- progressive_element_cloner.py (browser methods)

All tests use httpbin.org/html as a stable test page.
"""

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import server as _srv

spawn_browser  = _srv.spawn_browser
close_instance = _srv.close_instance
navigate       = _srv.navigate


async def _spawn() -> str:
    r = await spawn_browser(headless=False, viewport_width=1280, viewport_height=720)
    return r["instance_id"]

async def _close(iid: str):
    try:
        await close_instance(iid)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# CDPElementCloner
# ─────────────────────────────────────────────────────────────────────────────
class TestCDPElementCloner:

    @pytest.mark.asyncio
    async def test_extract_complete_element_body(self):
        from cdp_element_cloner import CDPElementCloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        cloner = CDPElementCloner()
        result = await cloner.extract_complete_element_cdp(tab, "body")

        assert result is not None
        assert isinstance(result, dict)
        assert "tag_name" in result or "error" not in result
        await _close(iid)

    @pytest.mark.asyncio
    async def test_extract_complete_element_nonexistent(self):
        from cdp_element_cloner import CDPElementCloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        cloner = CDPElementCloner()
        result = await cloner.extract_complete_element_cdp(tab, "#does-not-exist-xyz")

        # Should return error dict, not raise
        assert isinstance(result, dict)
        assert "error" in result
        await _close(iid)

    @pytest.mark.asyncio
    async def test_extract_element_has_html(self):
        from cdp_element_cloner import CDPElementCloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        cloner = CDPElementCloner()
        result = await cloner.extract_complete_element_cdp(tab, "h1", include_children=False)

        assert isinstance(result, dict)
        # Should have some content
        assert len(result) > 0
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# ElementCloner (JS-based)
# ─────────────────────────────────────────────────────────────────────────────
class TestElementCloner:

    @pytest.mark.asyncio
    async def test_extract_element_styles(self):
        from element_cloner import element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await element_cloner.extract_element_styles(tab, "body")

        assert isinstance(result, dict)
        # Should have computed styles or error
        assert len(result) > 0
        await _close(iid)

    @pytest.mark.asyncio
    async def test_extract_element_structure(self):
        from element_cloner import element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await element_cloner.extract_element_structure(tab, "body")

        assert isinstance(result, dict)
        assert len(result) > 0
        await _close(iid)

    @pytest.mark.asyncio
    async def test_extract_element_events(self):
        from element_cloner import element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await element_cloner.extract_element_events(tab, "body")

        assert isinstance(result, dict)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_extract_element_animations(self):
        from element_cloner import element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await element_cloner.extract_element_animations(tab, "body")

        assert isinstance(result, dict)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_extract_element_assets(self):
        from element_cloner import element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await element_cloner.extract_element_assets(tab, "body")

        assert isinstance(result, dict)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_extract_element_styles_cdp(self):
        from element_cloner import element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await element_cloner.extract_element_styles_cdp(tab, "body")

        assert isinstance(result, dict)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_clone_element_complete(self):
        from element_cloner import element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await element_cloner.clone_element_complete(tab, "body")

        assert isinstance(result, dict)
        # Should have multiple sections
        assert len(result) > 0
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# ProgressiveElementCloner — browser methods
# ─────────────────────────────────────────────────────────────────────────────
class TestProgressiveElementClonerBrowser:

    @pytest.mark.asyncio
    async def test_clone_element_progressive_returns_element_id(self):
        from progressive_element_cloner import progressive_element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await progressive_element_cloner.clone_element_progressive(tab, "body")

        assert isinstance(result, dict)
        assert "element_id" in result
        element_id = result["element_id"]
        assert element_id is not None

        # Cleanup stored element
        progressive_element_cloner.clear_stored_element(element_id)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_expand_styles_after_clone(self):
        from progressive_element_cloner import progressive_element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        clone_result = await progressive_element_cloner.clone_element_progressive(tab, "body")
        element_id = clone_result["element_id"]

        styles = progressive_element_cloner.expand_styles(element_id)
        assert isinstance(styles, dict)
        assert "error" not in styles

        progressive_element_cloner.clear_stored_element(element_id)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_expand_children_after_clone(self):
        from progressive_element_cloner import progressive_element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        clone_result = await progressive_element_cloner.clone_element_progressive(tab, "body")
        element_id = clone_result["element_id"]

        children = progressive_element_cloner.expand_children(element_id)
        assert isinstance(children, dict)

        progressive_element_cloner.clear_stored_element(element_id)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_list_stored_elements_after_clone(self):
        from progressive_element_cloner import progressive_element_cloner
        from persistent_storage import persistent_storage
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        clone_result = await progressive_element_cloner.clone_element_progressive(tab, "body")
        element_id = clone_result["element_id"]

        # Verify element is in the store directly
        store = persistent_storage.get("progressive_elements", {})
        assert element_id in store, f"Element {element_id} not found in store"

        # Also verify list_stored_elements returns it
        stored = progressive_element_cloner.list_stored_elements()
        key = "stored_elements" if "stored_elements" in stored else "elements"
        element_ids = [e.get("element_id") for e in stored.get(key, [])]
        assert element_id in element_ids

        progressive_element_cloner.clear_stored_element(element_id)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_clear_stored_element(self):
        from progressive_element_cloner import progressive_element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        clone_result = await progressive_element_cloner.clone_element_progressive(tab, "body")
        element_id = clone_result["element_id"]

        clear_result = progressive_element_cloner.clear_stored_element(element_id)
        assert "error" not in clear_result

        # Should be gone now
        styles = progressive_element_cloner.expand_styles(element_id)
        assert "error" in styles

        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# ComprehensiveElementCloner
# ─────────────────────────────────────────────────────────────────────────────
class TestComprehensiveElementCloner:

    @pytest.mark.asyncio
    async def test_extract_complete_element(self):
        from comprehensive_element_cloner import comprehensive_element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await comprehensive_element_cloner.extract_complete_element(tab, "body")

        assert isinstance(result, dict)
        assert len(result) > 0
        await _close(iid)

    @pytest.mark.asyncio
    async def test_extract_complete_element_to_file(self, tmp_path):
        from comprehensive_element_cloner import comprehensive_element_cloner
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await comprehensive_element_cloner.extract_complete_element(
            tab, "body", include_children=False
        )

        assert isinstance(result, dict)
        await _close(iid)
