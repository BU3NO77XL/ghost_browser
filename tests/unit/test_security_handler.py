"""Unit tests for SecurityHandler."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.security_handler import SecurityHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── set_ignore_certificate_errors ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_set_ignore_certificate_errors_true():
    tab = _make_tab()
    result = await SecurityHandler.set_ignore_certificate_errors(tab, True)
    assert result is True
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_set_ignore_certificate_errors_false():
    tab = _make_tab()
    result = await SecurityHandler.set_ignore_certificate_errors(tab, False)
    assert result is True


@pytest.mark.asyncio
async def test_set_ignore_certificate_errors_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await SecurityHandler.set_ignore_certificate_errors(tab, True)
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_ignore_certificate_errors_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await SecurityHandler.set_ignore_certificate_errors(tab, True)
    assert "timed out" in str(exc_info.value).lower()


# ── get_security_state ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_security_state_https():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = '{"protocol":"https:","hostname":"example.com","is_secure":true}'
    tab.send = AsyncMock(side_effect=[None, mock_result])

    result = await SecurityHandler.get_security_state(tab)
    assert isinstance(result, dict)
    assert "security_state" in result


@pytest.mark.asyncio
async def test_get_security_state_http():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.result = MagicMock()
    mock_result.result.value = '{"protocol":"http:","hostname":"example.com","is_secure":false}'
    tab.send = AsyncMock(side_effect=[None, mock_result])

    result = await SecurityHandler.get_security_state(tab)
    assert result["security_state"] == "insecure"
    assert result["scheme_is_cryptographic"] is False


@pytest.mark.asyncio
async def test_get_security_state_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await SecurityHandler.get_security_state(tab)
    assert "WebSocket" in str(exc_info.value)


# ── handle_certificate_error ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_handle_certificate_error_continue():
    tab = _make_tab()
    result = await SecurityHandler.handle_certificate_error(tab, event_id=1, action="continue")
    assert result is True


@pytest.mark.asyncio
async def test_handle_certificate_error_cancel():
    tab = _make_tab()
    result = await SecurityHandler.handle_certificate_error(tab, event_id=1, action="cancel")
    assert result is True


@pytest.mark.asyncio
async def test_handle_certificate_error_invalid_action():
    tab = _make_tab()
    with pytest.raises(ValueError) as exc_info:
        await SecurityHandler.handle_certificate_error(tab, event_id=1, action="ignore")
    assert "Invalid action" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_certificate_error_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await SecurityHandler.handle_certificate_error(tab, event_id=1, action="continue")
    assert "WebSocket" in str(exc_info.value)
