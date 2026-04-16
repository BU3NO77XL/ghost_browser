"""Integration tests for backgroundservice_management tools module."""

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
    from tools.backgroundservice_management import register

    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_start_observing_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["start_observing_background_service"](
            "inst-1", service="backgroundSync"
        )
        assert result is True


@pytest.mark.asyncio
async def test_stop_observing_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["stop_observing_background_service"](
            "inst-1", service="backgroundSync"
        )
        assert result is True


@pytest.mark.asyncio
async def test_get_events_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_background_service_events"](
            "inst-1", service="backgroundSync"
        )
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_clear_events_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["clear_background_service_events"](
            "inst-1", service="backgroundSync"
        )
        assert result is True


@pytest.mark.asyncio
async def test_start_observing_invalid_service_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception):
            await registered["start_observing_background_service"]("inst-1", service="notAService")


@pytest.mark.asyncio
async def test_backgroundservice_tool_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["start_observing_background_service"](
                "bad-id", service="backgroundSync"
            )
        assert "not found" in str(exc_info.value).lower()
