"""Integration tests for target_management tools module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_target(target_id="t-1", type_="page"):
    t = MagicMock()
    t.target_id = target_id
    t.type_ = type_
    t.type = type_
    t.title = "Test"
    t.url = "https://example.com"
    t.attached = False
    t.opener_id = None
    return t


def _make_deps(tab=None):
    if tab is None:
        tab = AsyncMock()
        tab.send = AsyncMock(return_value=None)
    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=tab)
    return {"browser_manager": bm}, tab


def _register():
    from tools.target_management import register

    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_target_get_targets_no_browser_type():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    tab.send = AsyncMock(
        return_value=[
            _make_target("t-1", "page"),
            _make_target("t-2", "browser"),
        ]
    )
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["target_get_targets"]("inst-1")
        types = [r["type"] for r in result]
        assert "browser" not in types


@pytest.mark.asyncio
async def test_target_get_targets_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["target_get_targets"]("bad-id")
        assert "Instance not found: bad-id" in str(exc_info.value)
