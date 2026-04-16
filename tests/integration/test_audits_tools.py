"""Integration tests for audits_management tools module."""

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
    from tools.audits_management import register

    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_audits_enable_disable_cycle():
    register, mcp, section_tool, registered = _register()
    deps, _ = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        assert await registered["audits_enable"]("inst-1") is True
        assert await registered["audits_disable"]("inst-1") is True


@pytest.mark.asyncio
async def test_audits_get_encoded_response_invalid_encoding_raises():
    register, mcp, section_tool, registered = _register()
    deps, _ = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(ValueError):
            await registered["audits_get_encoded_response"]("inst-1", "req-1", "gif")


@pytest.mark.asyncio
async def test_audits_enable_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["audits_enable"]("bad-id")
        assert "Instance not found: bad-id" in str(exc_info.value)
