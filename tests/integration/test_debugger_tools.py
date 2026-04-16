"""Integration tests for debugger_management tools module."""

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
    from tools.debugger_management import register

    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_enable_debugger_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.debugger_id = "dbg-1"
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["enable_debugger"]("inst-1")
        assert isinstance(result, str)


@pytest.mark.asyncio
async def test_disable_debugger_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["disable_debugger"]("inst-1")
        assert result is True


@pytest.mark.asyncio
async def test_set_breakpoint_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.breakpoint_id = "bp-1"
    mock_result.locations = []
    tab.send = AsyncMock(side_effect=[None, mock_result])
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["set_breakpoint"]("inst-1", url="app.js", line_number=42)
        assert result["breakpoint_id"] == "bp-1"


@pytest.mark.asyncio
async def test_remove_breakpoint_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["remove_breakpoint"]("inst-1", breakpoint_id="bp-1")
        assert result is True


@pytest.mark.asyncio
async def test_resume_execution_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["resume_execution"]("inst-1")
        assert result is True


@pytest.mark.asyncio
async def test_step_over_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["step_over"]("inst-1")
        assert result is True


@pytest.mark.asyncio
async def test_step_into_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["step_into"]("inst-1")
        assert result is True


@pytest.mark.asyncio
async def test_get_call_stack_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = "Error\n    at foo (app.js:10)"
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_call_stack"]("inst-1")
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_debugger_tool_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["enable_debugger"]("bad-id")
        assert "not found" in str(exc_info.value).lower()
