"""Unit tests for AnimationHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.animation_handler import AnimationHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── list_animations ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_animations_empty():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = "[]"
    tab.send = AsyncMock(side_effect=[None, mock_result])

    result = await AnimationHandler.list_animations(tab)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_animations_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await AnimationHandler.list_animations(tab)
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_animations_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await AnimationHandler.list_animations(tab)
    assert "timed out" in str(exc_info.value).lower()


# ── pause_animation ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pause_animation_success():
    tab = _make_tab()
    result = await AnimationHandler.pause_animation(tab, "anim-0")
    assert result is True
    tab.send.assert_called()


@pytest.mark.asyncio
async def test_pause_animation_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await AnimationHandler.pause_animation(tab, "anim-0")
    assert "WebSocket" in str(exc_info.value)


# ── play_animation ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_play_animation_success():
    tab = _make_tab()
    result = await AnimationHandler.play_animation(tab, "anim-0")
    assert result is True


@pytest.mark.asyncio
async def test_play_animation_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await AnimationHandler.play_animation(tab, "anim-0")
    assert "timed out" in str(exc_info.value).lower()


# ── set_playback_rate ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_set_playback_rate_normal():
    tab = _make_tab()
    result = await AnimationHandler.set_playback_rate(tab, 1.0)
    assert result is True


@pytest.mark.asyncio
async def test_set_playback_rate_slow():
    tab = _make_tab()
    result = await AnimationHandler.set_playback_rate(tab, 0.1)
    assert result is True


@pytest.mark.asyncio
async def test_set_playback_rate_fast():
    tab = _make_tab()
    result = await AnimationHandler.set_playback_rate(tab, 5.0)
    assert result is True


@pytest.mark.asyncio
async def test_set_playback_rate_paused():
    tab = _make_tab()
    result = await AnimationHandler.set_playback_rate(tab, 0.0)
    assert result is True


@pytest.mark.asyncio
async def test_set_playback_rate_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await AnimationHandler.set_playback_rate(tab, 1.0)
    assert "WebSocket" in str(exc_info.value)


# ── seek_animation ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_seek_animation_success():
    tab = _make_tab()
    result = await AnimationHandler.seek_animation(tab, ["anim-0", "anim-1"], 500.0)
    assert result is True


@pytest.mark.asyncio
async def test_seek_animation_single():
    tab = _make_tab()
    result = await AnimationHandler.seek_animation(tab, ["anim-0"], 0.0)
    assert result is True


@pytest.mark.asyncio
async def test_seek_animation_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await AnimationHandler.seek_animation(tab, ["anim-0"], 100.0)
    assert "timed out" in str(exc_info.value).lower()


# ── get_animation_timing ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_animation_timing_success():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.current_time = 250.0
    tab.send = AsyncMock(side_effect=[None, mock_result])

    result = await AnimationHandler.get_animation_timing(tab, "anim-0")
    assert isinstance(result, dict)
    assert result["animation_id"] == "anim-0"
    assert result["current_time"] == 250.0


@pytest.mark.asyncio
async def test_get_animation_timing_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await AnimationHandler.get_animation_timing(tab, "anim-0")
    assert "WebSocket" in str(exc_info.value)
