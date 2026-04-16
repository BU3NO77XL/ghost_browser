"""Fetch management MCP tools for intercepting and modifying network requests via CDP."""

from typing import Any, Dict, List, Optional

from core.fetch_handler import FetchHandler
from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("fetch-management")
    async def fetch_enable(
        instance_id: str,
        patterns: Optional[List[Dict]] = None,
        handle_auth_requests: bool = False,
    ) -> bool:
        """
        Enable the Fetch domain to intercept network requests for a browser instance.

        Must be called before any request interception can happen. Optionally
        accepts URL patterns to filter which requests are intercepted.

        Example:
            fetch_enable("abc123", patterns=[
                {"url_pattern": "https://api.example.com/*", "request_stage": "Request"}
            ])

        Args:
            instance_id (str): Browser instance ID.
            patterns (Optional[List[Dict]]): List of request pattern dicts with optional
                'url_pattern', 'resource_type', and 'request_stage' keys. If None,
                all requests are intercepted.
            handle_auth_requests (bool): Whether to handle auth challenge requests.
                Defaults to False.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await FetchHandler.enable_fetch(
            tab, patterns=patterns, handle_auth_requests=handle_auth_requests
        )

    @section_tool("fetch-management")
    async def fetch_disable(instance_id: str) -> bool:
        """
        Disable the Fetch domain, stopping request interception for a browser instance.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await FetchHandler.disable_fetch(tab)

    @section_tool("fetch-management")
    async def fetch_fail_request(
        instance_id: str,
        request_id: str,
        error_reason: str,
    ) -> bool:
        """
        Cause an intercepted request to fail with the given network error reason.

        Args:
            instance_id (str): Browser instance ID.
            request_id (str): The intercepted request ID.
            error_reason (str): The network error reason (e.g. 'Failed', 'Aborted',
                'TimedOut', 'AccessDenied', 'ConnectionClosed', 'ConnectionReset',
                'ConnectionRefused', 'ConnectionAborted', 'ConnectionFailed',
                'NameNotResolved', 'InternetDisconnected', 'AddressUnreachable',
                'BlockedByClient', 'BlockedByResponse').

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await FetchHandler.fail_request(
            tab, request_id=request_id, error_reason=error_reason
        )

    @section_tool("fetch-management")
    async def fetch_fulfill_request(
        instance_id: str,
        request_id: str,
        response_code: int,
        response_headers: Optional[List[Dict]] = None,
        body: Optional[str] = None,
        response_phrase: Optional[str] = None,
    ) -> bool:
        """
        Fulfill an intercepted request with the given response.

        Args:
            instance_id (str): Browser instance ID.
            request_id (str): The intercepted request ID.
            response_code (int): The HTTP response code (e.g. 200, 404).
            response_headers (Optional[List[Dict]]): Response headers as list of
                dicts with 'name' and 'value' keys.
            body (Optional[str]): Response body (base64-encoded for binary content).
            response_phrase (Optional[str]): HTTP response phrase (e.g. 'OK', 'Not Found').

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await FetchHandler.fulfill_request(
            tab,
            request_id=request_id,
            response_code=response_code,
            response_headers=response_headers,
            body=body,
            response_phrase=response_phrase,
        )

    @section_tool("fetch-management")
    async def fetch_continue_request(
        instance_id: str,
        request_id: str,
        url: Optional[str] = None,
        method: Optional[str] = None,
        post_data: Optional[str] = None,
        headers: Optional[List[Dict]] = None,
    ) -> bool:
        """
        Continue an intercepted request, optionally modifying it.

        Args:
            instance_id (str): Browser instance ID.
            request_id (str): The intercepted request ID.
            url (Optional[str]): Override URL for the request.
            method (Optional[str]): Override HTTP method (e.g. 'GET', 'POST').
            post_data (Optional[str]): Override POST data.
            headers (Optional[List[Dict]]): Override headers as list of dicts
                with 'name' and 'value' keys.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await FetchHandler.continue_request(
            tab,
            request_id=request_id,
            url=url,
            method=method,
            post_data=post_data,
            headers=headers,
        )

    @section_tool("fetch-management")
    async def fetch_continue_with_auth(
        instance_id: str,
        request_id: str,
        auth_challenge_response: Dict[str, Any],
    ) -> bool:
        """
        Continue an intercepted request that requires authentication.

        The auth_challenge_response dict must contain a 'response' key with one of:
        'Default', 'CancelAuth', 'ProvideCredentials'. When using 'ProvideCredentials',
        also include 'username' and 'password' keys.

        Example:
            fetch_continue_with_auth("abc123", "req-1", {
                "response": "ProvideCredentials",
                "username": "user",
                "password": "pass"
            })

        Args:
            instance_id (str): Browser instance ID.
            request_id (str): The intercepted request ID.
            auth_challenge_response (Dict): Auth challenge response dict with
                'response' key and optional 'username' and 'password' keys.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await FetchHandler.continue_with_auth(
            tab,
            request_id=request_id,
            auth_challenge_response=auth_challenge_response,
        )

    @section_tool("fetch-management")
    async def fetch_get_response_body(
        instance_id: str,
        request_id: str,
    ) -> Dict[str, Any]:
        """
        Get the response body for an intercepted request.

        Returns the body content and whether it is base64-encoded. Binary
        responses will have base64_encoded set to True.

        Args:
            instance_id (str): Browser instance ID.
            request_id (str): The intercepted request ID.

        Returns:
            Dict: A dict with:
                - body (str): The response body content.
                - base64_encoded (bool): True if the body is base64-encoded binary data.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await FetchHandler.get_response_body(tab, request_id=request_id)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
