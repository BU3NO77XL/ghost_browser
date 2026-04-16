"""Integration tests for system_info_management tools module."""

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
    from tools.system_info_management import register
    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func
        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_system_info_get_info_response_structure():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.gpu = MagicMock()
    mock_result.model_name = "Test"
    mock_result.command_line = "--headless"
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["system_info_get_info"]("inst-1")
        assert "gpu" in result
        assert "model_name" in result
        assert "command_line" in result


@pytest.mark.asyncio
async def test_system_info_get_info_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["system_info_get_info"]("bad-id")
        assert "Instance not found: bad-id" in str(exc_info.value)
