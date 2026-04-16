"""Unit tests for HeapProfilerHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.heapprofiler_handler import HeapProfilerHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── enable_heap_profiler ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_enable_heap_profiler_success():
    tab = _make_tab()
    result = await HeapProfilerHandler.enable_heap_profiler(tab)
    assert result is True


@pytest.mark.asyncio
async def test_enable_heap_profiler_already_enabled():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("already enabled"))
    result = await HeapProfilerHandler.enable_heap_profiler(tab)
    assert result is True


# ── collect_garbage ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_collect_garbage_success():
    tab = _make_tab()
    result = await HeapProfilerHandler.collect_garbage(tab)
    assert result is True
    tab.send.assert_called()


@pytest.mark.asyncio
async def test_collect_garbage_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await HeapProfilerHandler.collect_garbage(tab)
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_collect_garbage_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await HeapProfilerHandler.collect_garbage(tab)
    assert "timed out" in str(exc_info.value).lower()


# ── start_sampling ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_start_sampling_default_interval():
    tab = _make_tab()
    result = await HeapProfilerHandler.start_sampling(tab)
    assert result is True


@pytest.mark.asyncio
async def test_start_sampling_custom_interval():
    tab = _make_tab()
    result = await HeapProfilerHandler.start_sampling(tab, sampling_interval=16384)
    assert result is True


@pytest.mark.asyncio
async def test_start_sampling_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await HeapProfilerHandler.start_sampling(tab)
    assert "WebSocket" in str(exc_info.value)


# ── stop_sampling ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_stop_sampling_success():
    tab = _make_tab()
    mock_frame = MagicMock()
    mock_frame.function_name = "allocate"
    mock_frame.url = "app.js"

    mock_head = MagicMock()
    mock_head.call_frame = mock_frame
    mock_head.self_size = 1024
    mock_head.children = []

    mock_sample = MagicMock()
    mock_sample.node_id = 1
    mock_sample.ordinal = 0
    mock_sample.size = 512

    mock_profile = MagicMock()
    mock_profile.head = mock_head
    mock_profile.samples = [mock_sample]

    mock_result = MagicMock()
    mock_result.profile = mock_profile
    tab.send = AsyncMock(return_value=mock_result)

    result = await HeapProfilerHandler.stop_sampling(tab)
    assert isinstance(result, dict)
    assert "head" in result
    assert "samples" in result
    assert result["head"]["name"] == "allocate"
    assert len(result["samples"]) == 1


@pytest.mark.asyncio
async def test_stop_sampling_no_profile():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.profile = None
    tab.send = AsyncMock(return_value=mock_result)

    result = await HeapProfilerHandler.stop_sampling(tab)
    assert result == {"head": None, "samples": []}


@pytest.mark.asyncio
async def test_stop_sampling_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await HeapProfilerHandler.stop_sampling(tab)
    assert "WebSocket" in str(exc_info.value)


# ── start_tracking_heap_objects ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_start_tracking_heap_objects_default():
    tab = _make_tab()
    result = await HeapProfilerHandler.start_tracking_heap_objects(tab)
    assert result is True


@pytest.mark.asyncio
async def test_start_tracking_heap_objects_with_allocations():
    tab = _make_tab()
    result = await HeapProfilerHandler.start_tracking_heap_objects(tab, track_allocations=True)
    assert result is True


@pytest.mark.asyncio
async def test_start_tracking_heap_objects_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await HeapProfilerHandler.start_tracking_heap_objects(tab)
    assert "WebSocket" in str(exc_info.value)


# ── stop_tracking_heap_objects ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_stop_tracking_heap_objects_success():
    tab = _make_tab()
    result = await HeapProfilerHandler.stop_tracking_heap_objects(tab)
    assert result is True


@pytest.mark.asyncio
async def test_stop_tracking_heap_objects_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await HeapProfilerHandler.stop_tracking_heap_objects(tab)
    assert "timed out" in str(exc_info.value).lower()


# ── get_object_by_heap_id ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_object_by_heap_id_success():
    tab = _make_tab()
    mock_type = MagicMock()
    mock_type.value = "object"

    mock_obj = MagicMock()
    mock_obj.type_ = mock_type
    mock_obj.value = None
    mock_obj.description = "Object"
    mock_obj.object_id = "obj-1"

    mock_result = MagicMock()
    mock_result.result = mock_obj
    tab.send = AsyncMock(return_value=mock_result)

    result = await HeapProfilerHandler.get_object_by_heap_id(tab, "heap-obj-1")
    assert isinstance(result, dict)
    assert result["type"] == "object"
    assert result["description"] == "Object"


@pytest.mark.asyncio
async def test_get_object_by_heap_id_not_found():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.result = None
    tab.send = AsyncMock(return_value=mock_result)

    result = await HeapProfilerHandler.get_object_by_heap_id(tab, "nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_get_object_by_heap_id_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await HeapProfilerHandler.get_object_by_heap_id(tab, "heap-obj-1")
    assert "WebSocket" in str(exc_info.value)
