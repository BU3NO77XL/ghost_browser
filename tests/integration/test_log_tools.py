"""Integration tests for log_management tools module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_deps(tab=None):
    if tab is None:
        tab = AsyncMock()
        tab.send = AsyncMock(return_value=None)
    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=tab)
    return {"browser_manager": bm}, tab


def _register():
    from tools.log_management import register

    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_log_enable_disable_cycle():
    register, mcp, section_tool, registered = _register()
    deps, _ = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result_enable = await registered["log_enable"]("inst-1")
        result_disable = await registered["log_disable"]("inst-1")
        assert result_enable is True
        assert result_disable is True


@pytest.mark.asyncio
async def test_log_clear():
    register, mcp, section_tool, registered = _register()
    deps, _ = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["log_clear"]("inst-1")
        assert result is True


@pytest.mark.asyncio
async def test_log_start_stop_violations_report():
    register, mcp, section_tool, registered = _register()
    deps, _ = _make_deps()
    settings = [{"name": "longTask", "threshold": 200.0}]

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result_start = await registered["log_start_violations_report"]("inst-1", settings)
        result_stop = await registered["log_stop_violations_report"]("inst-1")
        assert result_start is True
        assert result_stop is True


@pytest.mark.asyncio
async def test_log_enable_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["log_enable"]("bad-id")
        assert "Instance not found: bad-id" in str(exc_info.value)
