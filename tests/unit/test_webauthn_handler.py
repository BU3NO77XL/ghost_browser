"""Unit tests for WebAuthnHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.webauthn_handler import WebAuthnHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── add_virtual_authenticator ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_virtual_authenticator_ctap2():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.authenticator_id = "auth-123"
    tab.send = AsyncMock(side_effect=[None, mock_result])

    result = await WebAuthnHandler.add_virtual_authenticator(
        tab, protocol="ctap2", transport="usb"
    )
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_add_virtual_authenticator_u2f():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.authenticator_id = "auth-u2f"
    tab.send = AsyncMock(side_effect=[None, mock_result])

    result = await WebAuthnHandler.add_virtual_authenticator(
        tab, protocol="u2f", transport="nfc"
    )
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_add_virtual_authenticator_internal_transport():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.authenticator_id = "auth-internal"
    tab.send = AsyncMock(side_effect=[None, mock_result])

    result = await WebAuthnHandler.add_virtual_authenticator(
        tab, protocol="ctap2", transport="internal",
        has_resident_key=True, has_user_verification=True, is_user_verified=True
    )
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_add_virtual_authenticator_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await WebAuthnHandler.add_virtual_authenticator(tab)
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_add_virtual_authenticator_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await WebAuthnHandler.add_virtual_authenticator(tab)
    assert "timed out" in str(exc_info.value).lower()


# ── remove_virtual_authenticator ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_remove_virtual_authenticator_success():
    tab = _make_tab()
    result = await WebAuthnHandler.remove_virtual_authenticator(tab, "auth-123")
    assert result is True
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_remove_virtual_authenticator_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await WebAuthnHandler.remove_virtual_authenticator(tab, "auth-123")
    assert "WebSocket" in str(exc_info.value)


# ── get_credentials ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_credentials_empty():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.credentials = []
    tab.send = AsyncMock(return_value=mock_result)

    result = await WebAuthnHandler.get_credentials(tab, "auth-123")
    assert result == []


@pytest.mark.asyncio
async def test_get_credentials_with_data():
    tab = _make_tab()
    mock_cred = MagicMock()
    mock_cred.credential_id = "cred-abc"
    mock_cred.is_resident_credential = True
    mock_cred.rp_id = "example.com"
    mock_cred.user_handle = "user-handle"
    mock_cred.sign_count = 5

    mock_result = MagicMock()
    mock_result.credentials = [mock_cred]
    tab.send = AsyncMock(return_value=mock_result)

    result = await WebAuthnHandler.get_credentials(tab, "auth-123")
    assert len(result) == 1
    assert result[0]["credential_id"] == "cred-abc"
    assert result[0]["rp_id"] == "example.com"
    assert result[0]["sign_count"] == 5


# ── remove_credential ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_remove_credential_success():
    tab = _make_tab()
    result = await WebAuthnHandler.remove_credential(tab, "auth-123", "cred-abc")
    assert result is True


@pytest.mark.asyncio
async def test_remove_credential_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await WebAuthnHandler.remove_credential(tab, "auth-123", "cred-abc")
    assert "WebSocket" in str(exc_info.value)


# ── set_user_verified ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_set_user_verified_true():
    tab = _make_tab()
    result = await WebAuthnHandler.set_user_verified(tab, "auth-123", True)
    assert result is True


@pytest.mark.asyncio
async def test_set_user_verified_false():
    tab = _make_tab()
    result = await WebAuthnHandler.set_user_verified(tab, "auth-123", False)
    assert result is True


@pytest.mark.asyncio
async def test_set_user_verified_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await WebAuthnHandler.set_user_verified(tab, "auth-123", True)
    assert "timed out" in str(exc_info.value).lower()
