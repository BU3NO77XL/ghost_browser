"""Integration tests for dom_snapshot_management tools module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_snapshot_result(node_count=5):
    nodes = MagicMock()
    nodes.node_type = list(range(node_count))
    doc = MagicMock()
    doc.nodes = nodes
    result = MagicMock()
    result.documents = [doc]
    result.strings = []
    return result


def _make_deps(tab=None):
    if tab is None:
        tab = AsyncMock()
        tab.send = AsyncMock(return_value=None)
    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=tab)
    return {"browser_manager": bm}, tab


def _register():
    from tools.dom_snapshot_management import register
    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func
        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_dom_snapshot_capture_twice_same_node_count():
    """Property 5: two captures on same page return equal node_count."""
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    tab.send = AsyncMock(side_effect=[
        _make_snapshot_result(10),
        _make_snapshot_result(10),
    ])
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        r1 = await registered["dom_snapshot_capture"]("inst-1")
        r2 = await registered["dom_snapshot_capture"]("inst-1")
        assert r1["node_count"] == r2["node_count"]


@pytest.mark.asyncio
async def test_dom_snapshot_capture_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["dom_snapshot_capture"]("bad-id")
        assert "Instance not found: bad-id" in str(exc_info.value)
