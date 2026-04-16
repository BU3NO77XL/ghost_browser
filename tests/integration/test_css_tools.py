"""Integration tests for css_management tools module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_deps(tab=None):
    if tab is None:
        tab = AsyncMock()
        tab.send = AsyncMock(return_value=None)
    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=tab)
    return {"browser_manager": bm}, tab


def _register():
    from tools.css_management import register
    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func
        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_get_computed_style_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_doc = MagicMock()
    mock_doc.node_id = 1
    mock_prop = MagicMock()
    mock_prop.name = "color"
    mock_prop.value = "black"
    mock_result = MagicMock()
    mock_result.computed_style = [mock_prop]
    # enable_css_domain + get_document + query_selector + get_computed_style
    tab.send = AsyncMock(side_effect=[None, mock_doc, 10, mock_result])

    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_computed_style"]("inst-1", selector="body")
        assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_get_inline_styles_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_doc = MagicMock()
    mock_doc.node_id = 1
    mock_prop = MagicMock()
    mock_prop.name = "color"
    mock_prop.value = "red"
    mock_inline = MagicMock()
    mock_inline.css_properties = [mock_prop]
    mock_result = MagicMock()
    mock_result.inline_style = mock_inline
    # enable_css_domain + get_document + query_selector + get_inline_styles
    tab.send = AsyncMock(side_effect=[None, mock_doc, 10, mock_result])

    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_inline_styles"]("inst-1", selector="#el")
        assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_get_matched_styles_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_doc = MagicMock()
    mock_doc.node_id = 1
    mock_result = MagicMock()
    mock_result.matched_css_rules = []
    mock_result.inline_style = None
    # enable_css_domain + get_document + query_selector + get_matched_styles
    tab.send = AsyncMock(side_effect=[None, mock_doc, 10, mock_result])

    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_matched_styles"]("inst-1", selector="body")
        assert "matched_rules" in result
        assert "inline_style" in result


@pytest.mark.asyncio
async def test_get_stylesheet_text_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.text = "body { color: red; }"
    tab.send = AsyncMock(side_effect=[None, mock_result])

    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_stylesheet_text"]("inst-1", stylesheet_id="1")
        assert result == "body { color: red; }"


@pytest.mark.asyncio
async def test_set_stylesheet_text_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["set_stylesheet_text"](
            "inst-1", stylesheet_id="1", text="body { color: blue; }"
        )
        assert result is True


@pytest.mark.asyncio
async def test_get_media_queries_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.medias = []
    tab.send = AsyncMock(side_effect=[None, mock_result])

    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_media_queries"]("inst-1")
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_css_tool_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["get_computed_style"]("bad-id", selector="body")
        assert "not found" in str(exc_info.value).lower()
