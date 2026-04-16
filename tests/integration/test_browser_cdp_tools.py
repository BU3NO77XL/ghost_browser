"""Integration tests for browser_cdp_management tools module."""

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
    from tools.browser_cdp_management import register

    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_browser_get_window_for_target_then_set_then_get():
    """Property 4 setup: get → set → get round-trip."""
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_bounds = MagicMock()
    mock_bounds.left = 0
    mock_bounds.top = 0
    mock_bounds.width = 1280
    mock_bounds.height = 720
    mock_bounds.window_state = "normal"

    # get_window_for_target returns (window_id, bounds)
    tab.send = AsyncMock(
        side_effect=[
            (1, mock_bounds),  # get_window_for_target
            None,  # set_window_bounds
            mock_bounds,  # get_window_bounds
        ]
    )
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        info = await registered["browser_get_window_for_target"]("inst-1")
        assert "window_id" in info

        set_result = await registered["browser_set_window_bounds"](
            "inst-1", 1, {"left": 0, "top": 0, "width": 1280, "height": 720}
        )
        assert set_result is True

        bounds = await registered["browser_get_window_bounds"]("inst-1", 1)
        assert "width" in bounds


@pytest.mark.asyncio
async def test_browser_get_window_for_target_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["browser_get_window_for_target"]("bad-id")
        assert "Instance not found: bad-id" in str(exc_info.value)
