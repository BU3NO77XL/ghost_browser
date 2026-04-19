"""Unit tests for CSSHandler."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.css_handler import CSSHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── enable_css_domain ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_enable_css_domain_success():
    tab = _make_tab()
    await CSSHandler.enable_css_domain(tab)
    assert tab.send.call_count == 2


@pytest.mark.asyncio
async def test_enable_css_domain_already_enabled():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("already enabled"))
    # Should not raise
    await CSSHandler.enable_css_domain(tab)


# ── _get_node_id_from_selector ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_node_id_from_selector_success():
    tab = _make_tab()
    mock_doc = MagicMock()
    mock_doc.node_id = 1
    tab.send = AsyncMock(side_effect=[mock_doc, 42])

    node_id = await CSSHandler._get_node_id_from_selector(tab, "body")
    assert node_id == 42


@pytest.mark.asyncio
async def test_get_node_id_from_selector_not_found():
    tab = _make_tab()
    mock_doc = MagicMock()
    mock_doc.node_id = 1
    tab.send = AsyncMock(side_effect=[mock_doc, None])

    with pytest.raises(Exception) as exc_info:
        await CSSHandler._get_node_id_from_selector(tab, ".nonexistent")
    assert "No element found" in str(exc_info.value)


# ── get_computed_style ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_computed_style_success():
    tab = _make_tab()
    mock_doc = MagicMock()
    mock_doc.node_id = 1

    mock_prop1 = MagicMock()
    mock_prop1.name = "color"
    mock_prop1.value = "rgb(0,0,0)"
    mock_prop2 = MagicMock()
    mock_prop2.name = "font-size"
    mock_prop2.value = "16px"

    mock_result = MagicMock()
    mock_result.computed_style = [mock_prop1, mock_prop2]

    # enable_css_domain (2 calls) + get_document + query_selector + get_computed_style
    tab.send = AsyncMock(side_effect=[None, None, mock_doc, 10, mock_result])

    result = await CSSHandler.get_computed_style(tab, "body")
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_get_computed_style_empty():
    tab = _make_tab()
    mock_doc = MagicMock()
    mock_doc.node_id = 1

    mock_result = MagicMock()
    mock_result.computed_style = []

    tab.send = AsyncMock(side_effect=[None, None, mock_doc, 10, mock_result])

    result = await CSSHandler.get_computed_style(tab, "body")
    assert result == {}


@pytest.mark.asyncio
async def test_get_computed_style_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await CSSHandler.get_computed_style(tab, "body")
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_computed_style_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await CSSHandler.get_computed_style(tab, "body")
    assert "timed out" in str(exc_info.value).lower()


# ── get_inline_styles ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_inline_styles_success():
    tab = _make_tab()
    mock_doc = MagicMock()
    mock_doc.node_id = 1

    mock_prop = MagicMock()
    mock_prop.name = "color"
    mock_prop.value = "red"

    mock_inline = MagicMock()
    mock_inline.css_properties = [mock_prop]

    mock_result = MagicMock()
    mock_result.inline_style = mock_inline

    # enable_css_domain (2 calls) + get_document + query_selector + get_inline_styles
    tab.send = AsyncMock(side_effect=[None, None, mock_doc, 10, mock_result])

    result = await CSSHandler.get_inline_styles(tab, "#el")
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_get_inline_styles_no_inline():
    tab = _make_tab()
    mock_doc = MagicMock()
    mock_doc.node_id = 1

    mock_result = MagicMock()
    mock_result.inline_style = None

    tab.send = AsyncMock(side_effect=[None, None, mock_doc, 10, mock_result])

    result = await CSSHandler.get_inline_styles(tab, "#el")
    assert result == {}


# ── get_stylesheet_text ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_stylesheet_text_success():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.text = "body { color: red; }"
    tab.send = AsyncMock(side_effect=[None, None, mock_result])

    result = await CSSHandler.get_stylesheet_text(tab, "1")
    assert result == "body { color: red; }"


@pytest.mark.asyncio
async def test_get_stylesheet_text_empty():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.text = None
    tab.send = AsyncMock(side_effect=[None, None, mock_result])

    result = await CSSHandler.get_stylesheet_text(tab, "1")
    assert result == ""


# ── set_stylesheet_text ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_set_stylesheet_text_success():
    tab = _make_tab()
    tab.send = AsyncMock(return_value=None)

    result = await CSSHandler.set_stylesheet_text(tab, "1", "body { color: blue; }")
    assert result is True


@pytest.mark.asyncio
async def test_set_stylesheet_text_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await CSSHandler.set_stylesheet_text(tab, "1", "body {}")
    assert "WebSocket" in str(exc_info.value)


# ── get_media_queries ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_media_queries_success():
    tab = _make_tab()

    mock_expr = MagicMock()
    mock_expr.value = 768
    mock_expr.unit = "px"
    mock_expr.feature = "max-width"

    mock_media = MagicMock()
    mock_media.text = "(max-width: 768px)"
    mock_media.source = "stylesheet"
    mock_media.media_list = [mock_expr]

    mock_result = MagicMock()
    mock_result.medias = [mock_media]

    tab.send = AsyncMock(side_effect=[None, None, mock_result])

    result = await CSSHandler.get_media_queries(tab)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["text"] == "(max-width: 768px)"


@pytest.mark.asyncio
async def test_get_media_queries_empty():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.medias = []
    tab.send = AsyncMock(side_effect=[None, None, mock_result])

    result = await CSSHandler.get_media_queries(tab)
    assert result == []
