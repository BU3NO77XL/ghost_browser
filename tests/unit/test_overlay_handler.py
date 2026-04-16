"""Unit tests for OverlayHandler."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.overlay_handler import OverlayHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── enable / disable ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_enable_overlay_success():
    tab = _make_tab()
    result = await OverlayHandler.enable_overlay(tab)
    assert result is True


@pytest.mark.asyncio
async def test_disable_overlay_success():
    tab = _make_tab()
    result = await OverlayHandler.disable_overlay(tab)
    assert result is True


# ── highlight_node ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_highlight_node_with_node_id():
    tab = _make_tab()
    with patch("core.overlay_handler.cdp") as mock_cdp:
        mock_cdp.overlay.HighlightConfig = MagicMock(return_value=MagicMock())
        mock_cdp.dom.NodeId = MagicMock(return_value=MagicMock())
        mock_cdp.dom.BackendNodeId = MagicMock(return_value=MagicMock())
        mock_cdp.overlay.highlight_node = MagicMock(return_value=MagicMock())
        tab.send = AsyncMock(return_value=None)

        result = await OverlayHandler.highlight_node(tab, {"show_info": True}, node_id=42)
        assert result is True
        mock_cdp.dom.NodeId.assert_called_once_with(42)
        mock_cdp.dom.BackendNodeId.assert_not_called()


@pytest.mark.asyncio
async def test_highlight_node_with_backend_node_id():
    tab = _make_tab()
    with patch("core.overlay_handler.cdp") as mock_cdp:
        mock_cdp.overlay.HighlightConfig = MagicMock(return_value=MagicMock())
        mock_cdp.dom.NodeId = MagicMock(return_value=MagicMock())
        mock_cdp.dom.BackendNodeId = MagicMock(return_value=MagicMock())
        mock_cdp.overlay.highlight_node = MagicMock(return_value=MagicMock())
        tab.send = AsyncMock(return_value=None)

        result = await OverlayHandler.highlight_node(tab, {}, backend_node_id=99)
        assert result is True
        mock_cdp.dom.BackendNodeId.assert_called_once_with(99)
        mock_cdp.dom.NodeId.assert_not_called()


# ── hide_highlight ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_hide_highlight_success():
    tab = _make_tab()
    result = await OverlayHandler.hide_highlight(tab)
    assert result is True


# ── highlight_rect ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_highlight_rect_success():
    tab = _make_tab()
    result = await OverlayHandler.highlight_rect(tab, x=10, y=20, width=100, height=50)
    assert result is True


# ── set_show_grid_overlays ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_set_show_grid_overlays_converts_configs():
    tab = _make_tab()
    with patch("core.overlay_handler.cdp") as mock_cdp:
        mock_cdp.dom.NodeId = MagicMock(return_value=MagicMock())
        mock_cdp.overlay.GridHighlightConfig = MagicMock(return_value=MagicMock())
        mock_cdp.overlay.GridNodeHighlightConfig = MagicMock(return_value=MagicMock())
        mock_cdp.overlay.set_show_grid_overlays = MagicMock(return_value=MagicMock())
        tab.send = AsyncMock(return_value=None)

        configs = [{"node_id": 5, "grid_highlight_config": {}}]
        result = await OverlayHandler.set_show_grid_overlays(tab, configs)
        assert result is True
        mock_cdp.overlay.GridNodeHighlightConfig.assert_called_once()


# ── websocket error ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_enable_overlay_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))
    with pytest.raises(Exception) as exc_info:
        await OverlayHandler.enable_overlay(tab)
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_highlight_rect_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())
    with pytest.raises(Exception) as exc_info:
        await OverlayHandler.highlight_rect(tab, 0, 0, 10, 10)
    assert "timed out" in str(exc_info.value).lower()
