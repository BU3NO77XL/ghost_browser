"""Integration tests for animation_management tools module."""

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
    from tools.animation_management import register
    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func
        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_list_animations_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = "[]"
    tab.send = AsyncMock(side_effect=[None, mock_result])
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["list_animations"]("inst-1")
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_pause_animation_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["pause_animation"]("inst-1", animation_id="anim-0")
        assert result is True


@pytest.mark.asyncio
async def test_play_animation_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["play_animation"]("inst-1", animation_id="anim-0")
        assert result is True


@pytest.mark.asyncio
async def test_set_animation_playback_rate_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["set_animation_playback_rate"]("inst-1", playback_rate=0.5)
        assert result is True


@pytest.mark.asyncio
async def test_seek_animations_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["seek_animations"](
            "inst-1", animation_ids=["anim-0"], current_time=500.0
        )
        assert result is True


@pytest.mark.asyncio
async def test_get_animation_timing_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.current_time = 250.0
    tab.send = AsyncMock(side_effect=[None, mock_result])
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_animation_timing"]("inst-1", animation_id="anim-0")
        assert isinstance(result, dict)
        assert result["current_time"] == 250.0


@pytest.mark.asyncio
async def test_animation_tool_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["list_animations"]("bad-id")
        assert "not found" in str(exc_info.value).lower()
