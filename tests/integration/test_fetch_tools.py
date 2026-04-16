"""Integration tests for fetch_management tools module."""

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
    from tools.fetch_management import register

    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_fetch_enable_disable_cycle():
    register, mcp, section_tool, registered = _register()
    deps, _ = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result_enable = await registered["fetch_enable"]("inst-1")
        result_disable = await registered["fetch_disable"]("inst-1")
        assert result_enable is True
        assert result_disable is True


@pytest.mark.asyncio
async def test_fetch_enable_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["fetch_enable"]("bad-id")
        assert "Instance not found: bad-id" in str(exc_info.value)
