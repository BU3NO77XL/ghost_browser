"""Unit tests for raw CDP command routing."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.cdp_function_executor import CDPFunctionExecutor
from tools import cdp_advanced


def _make_section_tool():
    def section_tool(_section):
        def decorator(func):
            return func

        return decorator

    return section_tool


def _consume_cdp_generator(cdp_obj, response=None):
    command = next(cdp_obj)
    try:
        cdp_obj.send(response or {})
    except StopIteration as exc:
        return command, exc.value
    return command, None


@pytest.mark.asyncio
async def test_dispatch_mouse_event_sends_raw_input_payload():
    sent = []

    async def send(cdp_obj):
        command, result = _consume_cdp_generator(cdp_obj)
        sent.append(command)
        return result

    tab = SimpleNamespace(
        send=AsyncMock(side_effect=send),
        browser=SimpleNamespace(connection=SimpleNamespace(send=MagicMock())),
    )
    browser_manager = SimpleNamespace(get_tab=AsyncMock(return_value=tab))
    tools = cdp_advanced.register(
        MagicMock(),
        _make_section_tool(),
        {"browser_manager": browser_manager},
    )

    result = await tools["dispatch_mouse_event"](
        "browser-1",
        "mousePressed",
        10,
        20,
        button="left",
        click_count=1,
    )

    assert result == {"success": True, "event": "mousePressed", "x": 10, "y": 20}
    assert sent == [
        {
            "method": "Input.dispatchMouseEvent",
            "params": {
                "type": "mousePressed",
                "x": 10,
                "y": 20,
                "button": "left",
                "clickCount": 1,
            },
        }
    ]
    tab.browser.connection.send.assert_not_called()


@pytest.mark.asyncio
async def test_execute_cdp_command_accepts_fully_qualified_raw_method():
    sent = []

    async def send(cdp_obj):
        command, result = _consume_cdp_generator(cdp_obj, {"ok": True})
        sent.append(command)
        return result

    tab = SimpleNamespace(send=AsyncMock(side_effect=send))
    executor = CDPFunctionExecutor()

    result = await executor.execute_cdp_command(
        tab,
        "Input.dispatchMouseEvent",
        {"type": "mouseReleased", "x": 5, "y": 6, "button": "left"},
    )

    assert result["success"] is True
    assert result["result"] == {"ok": True}
    assert sent == [
        {
            "method": "Input.dispatchMouseEvent",
            "params": {"type": "mouseReleased", "x": 5, "y": 6, "button": "left"},
        }
    ]
