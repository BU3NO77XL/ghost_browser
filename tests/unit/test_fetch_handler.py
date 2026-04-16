"""Unit tests for FetchHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from core.fetch_handler import FetchHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── enable_fetch ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_enable_fetch_no_patterns():
    tab = _make_tab()
    result = await FetchHandler.enable_fetch(tab)
    assert result is True


@pytest.mark.asyncio
async def test_enable_fetch_converts_pattern_dicts():
    """Verify pattern dicts are converted to RequestPattern objects."""
    tab = _make_tab()
    patterns = [{"url_pattern": "https://api.example.com/*", "request_stage": "Request"}]

    with patch("core.fetch_handler.cdp") as mock_cdp:
        mock_cdp.fetch.RequestPattern = MagicMock(return_value=MagicMock())
        mock_cdp.fetch.enable = MagicMock(return_value=MagicMock())
        tab.send = AsyncMock(return_value=None)

        result = await FetchHandler.enable_fetch(tab, patterns=patterns)
        assert result is True
        mock_cdp.fetch.RequestPattern.assert_called_once_with(
            url_pattern="https://api.example.com/*", request_stage="Request"
        )


@pytest.mark.asyncio
async def test_enable_fetch_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())
    with pytest.raises(Exception) as exc_info:
        await FetchHandler.enable_fetch(tab)
    assert "timed out" in str(exc_info.value).lower()


# ── disable_fetch ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_disable_fetch_success():
    tab = _make_tab()
    result = await FetchHandler.disable_fetch(tab)
    assert result is True


# ── continue_with_auth ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_continue_with_auth_converts_dict():
    """Verify auth dict is converted to AuthChallengeResponse."""
    tab = _make_tab()
    auth = {"response": "ProvideCredentials", "username": "user", "password": "pass"}

    with patch("core.fetch_handler.cdp") as mock_cdp:
        mock_cdp.fetch.AuthChallengeResponse = MagicMock(return_value=MagicMock())
        mock_cdp.fetch.RequestId = MagicMock(return_value=MagicMock())
        mock_cdp.fetch.continue_with_auth = MagicMock(return_value=MagicMock())
        tab.send = AsyncMock(return_value=None)

        result = await FetchHandler.continue_with_auth(tab, "req-1", auth)
        assert result is True
        mock_cdp.fetch.AuthChallengeResponse.assert_called_once_with(
            response="ProvideCredentials", username="user", password="pass"
        )


# ── get_response_body ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_response_body_structural_invariant():
    """Property 6: always returns dict with body (str) and base64_encoded (bool)."""
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.body = "hello world"
    mock_result.base64_encoded = False
    tab.send = AsyncMock(return_value=mock_result)

    result = await FetchHandler.get_response_body(tab, "req-1")
    assert isinstance(result["body"], str)
    assert isinstance(result["base64_encoded"], bool)
    assert result["body"] == "hello world"
    assert result["base64_encoded"] is False


@pytest.mark.asyncio
async def test_get_response_body_base64():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.body = "SGVsbG8="
    mock_result.base64_encoded = True
    tab.send = AsyncMock(return_value=mock_result)

    result = await FetchHandler.get_response_body(tab, "req-2")
    assert result["base64_encoded"] is True


@pytest.mark.asyncio
async def test_get_response_body_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))
    with pytest.raises(Exception) as exc_info:
        await FetchHandler.get_response_body(tab, "req-1")
    assert "WebSocket" in str(exc_info.value)
