"""Network debugging tools: requests, headers, cookies."""

import base64
from typing import Any, Dict, List, Optional, Union

from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]
    network_interceptor = deps["network_interceptor"]
    response_handler = deps["response_handler"]

    @section_tool("network-debugging")
    async def list_network_requests(
        instance_id: str, filter_type: Optional[str] = None
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        List captured network requests.

        Args:
            instance_id (str): Browser instance ID.
            filter_type (Optional[str]): Filter by resource type (e.g., 'image', 'script', 'xhr').

        Returns:
            Union[List[Dict[str, Any]], Dict[str, Any]]: List of network requests.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        requests = await network_interceptor.list_requests(instance_id, filter_type)
        formatted_requests = [
            {
                "request_id": req.request_id,
                "url": req.url,
                "method": req.method,
                "resource_type": req.resource_type,
                "timestamp": req.timestamp.isoformat(),
            }
            for req in requests
        ]
        return response_handler.handle_response(formatted_requests, "network_requests")

    @section_tool("network-debugging")
    async def get_request_details(request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a network request.

        Args:
            request_id (str): Network request ID.

        Returns:
            Optional[Dict[str, Any]]: Request details including headers, cookies, and body.
        """
        request = await network_interceptor.get_request(request_id)
        if request:
            return request.model_dump(mode="json")
        return None

    @section_tool("network-debugging")
    async def get_response_details(request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get response details for a network request.

        Args:
            request_id (str): Network request ID.

        Returns:
            Optional[Dict[str, Any]]: Response details including status, headers, and metadata.
        """
        response = await network_interceptor.get_response(request_id)
        if response:
            return response.model_dump(mode="json")
        return None

    @section_tool("network-debugging")
    async def get_response_content(instance_id: str, request_id: str) -> Optional[str]:
        """
        Get response body content.

        Args:
            instance_id (str): Browser instance ID.
            request_id (str): Network request ID.

        Returns:
            Optional[str]: Response body as text (base64 encoded for binary).
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        body = await network_interceptor.get_response_body(tab, request_id)
        if body:
            try:
                return body.decode("utf-8")
            except UnicodeDecodeError:
                return base64.b64encode(body).decode("utf-8")
        return None

    @section_tool("network-debugging")
    async def modify_headers(instance_id: str, headers: Dict[str, str]) -> bool:
        """
        Modify request headers for future requests.

        Args:
            instance_id (str): Browser instance ID.
            headers (Dict[str, str]): Headers to add/modify.

        Returns:
            bool: True if modified successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await network_interceptor.modify_headers(tab, headers)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
