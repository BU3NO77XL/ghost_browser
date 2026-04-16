"""Unit tests for TargetHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.target_handler import TargetHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


def _make_target(
    target_id="t-1",
    type_="page",
    title="Test",
    url="https://example.com",
    attached=False,
    opener_id=None,
):
    t = MagicMock()
    t.target_id = target_id
    t.type_ = type_
    t.type = type_
    t.title = title
    t.url = url
    t.attached = attached
    t.opener_id = opener_id
    return t


# ── get_targets ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_targets_filters_browser_type():
    """Property 3 setup: browser-type targets must be excluded."""
    tab = _make_tab()
    targets = [
        _make_target("t-1", "page"),
        _make_target("t-2", "browser"),  # should be filtered out
        _make_target("t-3", "worker"),
    ]
    tab.send = AsyncMock(return_value=targets)

    result = await TargetHandler.get_targets(tab)
    assert len(result) == 2
    types = [r["type"] for r in result]
    assert "browser" not in types


@pytest.mark.asyncio
async def test_get_targets_returns_correct_fields():
    tab = _make_tab()
    tab.send = AsyncMock(return_value=[_make_target("t-1", "page")])

    result = await TargetHandler.get_targets(tab)
    assert result[0]["target_id"] == "t-1"
    assert result[0]["type"] == "page"
    assert "title" in result[0]
    assert "url" in result[0]
    assert "attached" in result[0]


# ── get_target_info ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_target_info_returns_matching_target_id():
    """Property 3: returned target_id must equal the input target_id."""
    tab = _make_tab()
    tab.send = AsyncMock(return_value=_make_target("t-42", "page"))

    result = await TargetHandler.get_target_info(tab, "t-42")
    assert result["target_id"] == "t-42"


# ── create_target ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_target_extracts_string_target_id():
    tab = _make_tab()
    mock_target_id = MagicMock()
    mock_target_id.__str__ = MagicMock(return_value="new-target-id")
    tab.send = AsyncMock(return_value=mock_target_id)

    result = await TargetHandler.create_target(tab, "https://example.com")
    assert isinstance(result["target_id"], str)


# ── error handling ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_targets_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())
    with pytest.raises(Exception) as exc_info:
        await TargetHandler.get_targets(tab)
    assert "timed out" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_targets_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))
    with pytest.raises(Exception) as exc_info:
        await TargetHandler.get_targets(tab)
    assert "WebSocket" in str(exc_info.value)
