"""Security management MCP tools for certificate and security state control.

WARNING: Some tools in this module can weaken browser security protections.
Use only in controlled testing environments.
"""

from typing import Any, Dict

from core.login_guard import check_pending_login_guard
from core.security_handler import SecurityHandler


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("security-management")
    async def get_security_state(instance_id: str) -> Dict[str, Any]:
        """
        Get the current security state of the page.

        Returns information about the page's HTTPS status and whether the
        connection is considered secure.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Dict[str, Any]: Security state with security_state, scheme_is_cryptographic,
                            protocol, and hostname.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await SecurityHandler.get_security_state(tab)

    @section_tool("security-management")
    async def set_ignore_certificate_errors(instance_id: str, ignore: bool) -> bool:
        """
        Set whether SSL/TLS certificate errors should be ignored.

        WARNING: Ignoring certificate errors is a security risk. Only use this
        for testing purposes against known-safe environments. Never use in
        production or against untrusted sites.

        Args:
            instance_id (str): Browser instance ID.
            ignore (bool): True to ignore certificate errors, False to enforce them.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await SecurityHandler.set_ignore_certificate_errors(tab, ignore)

    @section_tool("security-management")
    async def handle_certificate_error(instance_id: str, event_id: int, action: str) -> bool:
        """
        Handle a certificate error event by continuing or cancelling the request.

        This is used to respond to certificate error events when certificate errors
        are not being automatically ignored.

        WARNING: Using 'continue' on a certificate error bypasses security checks.
        Only use in controlled testing environments.

        Args:
            instance_id (str): Browser instance ID.
            event_id (int): The certificate error event ID (from CDP Security events).
            action (str): The action to take: 'continue' (proceed anyway) or 'cancel'.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await SecurityHandler.handle_certificate_error(tab, event_id, action)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
