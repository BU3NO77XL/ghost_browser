"""Fetch domain handler for intercepting and modifying network requests via CDP."""

import asyncio
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.debug_logger import debug_logger


class FetchHandler:
    """Handles network request interception via CDP Fetch domain."""

    @staticmethod
    async def enable_fetch(
        tab: Tab,
        patterns: Optional[List[Dict[str, Any]]] = None,
        handle_auth_requests: bool = False,
    ) -> bool:
        """
        Enable the Fetch domain to intercept network requests.

        Args:
            tab (Tab): The browser tab object.
            patterns (Optional[List[Dict]]): List of request pattern dicts with optional
                'url_pattern', 'resource_type', and 'request_stage' keys.
            handle_auth_requests (bool): Whether to handle auth challenge requests.
                Defaults to False.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info("FetchHandler", "enable_fetch", "Enabling Fetch domain")
        try:
            request_patterns = None
            if patterns:
                request_patterns = [cdp.fetch.RequestPattern(**pattern) for pattern in patterns]
            await tab.send(
                cdp.fetch.enable(
                    patterns=request_patterns,
                    handle_auth_requests=handle_auth_requests,
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
            debug_logger.log_error("FetchHandler", "enable_fetch", e, {"patterns": patterns})
            raise

    @staticmethod
    async def disable_fetch(tab: Tab) -> bool:
        """
        Disable the Fetch domain, stopping request interception.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info("FetchHandler", "disable_fetch", "Disabling Fetch domain")
        try:
            await tab.send(cdp.fetch.disable())
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
            debug_logger.log_error("FetchHandler", "disable_fetch", e, {})
            raise

    @staticmethod
    async def fail_request(
        tab: Tab,
        request_id: str,
        error_reason: str,
    ) -> bool:
        """
        Cause a request to fail with the given network error reason.

        Args:
            tab (Tab): The browser tab object.
            request_id (str): The intercepted request ID.
            error_reason (str): The network error reason (e.g. 'Failed', 'Aborted').

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "FetchHandler",
            "fail_request",
            f"Failing request {request_id} with reason {error_reason}",
        )
        try:
            await tab.send(
                cdp.fetch.fail_request(
                    request_id=cdp.fetch.RequestId(request_id),
                    error_reason=cdp.network.ErrorReason(error_reason),
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
                "FetchHandler",
                "fail_request",
                e,
                {"request_id": request_id, "error_reason": error_reason},
            )
            raise

    @staticmethod
    async def fulfill_request(
        tab: Tab,
        request_id: str,
        response_code: int,
        response_headers: Optional[List[Dict[str, str]]] = None,
        body: Optional[str] = None,
        response_phrase: Optional[str] = None,
    ) -> bool:
        """
        Fulfill an intercepted request with the given response.

        Args:
            tab (Tab): The browser tab object.
            request_id (str): The intercepted request ID.
            response_code (int): The HTTP response code.
            response_headers (Optional[List[Dict]]): Response headers as list of
                dicts with 'name' and 'value' keys.
            body (Optional[str]): Response body (base64-encoded for binary).
            response_phrase (Optional[str]): HTTP response phrase (e.g. 'OK').

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "FetchHandler",
            "fulfill_request",
            f"Fulfilling request {request_id} with status {response_code}",
        )
        try:
            headers = None
            if response_headers:
                headers = [
                    cdp.fetch.HeaderEntry(name=h["name"], value=h["value"])
                    for h in response_headers
                ]
            await tab.send(
                cdp.fetch.fulfill_request(
                    request_id=cdp.fetch.RequestId(request_id),
                    response_code=response_code,
                    response_headers=headers,
                    body=body,
                    response_phrase=response_phrase,
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
                "FetchHandler",
                "fulfill_request",
                e,
                {"request_id": request_id, "response_code": response_code},
            )
            raise

    @staticmethod
    async def continue_request(
        tab: Tab,
        request_id: str,
        url: Optional[str] = None,
        method: Optional[str] = None,
        post_data: Optional[str] = None,
        headers: Optional[List[Dict[str, str]]] = None,
    ) -> bool:
        """
        Continue an intercepted request, optionally modifying it.

        Args:
            tab (Tab): The browser tab object.
            request_id (str): The intercepted request ID.
            url (Optional[str]): Override URL for the request.
            method (Optional[str]): Override HTTP method.
            post_data (Optional[str]): Override POST data.
            headers (Optional[List[Dict]]): Override headers as list of dicts
                with 'name' and 'value' keys.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "FetchHandler",
            "continue_request",
            f"Continuing request {request_id}",
        )
        try:
            override_headers = None
            if headers:
                override_headers = [
                    cdp.fetch.HeaderEntry(name=h["name"], value=h["value"]) for h in headers
                ]
            await tab.send(
                cdp.fetch.continue_request(
                    request_id=cdp.fetch.RequestId(request_id),
                    url=url,
                    method=method,
                    post_data=post_data,
                    headers=override_headers,
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
                "FetchHandler",
                "continue_request",
                e,
                {"request_id": request_id},
            )
            raise

    @staticmethod
    async def continue_with_auth(
        tab: Tab,
        request_id: str,
        auth_challenge_response: Dict[str, Any],
    ) -> bool:
        """
        Continue an intercepted request that requires authentication.

        Args:
            tab (Tab): The browser tab object.
            request_id (str): The intercepted request ID.
            auth_challenge_response (Dict): Auth challenge response dict with
                'response' key and optional 'username' and 'password' keys.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "FetchHandler",
            "continue_with_auth",
            f"Continuing request {request_id} with auth",
        )
        try:
            auth_response = cdp.fetch.AuthChallengeResponse(
                response=auth_challenge_response["response"],
                username=auth_challenge_response.get("username"),
                password=auth_challenge_response.get("password"),
            )
            await tab.send(
                cdp.fetch.continue_with_auth(
                    request_id=cdp.fetch.RequestId(request_id),
                    auth_challenge_response=auth_response,
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
                "FetchHandler",
                "continue_with_auth",
                e,
                {"request_id": request_id},
            )
            raise

    @staticmethod
    async def get_response_body(
        tab: Tab,
        request_id: str,
    ) -> Dict[str, Any]:
        """
        Get the response body for an intercepted request.

        Args:
            tab (Tab): The browser tab object.
            request_id (str): The intercepted request ID.

        Returns:
            Dict: A dict with 'body' (str) and 'base64_encoded' (bool) keys.
        """
        debug_logger.log_info(
            "FetchHandler",
            "get_response_body",
            f"Getting response body for request {request_id}",
        )
        try:
            result = await tab.send(
                cdp.fetch.get_response_body(
                    request_id=cdp.fetch.RequestId(request_id),
                )
            )
            return {
                "body": result.body,
                "base64_encoded": result.base64_encoded,
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
            debug_logger.log_error(
                "FetchHandler",
                "get_response_body",
                e,
                {"request_id": request_id},
            )
            raise
