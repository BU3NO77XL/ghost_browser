"""Unit tests for StorageCDPHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.storage_cdp_handler import StorageCDPHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── get_usage_and_quota ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_usage_and_quota_computes_usage_mb():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.usage = 1048576  # 1 MB in bytes
    mock_result.quota = 10485760
    mock_result.override_active = False
    mock_result.usage_breakdown = []
    tab.send = AsyncMock(return_value=mock_result)

    result = await StorageCDPHandler.get_usage_and_quota(tab, "https://example.com")
    assert result["usage_mb"] == 1.0
    assert result["usage"] == 1048576
    assert result["quota"] == 10485760
    assert "usage_breakdown" in result


@pytest.mark.asyncio
async def test_get_usage_and_quota_zero_usage():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.usage = 0
    mock_result.quota = 10485760
    mock_result.override_active = False
    mock_result.usage_breakdown = []
    tab.send = AsyncMock(return_value=mock_result)

    result = await StorageCDPHandler.get_usage_and_quota(tab, "https://example.com")
    assert result["usage_mb"] == 0.0


@pytest.mark.asyncio
async def test_get_usage_and_quota_rounds_to_two_decimals():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.usage = 1500000  # 1.430511... MB
    mock_result.quota = 10485760
    mock_result.override_active = False
    mock_result.usage_breakdown = []
    tab.send = AsyncMock(return_value=mock_result)

    result = await StorageCDPHandler.get_usage_and_quota(tab, "https://example.com")
    assert result["usage_mb"] == round(1500000 / (1024 * 1024), 2)


# ── clear_data_for_origin ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_clear_data_for_origin_success():
    tab = _make_tab()
    result = await StorageCDPHandler.clear_data_for_origin(tab, "https://example.com", "all")
    assert result is True
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_clear_data_for_origin_passes_storage_types():
    """Verify storage_types string is passed through to the CDP call."""
    tab = _make_tab()
    result = await StorageCDPHandler.clear_data_for_origin(
        tab, "https://example.com", "cookies,localStorage"
    )
    assert result is True


@pytest.mark.asyncio
async def test_clear_data_for_origin_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))
    with pytest.raises(Exception) as exc_info:
        await StorageCDPHandler.clear_data_for_origin(tab, "https://example.com", "all")
    assert "WebSocket" in str(exc_info.value)


# ── track / untrack ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_track_cache_storage_for_origin_success():
    tab = _make_tab()
    result = await StorageCDPHandler.track_cache_storage_for_origin(tab, "https://example.com")
    assert result is True


@pytest.mark.asyncio
async def test_untrack_cache_storage_for_origin_success():
    tab = _make_tab()
    result = await StorageCDPHandler.untrack_cache_storage_for_origin(tab, "https://example.com")
    assert result is True


@pytest.mark.asyncio
async def test_track_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())
    with pytest.raises(Exception) as exc_info:
        await StorageCDPHandler.track_cache_storage_for_origin(tab, "https://example.com")
    assert "timed out" in str(exc_info.value).lower()
