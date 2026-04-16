"""Integration tests for profiler_management tools module."""

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
    from tools.profiler_management import register

    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_start_cpu_profiling_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["start_cpu_profiling"]("inst-1")
        assert result is True


@pytest.mark.asyncio
async def test_stop_cpu_profiling_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_profile = MagicMock()
    mock_profile.nodes = []
    mock_profile.start_time = 0
    mock_profile.end_time = 1000
    mock_profile.samples = []
    mock_profile.time_deltas = []
    mock_result = MagicMock()
    mock_result.profile = mock_profile
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["stop_cpu_profiling"]("inst-1")
        assert isinstance(result, dict)
        assert "nodes" in result
        assert "start_time" in result


@pytest.mark.asyncio
async def test_start_code_coverage_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["start_code_coverage"]("inst-1")
        assert result is True


@pytest.mark.asyncio
async def test_start_code_coverage_detailed_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["start_code_coverage"]("inst-1", call_count=True, detailed=True)
        assert result is True


@pytest.mark.asyncio
async def test_stop_code_coverage_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["stop_code_coverage"]("inst-1")
        assert result is True


@pytest.mark.asyncio
async def test_take_code_coverage_snapshot_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.result = []
    mock_result.timestamp = 0
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["take_code_coverage_snapshot"]("inst-1")
        assert isinstance(result, dict)
        assert "scripts" in result
        assert "total_scripts" in result


@pytest.mark.asyncio
async def test_take_code_coverage_snapshot_with_filter_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.result = []
    mock_result.timestamp = 0
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["take_code_coverage_snapshot"]("inst-1", url_filter="app.js")
        assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_profiler_tool_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["start_cpu_profiling"]("bad-id")
        assert "not found" in str(exc_info.value).lower()
