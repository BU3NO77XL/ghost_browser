"""WebAuthn management MCP tools for virtual authenticator testing."""

from typing import Any, Dict, List, Optional

from core.login_guard import check_pending_login_guard
from core.webauthn_handler import WebAuthnHandler


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("webauthn-management")
    async def add_virtual_authenticator(
        instance_id: str,
        protocol: str = "ctap2",
        transport: str = "usb",
        has_resident_key: bool = True,
        has_user_verification: bool = True,
        is_user_verified: bool = True,
    ) -> str:
        """
        Add a virtual WebAuthn authenticator for testing passkeys and FIDO2.

        WebAuthn (Web Authentication) is the standard for passwordless authentication.
        Virtual authenticators let you test WebAuthn flows without physical hardware.

        Supported protocols:
        - 'ctap2': FIDO2/WebAuthn (modern, supports resident keys)
        - 'u2f': FIDO U2F (legacy)

        Supported transports:
        - 'usb': USB security key
        - 'nfc': NFC security key
        - 'ble': Bluetooth security key
        - 'internal': Platform authenticator (Touch ID, Windows Hello)

        Args:
            instance_id (str): Browser instance ID.
            protocol (str): Authenticator protocol ('ctap2' or 'u2f').
            transport (str): Authenticator transport ('usb', 'nfc', 'ble', 'internal').
            has_resident_key (bool): Whether the authenticator supports resident keys (passkeys).
            has_user_verification (bool): Whether the authenticator supports user verification.
            is_user_verified (bool): Whether the user is considered verified.

        Returns:
            str: The authenticator ID (use this for subsequent credential operations).
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await WebAuthnHandler.add_virtual_authenticator(
            tab, protocol, transport, has_resident_key, has_user_verification, is_user_verified
        )

    @section_tool("webauthn-management")
    async def remove_virtual_authenticator(
        instance_id: str, authenticator_id: str
    ) -> bool:
        """
        Remove a virtual WebAuthn authenticator.

        Args:
            instance_id (str): Browser instance ID.
            authenticator_id (str): The authenticator ID to remove.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await WebAuthnHandler.remove_virtual_authenticator(tab, authenticator_id)

    @section_tool("webauthn-management")
    async def add_webauthn_credential(
        instance_id: str,
        authenticator_id: str,
        credential_id: str,
        rp_id: str,
        private_key: str,
        user_handle: Optional[str] = None,
        sign_count: int = 0,
    ) -> bool:
        """
        Add a credential to a virtual WebAuthn authenticator.

        Args:
            instance_id (str): Browser instance ID.
            authenticator_id (str): The authenticator ID.
            credential_id (str): Base64-encoded credential ID.
            rp_id (str): Relying party ID (e.g., 'example.com').
            private_key (str): Base64-encoded private key (PKCS#8 DER format).
            user_handle (Optional[str]): Base64-encoded user handle.
            sign_count (int): Initial signature counter value.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await WebAuthnHandler.add_credential(
            tab, authenticator_id, credential_id, rp_id, private_key, user_handle, sign_count
        )

    @section_tool("webauthn-management")
    async def get_webauthn_credentials(
        instance_id: str, authenticator_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all credentials stored in a virtual WebAuthn authenticator.

        Args:
            instance_id (str): Browser instance ID.
            authenticator_id (str): The authenticator ID.

        Returns:
            List[Dict[str, Any]]: List of credential objects with id, rp_id, sign_count.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await WebAuthnHandler.get_credentials(tab, authenticator_id)

    @section_tool("webauthn-management")
    async def remove_webauthn_credential(
        instance_id: str, authenticator_id: str, credential_id: str
    ) -> bool:
        """
        Remove a credential from a virtual WebAuthn authenticator.

        Args:
            instance_id (str): Browser instance ID.
            authenticator_id (str): The authenticator ID.
            credential_id (str): The credential ID to remove.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await WebAuthnHandler.remove_credential(tab, authenticator_id, credential_id)

    @section_tool("webauthn-management")
    async def set_webauthn_user_verified(
        instance_id: str, authenticator_id: str, is_user_verified: bool
    ) -> bool:
        """
        Set the user verified state for a virtual WebAuthn authenticator.

        When is_user_verified=True, the authenticator will report that the user
        has been verified (e.g., via biometrics or PIN), allowing UV-required
        credentials to be used.

        Args:
            instance_id (str): Browser instance ID.
            authenticator_id (str): The authenticator ID.
            is_user_verified (bool): Whether the user should be considered verified.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await WebAuthnHandler.set_user_verified(
            tab, authenticator_id, is_user_verified
        )

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
