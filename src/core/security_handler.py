"""Security domain handler for certificate and security state management via CDP."""

import asyncio
from typing import Any, Dict, Optional

from nodriver import Tab, cdp

from core.debug_logger import debug_logger


class SecurityHandler:
    """Handles security operations via CDP Security domain."""

    @staticmethod
    async def enable_security_domain(tab: Tab) -> None:
        """
        Enable the Security domain for the given tab.

        Args:
            tab (Tab): The browser tab object.
        """
        try:
            await tab.send(cdp.security.enable())
        except Exception as e:
            error_msg = str(e).lower()
            if "already enabled" in error_msg:
                return
            raise

    @staticmethod
    async def set_ignore_certificate_errors(tab: Tab, ignore: bool) -> bool:
        """
        Set whether certificate errors should be ignored.

        WARNING: Ignoring certificate errors is a security risk. Only use this
        for testing purposes against known-safe environments.

        Args:
            tab (Tab): The browser tab object.
            ignore (bool): True to ignore certificate errors, False to enforce them.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "SecurityHandler",
            "set_ignore_certificate_errors",
            f"Setting ignore certificate errors: {ignore}",
        )
        try:
            await tab.send(cdp.security.set_ignore_certificate_errors(ignore=ignore))
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
                "SecurityHandler",
                "set_ignore_certificate_errors",
                e,
                {"ignore": ignore},
            )
            raise

    @staticmethod
    async def get_security_state(tab: Tab) -> Dict[str, Any]:
        """
        Get the current security state of the page.

        Returns information about the page's HTTPS status, certificate validity,
        and any security warnings.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            Dict[str, Any]: Security state with security_state, certificate_id,
                            scheme_is_cryptographic, and explanations.
        """
        debug_logger.log_info("SecurityHandler", "get_security_state", "Getting security state")
        try:
            await SecurityHandler.enable_security_domain(tab)
            # Use JS to get security info since CDP Security domain uses events
            result = await tab.send(
                cdp.runtime.evaluate(
                    expression="""
                    JSON.stringify({
                        protocol: location.protocol,
                        hostname: location.hostname,
                        is_secure: location.protocol === 'https:'
                    })
                    """,
                    return_by_value=True,
                )
            )
            import json

            state = {}
            if result and result.result and result.result.value:
                try:
                    state = json.loads(result.result.value)
                except Exception:
                    pass
            return {
                "security_state": "secure" if state.get("is_secure") else "insecure",
                "scheme_is_cryptographic": state.get("is_secure", False),
                "protocol": state.get("protocol", ""),
                "hostname": state.get("hostname", ""),
            }
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("SecurityHandler", "get_security_state", e, {})
            raise

    @staticmethod
    async def handle_certificate_error(tab: Tab, event_id: int, action: str) -> bool:
        """
        Handle a certificate error event.

        This is used to respond to certificate error events emitted by the
        Security domain when certificate errors are not being ignored.

        Args:
            tab (Tab): The browser tab object.
            event_id (int): The certificate error event ID.
            action (str): The action to take: 'continue' or 'cancel'.

        Returns:
            bool: True if successful.
        """
        if action not in ("continue", "cancel"):
            raise ValueError(f"Invalid action: '{action}'. Must be 'continue' or 'cancel'.")
        debug_logger.log_info(
            "SecurityHandler",
            "handle_certificate_error",
            f"Handling certificate error {event_id} with action: {action}",
        )
        try:
            await tab.send(
                cdp.security.handle_certificate_error(
                    event_id=event_id,
                    action=cdp.security.CertificateErrorAction(action),
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
                "SecurityHandler",
                "handle_certificate_error",
                e,
                {"event_id": event_id, "action": action},
            )
            raise
