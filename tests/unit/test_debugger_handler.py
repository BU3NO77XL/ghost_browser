"""Unit tests for DebuggerHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.debugger_handler import DebuggerHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── enable_debugger ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_enable_debugger_success():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.debugger_id = "dbg-123"
    tab.send = AsyncMock(return_value=mock_result)

    result = await DebuggerHandler.enable_debugger(tab)
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_enable_debugger_already_enabled():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("already enabled"))
    result = await DebuggerHandler.enable_debugger(tab)
    assert result == ""


# ── disable_debugger ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_disable_debugger_success():
    tab = _make_tab()
    result = await DebuggerHandler.disable_debugger(tab)
    assert result is True


@pytest.mark.asyncio
async def test_disable_debugger_not_enabled():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("not enabled"))
    result = await DebuggerHandler.disable_debugger(tab)
    assert result is True


# ── set_breakpoint ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_set_breakpoint_success():
    tab = _make_tab()
    mock_loc = MagicMock()
    mock_loc.script_id = "script-1"
    mock_loc.line_number = 42
    mock_loc.column_number = 0

    mock_result = MagicMock()
    mock_result.breakpoint_id = "bp-1"
    mock_result.locations = [mock_loc]
    tab.send = AsyncMock(side_effect=[None, mock_result])

    result = await DebuggerHandler.set_breakpoint(tab, "app.js", 42)
    assert result["breakpoint_id"] == "bp-1"
    assert len(result["locations"]) == 1
    assert result["locations"][0]["line_number"] == 42


@pytest.mark.asyncio
async def test_set_breakpoint_with_condition():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.breakpoint_id = "bp-cond"
    mock_result.locations = []
    tab.send = AsyncMock(side_effect=[None, mock_result])

    result = await DebuggerHandler.set_breakpoint(
        tab, "app.js", 10, condition="x > 5"
    )
    assert result["breakpoint_id"] == "bp-cond"


@pytest.mark.asyncio
async def test_set_breakpoint_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await DebuggerHandler.set_breakpoint(tab, "app.js", 1)
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_breakpoint_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await DebuggerHandler.set_breakpoint(tab, "app.js", 1)
    assert "timed out" in str(exc_info.value).lower()


# ── remove_breakpoint ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_remove_breakpoint_success():
    tab = _make_tab()
    # Pre-populate breakpoints dict
    DebuggerHandler._breakpoints["bp-1"] = "app.js:42"

    result = await DebuggerHandler.remove_breakpoint(tab, "bp-1")
    assert result is True
    assert "bp-1" not in DebuggerHandler._breakpoints


@pytest.mark.asyncio
async def test_remove_breakpoint_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await DebuggerHandler.remove_breakpoint(tab, "bp-1")
    assert "WebSocket" in str(exc_info.value)


# ── resume_execution ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resume_execution_success():
    tab = _make_tab()
    result = await DebuggerHandler.resume_execution(tab)
    assert result is True


@pytest.mark.asyncio
async def test_resume_execution_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await DebuggerHandler.resume_execution(tab)
    assert "WebSocket" in str(exc_info.value)


# ── step_over / step_into ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_step_over_success():
    tab = _make_tab()
    result = await DebuggerHandler.step_over(tab)
    assert result is True


@pytest.mark.asyncio
async def test_step_into_success():
    tab = _make_tab()
    result = await DebuggerHandler.step_into(tab)
    assert result is True


@pytest.mark.asyncio
async def test_step_over_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await DebuggerHandler.step_over(tab)
    assert "timed out" in str(exc_info.value).lower()


# ── get_call_stack ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_call_stack_returns_list():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = "Error\n    at foo (app.js:10)\n    at bar (app.js:20)"
    tab.send = AsyncMock(return_value=mock_result)

    result = await DebuggerHandler.get_call_stack(tab)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_call_stack_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await DebuggerHandler.get_call_stack(tab)
    assert "WebSocket" in str(exc_info.value)


# ── evaluate_on_call_frame ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_evaluate_on_call_frame_success():
    tab = _make_tab()
    mock_type = MagicMock()
    mock_type.value = "number"

    mock_obj = MagicMock()
    mock_obj.type_ = mock_type
    mock_obj.value = 42
    mock_obj.description = "42"

    mock_result = MagicMock()
    mock_result.result = mock_obj
    mock_result.exception_details = None
    tab.send = AsyncMock(return_value=mock_result)

    result = await DebuggerHandler.evaluate_on_call_frame(tab, "frame-0", "x + 1")
    assert result["result"]["value"] == 42
    assert result["exception_details"] is None


@pytest.mark.asyncio
async def test_evaluate_on_call_frame_with_exception():
    tab = _make_tab()
    mock_exc = MagicMock()
    mock_exc.text = "ReferenceError: x is not defined"
    mock_exc.line_number = 1
    mock_exc.column_number = 0

    mock_result = MagicMock()
    mock_result.result = None
    mock_result.exception_details = mock_exc
    tab.send = AsyncMock(return_value=mock_result)

    result = await DebuggerHandler.evaluate_on_call_frame(tab, "frame-0", "x")
    assert result["exception_details"] is not None
    assert "ReferenceError" in result["exception_details"]["text"]
