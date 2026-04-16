"""Integration tests for security_management tools module."""

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
    from tools.security_management import register

    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_get_security_state_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = '{"protocol":"https:","hostname":"example.com","is_secure":true}'
    tab.send = AsyncMock(side_effect=[None, mock_result])
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_security_state"]("inst-1")
        assert isinstance(result, dict)
        assert "security_state" in result


@pytest.mark.asyncio
async def test_set_ignore_certificate_errors_true_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["set_ignore_certificate_errors"]("inst-1", ignore=True)
        assert result is True


@pytest.mark.asyncio
async def test_set_ignore_certificate_errors_false_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["set_ignore_certificate_errors"]("inst-1", ignore=False)
        assert result is True


@pytest.mark.asyncio
async def test_handle_certificate_error_continue_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["handle_certificate_error"](
            "inst-1", event_id=1, action="continue"
        )
        assert result is True


@pytest.mark.asyncio
async def test_handle_certificate_error_cancel_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["handle_certificate_error"]("inst-1", event_id=1, action="cancel")
        assert result is True


@pytest.mark.asyncio
async def test_security_tool_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["get_security_state"]("bad-id")
        assert "not found" in str(exc_info.value).lower()
