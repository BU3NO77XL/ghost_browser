"""Unit tests for BrowserCDPHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from core.browser_cdp_handler import BrowserCDPHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── set_download_behavior — validation ───────────────────────────────────────

@pytest.mark.asyncio
async def test_set_download_behavior_allow_requires_path():
    tab = _make_tab()
    with pytest.raises(ValueError) as exc_info:
        await BrowserCDPHandler.set_download_behavior(tab, "allow")
    assert "download_path" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_download_behavior_allow_and_name_requires_path():
    tab = _make_tab()
    with pytest.raises(ValueError) as exc_info:
        await BrowserCDPHandler.set_download_behavior(tab, "allowAndName")
    assert "download_path" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_download_behavior_deny_no_path_ok():
    tab = _make_tab()
    result = await BrowserCDPHandler.set_download_behavior(tab, "deny")
    assert result is True


@pytest.mark.asyncio
async def test_set_download_behavior_default_no_path_ok():
    tab = _make_tab()
    result = await BrowserCDPHandler.set_download_behavior(tab, "default")
    assert result is True


@pytest.mark.asyncio
async def test_set_download_behavior_allow_with_path_ok():
    tab = _make_tab()
    result = await BrowserCDPHandler.set_download_behavior(tab, "allow", "/tmp/downloads")
    assert result is True


# ── get_window_bounds ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_window_bounds_returns_required_keys():
    tab = _make_tab()
    mock_bounds = MagicMock()
    mock_bounds.left = 0
    mock_bounds.top = 0
    mock_bounds.width = 1280
    mock_bounds.height = 720
    mock_bounds.window_state = "normal"
    tab.send = AsyncMock(return_value=mock_bounds)

    result = await BrowserCDPHandler.get_window_bounds(tab, 1)
    assert "left" in result
    assert "top" in result
    assert "width" in result
    assert "height" in result
    assert "window_state" in result
    assert result["width"] == 1280


# ── grant_permissions ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_grant_permissions_success():
    tab = _make_tab()
    result = await BrowserCDPHandler.grant_permissions(tab, ["geolocation"])
    assert result is True


# ── reset_permissions ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_reset_permissions_success():
    tab = _make_tab()
    result = await BrowserCDPHandler.reset_permissions(tab)
    assert result is True


# ── error handling ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_window_bounds_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())
    with pytest.raises(Exception) as exc_info:
        await BrowserCDPHandler.get_window_bounds(tab, 1)
    assert "timed out" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_reset_permissions_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))
    with pytest.raises(Exception) as exc_info:
        await BrowserCDPHandler.reset_permissions(tab)
    assert "WebSocket" in str(exc_info.value)
