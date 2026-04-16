"""Unit tests for DOMSnapshotHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.dom_snapshot_handler import DOMSnapshotHandler, DEFAULT_COMPUTED_STYLES


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


def _make_snapshot_result(node_count=5):
    nodes = MagicMock()
    nodes.node_type = list(range(node_count))

    doc = MagicMock()
    doc.nodes = nodes

    result = MagicMock()
    result.documents = [doc]
    result.strings = ["a", "b"]
    return result


# ── enable / disable ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_enable_dom_snapshot_success():
    tab = _make_tab()
    result = await DOMSnapshotHandler.enable_dom_snapshot(tab)
    assert result is True


@pytest.mark.asyncio
async def test_disable_dom_snapshot_success():
    tab = _make_tab()
    result = await DOMSnapshotHandler.disable_dom_snapshot(tab)
    assert result is True


# ── capture_snapshot — default computed_styles ────────────────────────────────

@pytest.mark.asyncio
async def test_capture_snapshot_uses_default_when_none():
    tab = _make_tab()
    tab.send = AsyncMock(return_value=_make_snapshot_result())

    result = await DOMSnapshotHandler.capture_snapshot(tab, computed_styles=None)
    assert "node_count" in result
    # Verify the CDP call was made (tab.send called once)
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_capture_snapshot_uses_default_when_empty_list():
    tab = _make_tab()
    tab.send = AsyncMock(return_value=_make_snapshot_result())

    result = await DOMSnapshotHandler.capture_snapshot(tab, computed_styles=[])
    assert "node_count" in result


# ── capture_snapshot — node_count ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_capture_snapshot_node_count_correct():
    """Property 5 setup: node_count equals len of first doc's node_type list."""
    tab = _make_tab()
    tab.send = AsyncMock(return_value=_make_snapshot_result(node_count=7))

    result = await DOMSnapshotHandler.capture_snapshot(tab)
    assert result["node_count"] == 7


@pytest.mark.asyncio
async def test_capture_snapshot_node_count_zero_when_no_documents():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.documents = []
    mock_result.strings = []
    tab.send = AsyncMock(return_value=mock_result)

    result = await DOMSnapshotHandler.capture_snapshot(tab)
    assert result["node_count"] == 0


@pytest.mark.asyncio
async def test_capture_snapshot_always_has_node_count_key():
    tab = _make_tab()
    tab.send = AsyncMock(return_value=_make_snapshot_result())

    result = await DOMSnapshotHandler.capture_snapshot(tab)
    assert "node_count" in result
    assert "documents" in result
    assert "strings" in result


# ── error handling ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_capture_snapshot_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())
    with pytest.raises(Exception) as exc_info:
        await DOMSnapshotHandler.capture_snapshot(tab)
    assert "timed out" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_capture_snapshot_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))
    with pytest.raises(Exception) as exc_info:
        await DOMSnapshotHandler.capture_snapshot(tab)
    assert "WebSocket" in str(exc_info.value)
