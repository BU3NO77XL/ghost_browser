"""Unit tests for ProfilerHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.profiler_handler import ProfilerHandler, MAX_PROFILE_NODES


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── enable_profiler ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_enable_profiler_success():
    tab = _make_tab()
    result = await ProfilerHandler.enable_profiler(tab)
    assert result is True


@pytest.mark.asyncio
async def test_enable_profiler_already_enabled():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("already enabled"))
    result = await ProfilerHandler.enable_profiler(tab)
    assert result is True


# ── start_profiling ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_start_profiling_success():
    tab = _make_tab()
    result = await ProfilerHandler.start_profiling(tab)
    assert result is True
    tab.send.assert_called()


@pytest.mark.asyncio
async def test_start_profiling_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await ProfilerHandler.start_profiling(tab)
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_start_profiling_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await ProfilerHandler.start_profiling(tab)
    assert "timed out" in str(exc_info.value).lower()


# ── stop_profiling ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_stop_profiling_success():
    tab = _make_tab()
    mock_frame = MagicMock()
    mock_frame.function_name = "myFunc"
    mock_frame.script_id = "1"
    mock_frame.url = "app.js"
    mock_frame.line_number = 10
    mock_frame.column_number = 0

    mock_node = MagicMock()
    mock_node.id_ = 1
    mock_node.call_frame = mock_frame
    mock_node.hit_count = 5
    mock_node.children = []

    mock_profile = MagicMock()
    mock_profile.nodes = [mock_node]
    mock_profile.start_time = 1000
    mock_profile.end_time = 2000
    mock_profile.samples = [1, 1, 1]
    mock_profile.time_deltas = [100, 100, 100]

    mock_result = MagicMock()
    mock_result.profile = mock_profile
    tab.send = AsyncMock(return_value=mock_result)

    result = await ProfilerHandler.stop_profiling(tab)
    assert isinstance(result, dict)
    assert "nodes" in result
    assert "start_time" in result
    assert "end_time" in result
    assert result["start_time"] == 1000
    assert result["end_time"] == 2000
    assert result["truncated"] is False


@pytest.mark.asyncio
async def test_stop_profiling_truncates_large_profile():
    tab = _make_tab()
    mock_frame = MagicMock()
    mock_frame.function_name = "f"
    mock_frame.script_id = "1"
    mock_frame.url = "app.js"
    mock_frame.line_number = 1
    mock_frame.column_number = 0

    # Create more nodes than MAX_PROFILE_NODES
    nodes = []
    for i in range(MAX_PROFILE_NODES + 10):
        node = MagicMock()
        node.id_ = i
        node.call_frame = mock_frame
        node.hit_count = 1
        node.children = []
        nodes.append(node)

    mock_profile = MagicMock()
    mock_profile.nodes = nodes
    mock_profile.start_time = 0
    mock_profile.end_time = 1000
    mock_profile.samples = []
    mock_profile.time_deltas = []

    mock_result = MagicMock()
    mock_result.profile = mock_profile
    tab.send = AsyncMock(return_value=mock_result)

    result = await ProfilerHandler.stop_profiling(tab)
    assert result["truncated"] is True
    assert len(result["nodes"]) == MAX_PROFILE_NODES
    assert result["total_nodes"] == MAX_PROFILE_NODES + 10


@pytest.mark.asyncio
async def test_stop_profiling_no_profile():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.profile = None
    tab.send = AsyncMock(return_value=mock_result)

    result = await ProfilerHandler.stop_profiling(tab)
    assert result["nodes"] == []


# ── start_precise_coverage ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_start_precise_coverage_default():
    tab = _make_tab()
    result = await ProfilerHandler.start_precise_coverage(tab)
    assert result is True


@pytest.mark.asyncio
async def test_start_precise_coverage_detailed():
    tab = _make_tab()
    result = await ProfilerHandler.start_precise_coverage(tab, call_count=True, detailed=True)
    assert result is True


@pytest.mark.asyncio
async def test_start_precise_coverage_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await ProfilerHandler.start_precise_coverage(tab)
    assert "WebSocket" in str(exc_info.value)


# ── stop_precise_coverage ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_stop_precise_coverage_success():
    tab = _make_tab()
    result = await ProfilerHandler.stop_precise_coverage(tab)
    assert result is True


# ── take_precise_coverage ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_take_precise_coverage_success():
    tab = _make_tab()
    mock_range = MagicMock()
    mock_range.start_offset = 0
    mock_range.end_offset = 100
    mock_range.count = 5

    mock_func = MagicMock()
    mock_func.function_name = "myFunc"
    mock_func.is_block_coverage = False
    mock_func.ranges = [mock_range]

    mock_script = MagicMock()
    mock_script.script_id = "1"
    mock_script.url = "https://example.com/app.js"
    mock_script.functions = [mock_func]

    mock_result = MagicMock()
    mock_result.result = [mock_script]
    mock_result.timestamp = 12345
    tab.send = AsyncMock(return_value=mock_result)

    result = await ProfilerHandler.take_precise_coverage(tab)
    assert isinstance(result, dict)
    assert "scripts" in result
    assert result["total_scripts"] == 1
    assert result["scripts"][0]["url"] == "https://example.com/app.js"


@pytest.mark.asyncio
async def test_take_precise_coverage_with_url_filter():
    tab = _make_tab()
    mock_script1 = MagicMock()
    mock_script1.script_id = "1"
    mock_script1.url = "https://example.com/app.js"
    mock_script1.functions = []

    mock_script2 = MagicMock()
    mock_script2.script_id = "2"
    mock_script2.url = "https://example.com/vendor.js"
    mock_script2.functions = []

    mock_result = MagicMock()
    mock_result.result = [mock_script1, mock_script2]
    mock_result.timestamp = 0
    tab.send = AsyncMock(return_value=mock_result)

    result = await ProfilerHandler.take_precise_coverage(tab, url_filter="app.js")
    assert result["total_scripts"] == 1
    assert result["scripts"][0]["url"] == "https://example.com/app.js"
