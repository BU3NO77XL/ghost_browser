"""Integration tests for storage_cdp_management tools module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_deps(tab=None):
    if tab is None:
        tab = AsyncMock()
        tab.send = AsyncMock(return_value=None)
    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=tab)
    return {"browser_manager": bm}, tab


def _register():
    from tools.storage_cdp_management import register

    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_storage_get_usage_and_quota_contains_usage_mb():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.usage = 2097152  # 2 MB
    mock_result.quota = 10485760
    mock_result.override_active = False
    mock_result.usage_breakdown = []
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["storage_get_usage_and_quota"]("inst-1", "https://example.com")
        assert "usage_mb" in result
        assert result["usage_mb"] == 2.0


@pytest.mark.asyncio
async def test_storage_clear_data_for_origin_success():
    register, mcp, section_tool, registered = _register()
    deps, _ = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["storage_clear_data_for_origin"]("inst-1", "https://example.com")
        assert result is True


@pytest.mark.asyncio
async def test_storage_get_usage_and_quota_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["storage_get_usage_and_quota"]("bad-id", "https://example.com")
        assert "Instance not found: bad-id" in str(exc_info.value)
