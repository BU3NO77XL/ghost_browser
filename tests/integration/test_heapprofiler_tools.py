"""Integration tests for heapprofiler_management tools module."""

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
    from tools.heapprofiler_management import register
    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func
        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_collect_garbage_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["collect_garbage"]("inst-1")
        assert result is True


@pytest.mark.asyncio
async def test_start_heap_sampling_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["start_heap_sampling"]("inst-1")
        assert result is True


@pytest.mark.asyncio
async def test_start_heap_sampling_custom_interval_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["start_heap_sampling"]("inst-1", sampling_interval=16384)
        assert result is True


@pytest.mark.asyncio
async def test_stop_heap_sampling_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_profile = MagicMock()
    mock_profile.head = None
    mock_profile.samples = []
    mock_result = MagicMock()
    mock_result.profile = mock_profile
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["stop_heap_sampling"]("inst-1")
        assert isinstance(result, dict)
        assert "head" in result
        assert "samples" in result


@pytest.mark.asyncio
async def test_start_tracking_heap_objects_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["start_tracking_heap_objects"]("inst-1")
        assert result is True


@pytest.mark.asyncio
async def test_start_tracking_heap_objects_with_allocations_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["start_tracking_heap_objects"](
            "inst-1", track_allocations=True
        )
        assert result is True


@pytest.mark.asyncio
async def test_stop_tracking_heap_objects_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["stop_tracking_heap_objects"]("inst-1")
        assert result is True


@pytest.mark.asyncio
async def test_get_object_by_heap_id_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
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
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_object_by_heap_id"](
            "inst-1", heap_snapshot_object_id="heap-1"
        )
        assert isinstance(result, dict)
        assert result["type"] == "object"


@pytest.mark.asyncio
async def test_heapprofiler_tool_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["collect_garbage"]("bad-id")
        assert "not found" in str(exc_info.value).lower()
