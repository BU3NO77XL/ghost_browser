"""Unit tests for AuditsHandler."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.audits_handler import AuditsHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── enable / disable ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_enable_audits_success():
    tab = _make_tab()
    result = await AuditsHandler.enable_audits(tab)
    assert result is True


@pytest.mark.asyncio
async def test_disable_audits_success():
    tab = _make_tab()
    result = await AuditsHandler.disable_audits(tab)
    assert result is True


# ── get_encoded_response — encoding validation ────────────────────────────────


@pytest.mark.asyncio
async def test_get_encoded_response_invalid_encoding_gif():
    tab = _make_tab()
    with pytest.raises(ValueError) as exc_info:
        await AuditsHandler.get_encoded_response(tab, "req-1", "gif")
    assert "gif" in str(exc_info.value)
    assert "jpeg" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_encoded_response_invalid_encoding_bmp():
    tab = _make_tab()
    with pytest.raises(ValueError):
        await AuditsHandler.get_encoded_response(tab, "req-1", "bmp")


@pytest.mark.asyncio
async def test_get_encoded_response_valid_webp():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.body = "base64data"
    mock_result.original_size = 1000
    mock_result.encoded_size = 800
    tab.send = AsyncMock(return_value=mock_result)

    result = await AuditsHandler.get_encoded_response(tab, "req-1", "webp")
    assert result["original_size"] == 1000
    assert result["encoded_size"] == 800


@pytest.mark.asyncio
async def test_get_encoded_response_valid_jpeg():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.body = "data"
    mock_result.original_size = 500
    mock_result.encoded_size = 400
    tab.send = AsyncMock(return_value=mock_result)

    result = await AuditsHandler.get_encoded_response(tab, "req-1", "jpeg")
    assert "body" in result


@pytest.mark.asyncio
async def test_get_encoded_response_valid_png():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.body = "data"
    mock_result.original_size = 200
    mock_result.encoded_size = 180
    tab.send = AsyncMock(return_value=mock_result)

    result = await AuditsHandler.get_encoded_response(tab, "req-1", "png")
    assert "encoded_size" in result


# ── check_contrast ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_check_contrast_returns_true_when_cdp_returns_none():
    tab = _make_tab()
    tab.send = AsyncMock(return_value=None)
    result = await AuditsHandler.check_contrast(tab)
    assert result is True


@pytest.mark.asyncio
async def test_check_contrast_with_report_aaa():
    tab = _make_tab()
    result = await AuditsHandler.check_contrast(tab, report_aaa=True)
    assert result is True


# ── error handling ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_enable_audits_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())
    with pytest.raises(Exception) as exc_info:
        await AuditsHandler.enable_audits(tab)
    assert "timed out" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_enable_audits_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))
    with pytest.raises(Exception) as exc_info:
        await AuditsHandler.enable_audits(tab)
    assert "WebSocket" in str(exc_info.value)
