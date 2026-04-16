"""Integration tests for webauthn_management tools module."""

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
    from tools.webauthn_management import register
    mcp = MagicMock()
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func
        return decorator

    return register, mcp, section_tool, registered


@pytest.mark.asyncio
async def test_add_virtual_authenticator_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.authenticator_id = "auth-123"
    tab.send = AsyncMock(side_effect=[None, mock_result])
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["add_virtual_authenticator"](
            "inst-1", protocol="ctap2", transport="usb"
        )
        assert isinstance(result, str)


@pytest.mark.asyncio
async def test_remove_virtual_authenticator_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["remove_virtual_authenticator"]("inst-1", authenticator_id="auth-123")
        assert result is True


@pytest.mark.asyncio
async def test_get_webauthn_credentials_tool():
    register, mcp, section_tool, registered = _register()

    tab = AsyncMock()
    mock_result = MagicMock()
    mock_result.credentials = []
    tab.send = AsyncMock(return_value=mock_result)
    deps, _ = _make_deps(tab)

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["get_webauthn_credentials"]("inst-1", authenticator_id="auth-123")
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_remove_webauthn_credential_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["remove_webauthn_credential"](
            "inst-1", authenticator_id="auth-123", credential_id="cred-abc"
        )
        assert result is True


@pytest.mark.asyncio
async def test_set_webauthn_user_verified_tool():
    register, mcp, section_tool, registered = _register()
    deps, tab = _make_deps()

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        result = await registered["set_webauthn_user_verified"](
            "inst-1", authenticator_id="auth-123", is_user_verified=True
        )
        assert result is True


@pytest.mark.asyncio
async def test_webauthn_tool_instance_not_found():
    register, mcp, section_tool, registered = _register()

    bm = MagicMock()
    bm.get_tab = AsyncMock(return_value=None)
    deps = {"browser_manager": bm}

    with patch("core.login_guard.check_pending_login_guard", return_value=None):
        register(mcp, section_tool, deps)
        with pytest.raises(Exception) as exc_info:
            await registered["get_webauthn_credentials"]("bad-id", authenticator_id="auth-123")
        assert "not found" in str(exc_info.value).lower()
