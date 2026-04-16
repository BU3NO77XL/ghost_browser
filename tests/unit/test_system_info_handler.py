"""Unit tests for SystemInfoHandler."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.system_info_handler import SystemInfoHandler


def _make_tab():
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)
    return tab


# ── get_info ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_info_returns_required_keys():
    """Property 7: get_info always returns gpu, model_name, command_line."""
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.gpu = MagicMock()
    mock_result.model_name = "Test Model"
    mock_result.command_line = "--headless"
    tab.send = AsyncMock(return_value=mock_result)

    result = await SystemInfoHandler.get_info(tab)
    assert "gpu" in result
    assert "model_name" in result
    assert "command_line" in result
    assert result["model_name"] == "Test Model"
    assert result["command_line"] == "--headless"


@pytest.mark.asyncio
async def test_get_info_timeout():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())
    with pytest.raises(Exception) as exc_info:
        await SystemInfoHandler.get_info(tab)
    assert "timed out" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_info_websocket_error():
    tab = _make_tab()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))
    with pytest.raises(Exception) as exc_info:
        await SystemInfoHandler.get_info(tab)
    assert "WebSocket" in str(exc_info.value)


# ── get_feature_state ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_feature_state_returns_feature_enabled_true():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.feature_enabled = True
    tab.send = AsyncMock(return_value=mock_result)

    result = await SystemInfoHandler.get_feature_state(tab, "SomeFeature")
    assert result == {"feature_enabled": True}


@pytest.mark.asyncio
async def test_get_feature_state_returns_feature_enabled_false():
    tab = _make_tab()
    mock_result = MagicMock()
    mock_result.feature_enabled = False
    tab.send = AsyncMock(return_value=mock_result)

    result = await SystemInfoHandler.get_feature_state(tab, "SomeFeature")
    assert result == {"feature_enabled": False}


# ── get_process_info ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_process_info_converts_to_plain_dicts():
    tab = _make_tab()
    proc1 = MagicMock()
    proc1.id = 1
    proc1.type = "browser"
    proc1.cpu_time = 0.5
    proc2 = MagicMock()
    proc2.id = 2
    proc2.type = "renderer"
    proc2.cpu_time = 1.2
    tab.send = AsyncMock(return_value=[proc1, proc2])

    result = await SystemInfoHandler.get_process_info(tab)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["type"] == "renderer"


@pytest.mark.asyncio
async def test_get_process_info_empty_list():
    tab = _make_tab()
    tab.send = AsyncMock(return_value=[])
    result = await SystemInfoHandler.get_process_info(tab)
    assert result == []
