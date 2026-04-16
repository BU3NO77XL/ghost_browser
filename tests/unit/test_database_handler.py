"""Unit tests for DatabaseHandler."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.database_handler import DatabaseHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


def _make_js_result(value):
    """Helper to create a mock JS evaluation result."""
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = value
    return mock_result


# ── enable_database_domain ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_enable_database_domain_is_noop():
    """enable_database_domain is a no-op (WebSQL uses JS)."""
    tab = _make_tab()
    await DatabaseHandler.enable_database_domain(tab)
    tab.send.assert_not_called()


# ── list_databases ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_databases_returns_list():
    tab = _make_tab()
    tab.send = AsyncMock(return_value=_make_js_result("[]"))

    result = await DatabaseHandler.list_databases(tab)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_databases_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await DatabaseHandler.list_databases(tab)
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_databases_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await DatabaseHandler.list_databases(tab)
    assert "timed out" in str(exc_info.value).lower()


# ── get_table_names ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_table_names_returns_list():
    tab = _make_tab()
    tab.send = AsyncMock(return_value=_make_js_result('["users", "products"]'))

    result = await DatabaseHandler.get_table_names(tab, "myDB")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_table_names_empty():
    tab = _make_tab()
    tab.send = AsyncMock(return_value=_make_js_result("[]"))

    result = await DatabaseHandler.get_table_names(tab, "myDB")
    assert result == []


@pytest.mark.asyncio
async def test_get_table_names_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await DatabaseHandler.get_table_names(tab, "myDB")
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_table_names_serializes_database_id_as_js_string():
    tab = _make_tab()
    tab.send = AsyncMock(return_value=_make_js_result("[]"))
    captured = {}

    def fake_evaluate(**kwargs):
        captured.update(kwargs)
        return "runtime-evaluate-command"

    with patch("core.database_handler.cdp.runtime.evaluate", side_effect=fake_evaluate):
        await DatabaseHandler.get_table_names(tab, "bad'id")

    assert 'openDatabase("bad\'id"' in captured["expression"]
    assert "openDatabase('bad'id'" not in captured["expression"]


# ── execute_sql ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_execute_sql_returns_dict():
    tab = _make_tab()
    payload = json.dumps(
        {"columns": ["id", "name"], "rows": [[1, "Alice"], [2, "Bob"]], "sql_error": None}
    )
    tab.send = AsyncMock(return_value=_make_js_result(payload))

    result = await DatabaseHandler.execute_sql(tab, "myDB", "SELECT * FROM users")
    assert isinstance(result, dict)
    assert "columns" in result
    assert "rows" in result
    assert "sql_error" in result


@pytest.mark.asyncio
async def test_execute_sql_with_error_returns_dict():
    tab = _make_tab()
    payload = json.dumps(
        {"columns": [], "rows": [], "sql_error": {"code": 1, "message": "no such table: users"}}
    )
    tab.send = AsyncMock(return_value=_make_js_result(payload))

    result = await DatabaseHandler.execute_sql(tab, "myDB", "SELECT * FROM users")
    assert isinstance(result, dict)
    assert "sql_error" in result


@pytest.mark.asyncio
async def test_execute_sql_with_args_returns_dict():
    tab = _make_tab()
    payload = json.dumps({"columns": ["id"], "rows": [[42]], "sql_error": None})
    tab.send = AsyncMock(return_value=_make_js_result(payload))

    result = await DatabaseHandler.execute_sql(
        tab, "myDB", "SELECT id FROM users WHERE id = ?", [42]
    )
    assert isinstance(result, dict)
    assert "columns" in result


@pytest.mark.asyncio
async def test_execute_sql_serializes_database_id_as_js_string():
    tab = _make_tab()
    payload = json.dumps({"columns": [], "rows": [], "sql_error": None})
    tab.send = AsyncMock(return_value=_make_js_result(payload))
    captured = {}

    def fake_evaluate(**kwargs):
        captured.update(kwargs)
        return "runtime-evaluate-command"

    with patch("core.database_handler.cdp.runtime.evaluate", side_effect=fake_evaluate):
        await DatabaseHandler.execute_sql(tab, "bad'id", "SELECT 1")

    assert 'openDatabase("bad\'id"' in captured["expression"]
    assert "openDatabase('bad'id'" not in captured["expression"]


@pytest.mark.asyncio
async def test_execute_sql_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await DatabaseHandler.execute_sql(tab, "myDB", "SELECT 1")
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_execute_sql_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await DatabaseHandler.execute_sql(tab, "myDB", "SELECT 1")
    assert "timed out" in str(exc_info.value).lower()
