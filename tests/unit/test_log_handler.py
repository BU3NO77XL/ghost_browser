"""Unit tests for LogHandler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from core.log_handler import LogHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── enable_log ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_enable_log_success():
    tab = _make_tab()
    result = await LogHandler.enable_log(tab)
    assert result is True
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_enable_log_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())
    with pytest.raises(Exception) as exc_info:
        await LogHandler.enable_log(tab)
    assert "timed out" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_enable_log_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))
    with pytest.raises(Exception) as exc_info:
        await LogHandler.enable_log(tab)
    assert "WebSocket" in str(exc_info.value)


# ── disable_log ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_disable_log_success():
    tab = _make_tab()
    result = await LogHandler.disable_log(tab)
    assert result is True


# ── clear_log ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_clear_log_success():
    tab = _make_tab()
    result = await LogHandler.clear_log(tab)
    assert result is True


# ── start_violations_report ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_start_violations_report_converts_dicts():
    """Verify dicts are converted to ViolationSetting objects before CDP call."""
    tab = _make_tab()
    settings = [{"name": "longTask", "threshold": 200.0}]

    with patch("core.log_handler.cdp") as mock_cdp:
        mock_cdp.log.ViolationSetting = MagicMock(return_value=MagicMock())
        mock_cdp.log.start_violations_report = MagicMock(return_value=MagicMock())
        tab.send = AsyncMock(return_value=None)

        result = await LogHandler.start_violations_report(tab, settings)
        assert result is True
        mock_cdp.log.ViolationSetting.assert_called_once_with(
            name="longTask", threshold=200.0
        )


@pytest.mark.asyncio
async def test_start_violations_report_multiple_settings():
    tab = _make_tab()
    settings = [
        {"name": "longTask", "threshold": 200.0},
        {"name": "longLayout", "threshold": 30.0},
    ]
    result = await LogHandler.start_violations_report(tab, settings)
    assert result is True


@pytest.mark.asyncio
async def test_start_violations_report_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())
    with pytest.raises(Exception) as exc_info:
        await LogHandler.start_violations_report(tab, [{"name": "x", "threshold": 1.0}])
    assert "timed out" in str(exc_info.value).lower()


# ── stop_violations_report ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_stop_violations_report_success():
    tab = _make_tab()
    result = await LogHandler.stop_violations_report(tab)
    assert result is True
