"""Integration tests for storage_management tools module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_deps(tab=None):
    if tab is None:
        tab = AsyncMock()
        tab.send = AsyncMock(return_value=None)
    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=tab)
    return {"browser_manager": bm}, tab


def _make_mcp_and_section_tool():
    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return mcp, section_tool, registered


@pytest.fixture
def storage_tools():
    from tools.storage_management import register

    mcp, section_tool, registered = _make_mcp_and_section_tool()
    deps, _ = _make_deps()
    register(mcp, section_tool, deps)
    return registered, deps


# ── LocalStorage ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_local_storage_tool():
    from tools.storage_management import register

    mcp, section_tool, registered = _make_mcp_and_section_tool()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.entries = [["k1", "v1"]]
    tab.send = AsyncMock(return_value=mock_result)

    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_local_storage"]("inst-1", origin="https://example.com")
        assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_set_local_storage_item_tool():
    from tools.storage_management import register

    mcp, section_tool, registered = _make_mcp_and_section_tool()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["set_local_storage_item"](
            "inst-1", origin="https://example.com", key="k", value="v"
        )
        assert result is True


@pytest.mark.asyncio
async def test_remove_local_storage_item_tool():
    from tools.storage_management import register

    mcp, section_tool, registered = _make_mcp_and_section_tool()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["remove_local_storage_item"](
            "inst-1", origin="https://example.com", key="k"
        )
        assert result is True


@pytest.mark.asyncio
async def test_clear_local_storage_tool():
    from tools.storage_management import register

    mcp, section_tool, registered = _make_mcp_and_section_tool()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["clear_local_storage"]("inst-1", origin="https://example.com")
        assert result is True


# ── SessionStorage ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_session_storage_tool():
    from tools.storage_management import register

    mcp, section_tool, registered = _make_mcp_and_section_tool()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.entries = []
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_session_storage"]("inst-1", origin="https://example.com")
        assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_set_session_storage_item_tool():
    from tools.storage_management import register

    mcp, section_tool, registered = _make_mcp_and_section_tool()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["set_session_storage_item"](
            "inst-1", origin="https://example.com", key="sk", value="sv"
        )
        assert result is True


# ── IndexedDB ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_indexed_databases_tool():
    from tools.storage_management import register
    from core.storage_handler import StorageHandler

    mcp, section_tool, registered = _make_mcp_and_section_tool()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.database_names = []
    tab.send = AsyncMock(side_effect=[None, mock_result])

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=tab)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", new=AsyncMock(return_value=None)):
        with patch.object(StorageHandler, "list_indexed_databases", new=AsyncMock(return_value=[])):
            register(mcp, section_tool, deps)
            result = await registered["list_indexed_databases"](
                "inst-1", origin="https://example.com"
            )
            assert isinstance(result, list)


@pytest.mark.asyncio
async def test_delete_indexed_database_tool():
    from tools.storage_management import register

    mcp, section_tool, registered = _make_mcp_and_section_tool()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["delete_indexed_database"](
            "inst-1", origin="https://example.com", database_name="myDB"
        )
        assert result is True


# ── Cache Storage ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_cache_storage_tool():
    from tools.storage_management import register

    mcp, section_tool, registered = _make_mcp_and_section_tool()

    tab = AsyncMock()
    tab.send = AsyncMock(return_value=[])
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["list_cache_storage"](
            "inst-1", security_origin="https://example.com"
        )
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_delete_cache_tool():
    from tools.storage_management import register

    mcp, section_tool, registered = _make_mcp_and_section_tool()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["delete_cache"](
            "inst-1", security_origin="https://example.com", cache_name="api-cache"
        )
        assert result is True


# ── Error handling ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_tool_instance_not_found():
    from tools.storage_management import register

    mcp, section_tool, registered = _make_mcp_and_section_tool()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["get_local_storage"]("bad-id", origin="https://example.com")
        assert "not found" in str(exc_info.value).lower()
