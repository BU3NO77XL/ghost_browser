"""Unit tests for ServiceWorkerHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.serviceworker_handler import ServiceWorkerHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── list_service_workers ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_service_workers_empty():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = []
    tab.send = AsyncMock(return_value=mock_result)

    result = await ServiceWorkerHandler.list_service_workers(tab)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_service_workers_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await ServiceWorkerHandler.list_service_workers(tab)
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_service_workers_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await ServiceWorkerHandler.list_service_workers(tab)
    assert "timed out" in str(exc_info.value).lower()


# ── unregister_service_worker ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_unregister_service_worker_success():
    tab = _make_tab()
    result = await ServiceWorkerHandler.unregister_service_worker(tab, "https://example.com/")
    assert result is True
    tab.send.assert_called()


@pytest.mark.asyncio
async def test_unregister_service_worker_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await ServiceWorkerHandler.unregister_service_worker(tab, "https://example.com/")
    assert "WebSocket" in str(exc_info.value)


# ── force_update_service_worker ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_force_update_service_worker_success():
    tab = _make_tab()
    result = await ServiceWorkerHandler.force_update_service_worker(tab, "https://example.com/")
    assert result is True


@pytest.mark.asyncio
async def test_force_update_service_worker_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await ServiceWorkerHandler.force_update_service_worker(tab, "https://example.com/")
    assert "timed out" in str(exc_info.value).lower()


# ── deliver_push_message ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_deliver_push_message_success():
    tab = _make_tab()
    result = await ServiceWorkerHandler.deliver_push_message(
        tab, "https://example.com", "reg-123", '{"title": "Test"}'
    )
    assert result is True


@pytest.mark.asyncio
async def test_deliver_push_message_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await ServiceWorkerHandler.deliver_push_message(
            tab, "https://example.com", "reg-123", "data"
        )
    assert "WebSocket" in str(exc_info.value)


# ── dispatch_sync_event ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_dispatch_sync_event_success():
    tab = _make_tab()
    result = await ServiceWorkerHandler.dispatch_sync_event(
        tab, "https://example.com", "reg-123", "sync-messages"
    )
    assert result is True


@pytest.mark.asyncio
async def test_dispatch_sync_event_last_chance():
    tab = _make_tab()
    result = await ServiceWorkerHandler.dispatch_sync_event(
        tab, "https://example.com", "reg-123", "sync-messages", last_chance=True
    )
    assert result is True


# ── skip_waiting ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_skip_waiting_success():
    tab = _make_tab()
    result = await ServiceWorkerHandler.skip_waiting(tab, "https://example.com/")
    assert result is True


# ── set_force_update_on_page_load ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_set_force_update_on_page_load_true():
    tab = _make_tab()
    result = await ServiceWorkerHandler.set_force_update_on_page_load(tab, True)
    assert result is True


@pytest.mark.asyncio
async def test_set_force_update_on_page_load_false():
    tab = _make_tab()
    result = await ServiceWorkerHandler.set_force_update_on_page_load(tab, False)
    assert result is True
