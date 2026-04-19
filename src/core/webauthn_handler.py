"""WebAuthn domain handler for virtual authenticator management via CDP."""

import asyncio
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.debug_logger import debug_logger


class WebAuthnHandler:
    """Handles WebAuthn virtual authenticator operations via CDP WebAuthn domain."""

    @staticmethod
    async def enable_webauthn_domain(tab: Tab) -> None:
        """
        Enable the WebAuthn domain for the given tab.

        Args:
            tab (Tab): The browser tab object.
        """
        try:
            await tab.send(cdp.web_authn.enable())
        except Exception as e:
            error_msg = str(e).lower()
            if "already enabled" in error_msg:
                return
            raise

    @staticmethod
    async def add_virtual_authenticator(
        tab: Tab,
        protocol: str = "ctap2",
        transport: str = "usb",
        has_resident_key: bool = True,
        has_user_verification: bool = True,
        is_user_verified: bool = True,
    ) -> str:
        """
        Add a virtual authenticator for WebAuthn testing.

        Supported protocols: 'ctap2' (FIDO2), 'u2f' (FIDO U2F)
        Supported transports: 'usb', 'nfc', 'ble', 'internal'

        Args:
            tab (Tab): The browser tab object.
            protocol (str): Authenticator protocol ('ctap2' or 'u2f').
            transport (str): Authenticator transport ('usb', 'nfc', 'ble', 'internal').
            has_resident_key (bool): Whether the authenticator supports resident keys.
            has_user_verification (bool): Whether the authenticator supports user verification.
            is_user_verified (bool): Whether the user is considered verified.

        Returns:
            str: The authenticator ID.
        """
        debug_logger.log_info(
            "WebAuthnHandler",
            "add_virtual_authenticator",
            f"Adding virtual authenticator: protocol={protocol}, transport={transport}",
        )
        try:
            await WebAuthnHandler.enable_webauthn_domain(tab)
            options = cdp.web_authn.VirtualAuthenticatorOptions(
                protocol=cdp.web_authn.AuthenticatorProtocol(protocol),
                transport=cdp.web_authn.AuthenticatorTransport(transport),
                has_resident_key=has_resident_key,
                has_user_verification=has_user_verification,
                is_user_verified=is_user_verified,
            )
            result = await tab.send(cdp.web_authn.add_virtual_authenticator(options=options))
            authenticator_id = str(getattr(result, "authenticator_id", result))
            debug_logger.log_info(
                "WebAuthnHandler",
                "add_virtual_authenticator",
                f"Created authenticator: {authenticator_id}",
            )
            return authenticator_id
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "WebAuthnHandler",
                "add_virtual_authenticator",
                e,
                {"protocol": protocol, "transport": transport},
            )
            raise

    @staticmethod
    async def remove_virtual_authenticator(tab: Tab, authenticator_id: str) -> bool:
        """
        Remove a virtual authenticator.

        Args:
            tab (Tab): The browser tab object.
            authenticator_id (str): The authenticator ID to remove.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "WebAuthnHandler",
            "remove_virtual_authenticator",
            f"Removing authenticator: {authenticator_id}",
        )
        try:
            await tab.send(
                cdp.web_authn.remove_virtual_authenticator(
                    authenticator_id=cdp.web_authn.AuthenticatorId(authenticator_id)
                )
            )
            return True
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "WebAuthnHandler",
                "remove_virtual_authenticator",
                e,
                {"authenticator_id": authenticator_id},
            )
            raise

    @staticmethod
    async def add_credential(
        tab: Tab,
        authenticator_id: str,
        credential_id: str,
        rp_id: str,
        private_key: str,
        user_handle: Optional[str] = None,
        sign_count: int = 0,
    ) -> bool:
        """
        Add a credential to a virtual authenticator.

        Args:
            tab (Tab): The browser tab object.
            authenticator_id (str): The authenticator ID.
            credential_id (str): Base64-encoded credential ID.
            rp_id (str): Relying party ID (e.g., 'example.com').
            private_key (str): Base64-encoded private key (PKCS#8 DER format).
            user_handle (Optional[str]): Base64-encoded user handle.
            sign_count (int): Initial signature counter value.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "WebAuthnHandler",
            "add_credential",
            f"Adding credential to authenticator: {authenticator_id}",
        )
        try:
            credential = cdp.web_authn.Credential(
                credential_id=credential_id,
                is_resident_credential=True,
                rp_id=rp_id,
                private_key=private_key,
                user_handle=user_handle,
                sign_count=sign_count,
            )
            await tab.send(
                cdp.web_authn.add_credential(
                    authenticator_id=cdp.web_authn.AuthenticatorId(authenticator_id),
                    credential=credential,
                )
            )
            return True
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "WebAuthnHandler",
                "add_credential",
                e,
                {"authenticator_id": authenticator_id, "rp_id": rp_id},
            )
            raise

    @staticmethod
    async def get_credentials(tab: Tab, authenticator_id: str) -> List[Dict[str, Any]]:
        """
        Get all credentials stored in a virtual authenticator.

        Args:
            tab (Tab): The browser tab object.
            authenticator_id (str): The authenticator ID.

        Returns:
            List[Dict[str, Any]]: List of credential objects.
        """
        debug_logger.log_info(
            "WebAuthnHandler",
            "get_credentials",
            f"Getting credentials for authenticator: {authenticator_id}",
        )
        try:
            result = await tab.send(
                cdp.web_authn.get_credentials(
                    authenticator_id=cdp.web_authn.AuthenticatorId(authenticator_id)
                )
            )
            credentials = []
            credential_items = (
                result if isinstance(result, list) else getattr(result, "credentials", None) or []
            )
            for cred in credential_items:
                credentials.append(
                    {
                        "credential_id": cred.credential_id,
                        "is_resident_credential": cred.is_resident_credential,
                        "rp_id": cred.rp_id,
                        "user_handle": cred.user_handle,
                        "sign_count": cred.sign_count,
                    }
                )
            return credentials
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "WebAuthnHandler",
                "get_credentials",
                e,
                {"authenticator_id": authenticator_id},
            )
            raise

    @staticmethod
    async def remove_credential(tab: Tab, authenticator_id: str, credential_id: str) -> bool:
        """
        Remove a credential from a virtual authenticator.

        Args:
            tab (Tab): The browser tab object.
            authenticator_id (str): The authenticator ID.
            credential_id (str): The credential ID to remove.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "WebAuthnHandler",
            "remove_credential",
            f"Removing credential {credential_id} from authenticator: {authenticator_id}",
        )
        try:
            await tab.send(
                cdp.web_authn.remove_credential(
                    authenticator_id=cdp.web_authn.AuthenticatorId(authenticator_id),
                    credential_id=credential_id,
                )
            )
            return True
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "WebAuthnHandler",
                "remove_credential",
                e,
                {"authenticator_id": authenticator_id, "credential_id": credential_id},
            )
            raise

    @staticmethod
    async def set_user_verified(tab: Tab, authenticator_id: str, is_user_verified: bool) -> bool:
        """
        Set the user verified state for a virtual authenticator.

        Args:
            tab (Tab): The browser tab object.
            authenticator_id (str): The authenticator ID.
            is_user_verified (bool): Whether the user should be considered verified.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "WebAuthnHandler",
            "set_user_verified",
            f"Setting user verified={is_user_verified} for authenticator: {authenticator_id}",
        )
        try:
            await tab.send(
                cdp.web_authn.set_user_verified(
                    authenticator_id=cdp.web_authn.AuthenticatorId(authenticator_id),
                    is_user_verified=is_user_verified,
                )
            )
            return True
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "WebAuthnHandler",
                "set_user_verified",
                e,
                {"authenticator_id": authenticator_id, "is_user_verified": is_user_verified},
            )
            raise
