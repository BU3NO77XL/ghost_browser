"""Integration tests for database_management tools module."""

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
    from tools.database_management import register
    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func
        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_list_websql_databases_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = "[]"
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["list_websql_databases"]("inst-1")
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_websql_table_names_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = '["users", "products"]'
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_websql_table_names"]("inst-1", database_id="myDB")
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_execute_websql_query_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    import json
    payload = json.dumps({"columns": ["id", "name"], "rows": [[1, "Alice"]], "sql_error": None})
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = payload
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["execute_websql_query"](
            "inst-1", database_id="myDB", query="SELECT * FROM users"
        )
        assert isinstance(result, dict)
        assert "columns" in result


@pytest.mark.asyncio
async def test_execute_websql_query_with_args_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    import json
    payload = json.dumps({"columns": ["id"], "rows": [[42]], "sql_error": None})
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = payload
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["execute_websql_query"](
            "inst-1", database_id="myDB",
            query="SELECT id FROM users WHERE id = ?",
            query_args=[42]
        )
        assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_database_tool_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["list_websql_databases"]("bad-id")
        assert "not found" in str(exc_info.value).lower()
