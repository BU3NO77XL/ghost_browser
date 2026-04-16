"""Integration tests for serviceworker_management tools module."""

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
    from tools.serviceworker_management import register

    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_list_service_workers_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = []
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["list_service_workers"]("inst-1")
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_unregister_service_worker_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["unregister_service_worker"](
            "inst-1", scope_url="https://example.com/"
        )
        assert result is True


@pytest.mark.asyncio
async def test_force_update_service_worker_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["force_update_service_worker"](
            "inst-1", scope_url="https://example.com/"
        )
        assert result is True


@pytest.mark.asyncio
async def test_deliver_push_message_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["deliver_push_message"](
            "inst-1",
            origin="https://example.com",
            registration_id="reg-123",
            data='{"title": "Test"}',
        )
        assert result is True


@pytest.mark.asyncio
async def test_dispatch_sync_event_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["dispatch_sync_event"](
            "inst-1", origin="https://example.com", registration_id="reg-123", tag="sync-messages"
        )
        assert result is True


@pytest.mark.asyncio
async def test_skip_waiting_service_worker_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["skip_waiting_service_worker"](
            "inst-1", scope_url="https://example.com/"
        )
        assert result is True


@pytest.mark.asyncio
async def test_set_service_worker_force_update_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["set_service_worker_force_update"]("inst-1", force_update=True)
        assert result is True


@pytest.mark.asyncio
async def test_serviceworker_tool_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["list_service_workers"]("bad-id")
        assert "not found" in str(exc_info.value).lower()
