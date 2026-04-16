"""Unit tests for BackgroundServiceHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.backgroundservice_handler import BackgroundServiceHandler, VALID_SERVICE_TYPES


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── start_observing ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_start_observing_valid_service():
    tab = _make_tab()
    result = await BackgroundServiceHandler.start_observing(tab, "backgroundSync")
    assert result is True
    tab.send.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("service", list(VALID_SERVICE_TYPES))
async def test_start_observing_all_valid_types(service):
    tab = _make_tab()
    result = await BackgroundServiceHandler.start_observing(tab, service)
    assert result is True


@pytest.mark.asyncio
async def test_start_observing_invalid_service():
    tab = _make_tab()
    with pytest.raises(ValueError) as exc_info:
        await BackgroundServiceHandler.start_observing(tab, "invalidService")
    assert "Invalid service type" in str(exc_info.value)


@pytest.mark.asyncio
async def test_start_observing_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await BackgroundServiceHandler.start_observing(tab, "backgroundSync")
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_start_observing_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await BackgroundServiceHandler.start_observing(tab, "backgroundSync")
    assert "timed out" in str(exc_info.value).lower()


# ── stop_observing ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_stop_observing_success():
    tab = _make_tab()
    result = await BackgroundServiceHandler.stop_observing(tab, "backgroundSync")
    assert result is True


@pytest.mark.asyncio
async def test_stop_observing_invalid_service():
    tab = _make_tab()
    with pytest.raises(ValueError):
        await BackgroundServiceHandler.stop_observing(tab, "notAService")


# ── get_events ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_events_empty():
    tab = _make_tab()
    # Clear any existing events
    BackgroundServiceHandler._events.clear()

    result = await BackgroundServiceHandler.get_events(tab, "backgroundSync")
    assert isinstance(result, list)
    assert result == []


@pytest.mark.asyncio
async def test_get_events_filters_by_service():
    tab = _make_tab()
    tab_key = str(id(tab))
    BackgroundServiceHandler._events[tab_key] = [
        {"service": "backgroundSync", "data": "event1"},
        {"service": "pushMessaging", "data": "event2"},
    ]

    result = await BackgroundServiceHandler.get_events(tab, "backgroundSync")
    assert len(result) == 1
    assert result[0]["service"] == "backgroundSync"

    # Cleanup
    BackgroundServiceHandler._events.pop(tab_key, None)


# ── clear_events ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_clear_events_success():
    tab = _make_tab()
    result = await BackgroundServiceHandler.clear_events(tab, "backgroundSync")
    assert result is True


@pytest.mark.asyncio
async def test_clear_events_invalid_service():
    tab = _make_tab()
    with pytest.raises(ValueError):
        await BackgroundServiceHandler.clear_events(tab, "notAService")


@pytest.mark.asyncio
async def test_clear_events_removes_from_store():
    tab = _make_tab()
    tab_key = str(id(tab))
    BackgroundServiceHandler._events[tab_key] = [
        {"service": "backgroundSync", "data": "event1"},
        {"service": "pushMessaging", "data": "event2"},
    ]

    await BackgroundServiceHandler.clear_events(tab, "backgroundSync")

    remaining = BackgroundServiceHandler._events.get(tab_key, [])
    assert all(e["service"] != "backgroundSync" for e in remaining)

    # Cleanup
    BackgroundServiceHandler._events.pop(tab_key, None)
