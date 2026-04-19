"""Network interception and traffic monitoring using CDP."""

import asyncio
import base64
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import nodriver as uc
from nodriver import Tab

from core.cdp_result import to_json
from core.debug_logger import debug_logger
from core.models import NetworkRequest, NetworkResponse


class NetworkInterceptor:
    """Intercepts and manages network traffic for browser instances."""

    MAX_REQUESTS_PER_INSTANCE = 500  # prevent unbounded memory growth

    def __init__(self):
        self._requests: Dict[str, NetworkRequest] = {}
        self._responses: Dict[str, NetworkResponse] = {}
        self._instance_requests: Dict[str, List[str]] = {}
        self._lock = asyncio.Lock()

    async def setup_interception(
        self, tab: Tab, instance_id: str, block_resources: List[str] = None
    ):
        """
        Set up network interception for a tab.

        tab: Tab - The browser tab to intercept.
        instance_id: str - The browser instance identifier.
        block_resources: List[str] - List of resource types or URL patterns to block.
        """
        try:
            await tab.send(uc.cdp.network.enable())

            if block_resources:
                # Convert resource types to URL patterns for blocking
                url_patterns = []
                for resource_type in block_resources:
                    # Map resource types to URL patterns that typically identify these resources
                    resource_patterns = {
                        "image": [
                            "*.jpg",
                            "*.jpeg",
                            "*.png",
                            "*.gif",
                            "*.webp",
                            "*.svg",
                            "*.bmp",
                            "*.ico",
                        ],
                        "stylesheet": ["*.css"],
                        "font": ["*.woff", "*.woff2", "*.ttf", "*.otf", "*.eot"],
                        "script": ["*.js", "*.mjs"],
                        "media": ["*.mp4", "*.mp3", "*.wav", "*.avi", "*.webm"],
                    }

                    if resource_type.lower() in resource_patterns:
                        url_patterns.extend(resource_patterns[resource_type.lower()])
                        debug_logger.log_info(
                            "network_interceptor",
                            "setup_interception",
                            f"Added URL patterns for {resource_type}",
                        )
                    else:
                        url_patterns.append(resource_type)
                        debug_logger.log_info(
                            "network_interceptor",
                            "setup_interception",
                            f"Added custom URL pattern: {resource_type}",
                        )

                if url_patterns:
                    await tab.send(uc.cdp.network.set_blocked_ur_ls(urls=url_patterns))
                    debug_logger.log_info(
                        "network_interceptor",
                        "setup_interception",
                        f"Blocked {len(url_patterns)} URL patterns",
                    )

            tab.add_handler(
                uc.cdp.network.RequestWillBeSent,
                lambda event, _=None: asyncio.create_task(self._on_request(event, instance_id)),
            )
            tab.add_handler(
                uc.cdp.network.ResponseReceived,
                lambda event, _=None: asyncio.create_task(self._on_response(event, instance_id)),
            )

            async with self._lock:
                if instance_id not in self._instance_requests:
                    self._instance_requests[instance_id] = []
        except Exception as e:
            debug_logger.log_error("network_interceptor", "setup_interception", e)
            raise Exception(f"Failed to setup network interception: {str(e)}")

    async def _on_request(self, event, instance_id: str):
        """
        Handle request event.

        event: Any - The event object containing request data.
        instance_id: str - The browser instance identifier.
        """
        try:
            request_id = event.request_id
            request = event.request
            cookies = {}
            if hasattr(request, "headers") and "Cookie" in request.headers:
                cookie_str = request.headers["Cookie"]
                for cookie in cookie_str.split("; "):
                    if "=" in cookie:
                        key, value = cookie.split("=", 1)
                        cookies[key] = value
            network_request = NetworkRequest(
                request_id=request_id,
                instance_id=instance_id,
                url=request.url,
                method=request.method,
                headers=dict(request.headers) if hasattr(request, "headers") else {},
                cookies=cookies,
                post_data=request.post_data if hasattr(request, "post_data") else None,
                resource_type=event.type if hasattr(event, "type") else None,
            )
            async with self._lock:
                self._requests[request_id] = network_request
                self._instance_requests[instance_id].append(request_id)
                # Evict oldest entries if limit exceeded (prevent memory leak)
                instance_reqs = self._instance_requests[instance_id]
                if len(instance_reqs) > self.MAX_REQUESTS_PER_INSTANCE:
                    oldest_id = instance_reqs.pop(0)
                    self._requests.pop(oldest_id, None)
                    self._responses.pop(oldest_id, None)
        except Exception as e:
            debug_logger.log_warning(
                "network_interceptor", "_on_request", f"Error processing request event: {e}"
            )

    async def _on_response(self, event, instance_id: str):
        """
        Handle response event.

        event: Any - The event object containing response data.
        instance_id: str - The browser instance identifier.
        """
        try:
            request_id = event.request_id
            response = event.response
            network_response = NetworkResponse(
                request_id=request_id,
                status=response.status,
                headers=dict(response.headers) if hasattr(response, "headers") else {},
                content_type=response.mime_type if hasattr(response, "mime_type") else None,
            )
            async with self._lock:
                self._responses[request_id] = network_response
        except Exception as e:
            debug_logger.log_warning(
                "network_interceptor", "_on_response", f"Error processing response event: {e}"
            )

    async def list_requests(
        self, instance_id: str, filter_type: Optional[str] = None
    ) -> List[NetworkRequest]:
        """
        List all requests for an instance.

        instance_id: str - The browser instance identifier.
        filter_type: Optional[str] - Filter requests by resource type.
        Returns: List[NetworkRequest] - List of network requests.
        """
        async with self._lock:
            request_ids = self._instance_requests.get(instance_id, [])
            requests = []
            for req_id in request_ids:
                if req_id in self._requests:
                    request = self._requests[req_id]
                    if filter_type:
                        if (
                            request.resource_type
                            and filter_type.lower() in request.resource_type.lower()
                        ):
                            requests.append(request)
                    else:
                        requests.append(request)
            return requests

    async def get_request(self, request_id: str) -> Optional[NetworkRequest]:
        """
        Get specific request by ID.

        request_id: str - The request identifier.
        Returns: Optional[NetworkRequest] - The network request object or None.
        """
        async with self._lock:
            return self._requests.get(request_id)

    async def get_response(self, request_id: str) -> Optional[NetworkResponse]:
        """
        Get response for a request.

        request_id: str - The request identifier.
        Returns: Optional[NetworkResponse] - The network response object or None.
        """
        async with self._lock:
            return self._responses.get(request_id)

    async def get_response_body(self, tab: Tab, request_id: str) -> Optional[bytes]:
        """
        Get response body content.

        tab: Tab - The browser tab.
        request_id: str - The request identifier.
        Returns: Optional[bytes] - The response body as bytes, or None.
        """
        try:
            # Convert string to RequestId object
            request_id_obj = uc.cdp.network.RequestId(request_id)
            result = await tab.send(uc.cdp.network.get_response_body(request_id=request_id_obj))
            if result:
                body, base64_encoded = result  # Result is a tuple (body, base64Encoded)
                if base64_encoded:
                    return base64.b64decode(body)
                else:
                    return body.encode("utf-8")
        except Exception as e:
            debug_logger.log_warning(
                "network_interceptor", "get_response_body", f"Failed to get response body: {e}"
            )
        return None

    async def modify_headers(self, tab: Tab, headers: Dict[str, str]):
        """
        Modify request headers for future requests.

        tab: Tab - The browser tab.
        headers: Dict[str, str] - Headers to set.
        Returns: bool - True if successful.
        """
        try:
            # Convert dict to Headers object
            headers_obj = uc.cdp.network.Headers(headers)
            await tab.send(uc.cdp.network.set_extra_http_headers(headers=headers_obj))
            return True
        except Exception as e:
            raise Exception(f"Failed to modify headers: {str(e)}")

    async def set_user_agent(self, tab: Tab, user_agent: str):
        """
        Set custom user agent.

        tab: Tab - The browser tab.
        user_agent: str - The user agent string to set.
        Returns: bool - True if successful.
        """
        try:
            await tab.send(uc.cdp.network.set_user_agent_override(user_agent=user_agent))
            return True
        except Exception as e:
            raise Exception(f"Failed to set user agent: {str(e)}")

    async def enable_cache(self, tab: Tab, enabled: bool = True):
        """
        Enable or disable cache.

        tab: Tab - The browser tab.
        enabled: bool - True to enable cache, False to disable.
        Returns: bool - True if successful.
        """
        try:
            await tab.send(uc.cdp.network.set_cache_disabled(cache_disabled=not enabled))
            return True
        except Exception as e:
            raise Exception(f"Failed to set cache state: {str(e)}")

    async def clear_browser_cache(self, tab: Tab):
        """
        Clear browser cache.

        tab: Tab - The browser tab.
        Returns: bool - True if successful.
        """
        try:
            await tab.send(uc.cdp.network.clear_browser_cache())
            return True
        except Exception as e:
            raise Exception(f"Failed to clear cache: {str(e)}")

    async def clear_cookies(self, tab: Tab, url: Optional[str] = None):
        """
        Clear cookies.

        tab: Tab - The browser tab.
        url: Optional[str] - The URL for which to clear cookies, or None to clear all.
        Returns: bool - True if successful.
        """
        try:
            # Use JS to clear cookies first (safe, no WebSocket corruption risk)
            try:
                await asyncio.wait_for(
                    tab.evaluate("""
                        (function() {
                            var cookies = document.cookie.split(';');
                            for (var i = 0; i < cookies.length; i++) {
                                var cookie = cookies[i];
                                var eqPos = cookie.indexOf('=');
                                var name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
                                document.cookie = name + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
                            }
                        })()
                    """),
                    timeout=3.0,
                )
            except Exception as e:
                debug_logger.log_warning(
                    "network_interceptor", "clear_cookies", f"JS cookie clear failed: {e}"
                )

            # Also clear via CDP storage (best effort, don't let it corrupt WebSocket)
            try:
                await asyncio.wait_for(
                    tab.send(uc.cdp.storage.clear_cookies(browser_context_id=None)), timeout=4.0
                )
            except Exception as e:
                debug_logger.log_warning(
                    "network_interceptor",
                    "clear_cookies",
                    f"CDP clear failed (best effort): {type(e).__name__}",
                )

            return True
        except Exception as e:
            raise Exception(f"Failed to clear cookies: {str(e)}")

    async def set_cookie(self, tab: Tab, cookie: Dict[str, Any]):
        """
        Set a cookie.

        tab: Tab - The browser tab.
        cookie: Dict[str, Any] - Cookie parameters.
        Returns: bool - True if successful.
        """
        try:
            # nodriver's CDP wrapper expects `expires` to be a TimeSinceEpoch
            # (a float subclass with to_json), not a raw int.
            expires = cookie.get("expires")
            if isinstance(expires, (int, float)):
                cookie["expires"] = uc.cdp.network.TimeSinceEpoch(float(expires))
            elif isinstance(expires, str) and expires.strip().isdigit():
                cookie["expires"] = uc.cdp.network.TimeSinceEpoch(float(expires.strip()))
            same_site = cookie.get("same_site")
            if isinstance(same_site, str):
                cookie["same_site"] = uc.cdp.network.CookieSameSite(same_site)

            await asyncio.wait_for(tab.send(uc.cdp.network.set_cookie(**cookie)), timeout=10.0)
            return True
        except asyncio.TimeoutError:
            raise Exception("Timeout ao definir cookie - a página pode estar travada")
        except Exception as e:
            raise Exception(f"Failed to set cookie: {str(e)}")

    async def get_cookies(self, tab: Tab, urls: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get cookies.

        tab: Tab - The browser tab.
        urls: Optional[List[str]] - List of URLs to get cookies for, or None for all.
        Returns: List[Dict[str, Any]] - List of cookies.
        """
        cookies = []
        try:
            # Use JavaScript first — it's faster and doesn't risk corrupting
            # the nodriver WebSocket state via asyncio.wait_for cancellation.
            try:
                cookie_string = await asyncio.wait_for(tab.evaluate("document.cookie"), timeout=3.0)
                hostname = ""
                try:
                    hostname = await asyncio.wait_for(
                        tab.evaluate("window.location.hostname"), timeout=2.0
                    )
                except Exception:
                    hostname = ""

                if cookie_string and isinstance(cookie_string, str):
                    for cookie_pair in cookie_string.split("; "):
                        if "=" in cookie_pair:
                            name, value = cookie_pair.split("=", 1)
                            cookies.append(
                                {
                                    "name": name.strip(),
                                    "value": value.strip(),
                                    "domain": hostname,
                                    "path": "/",
                                }
                            )

                # If JS returned cookies, great. If empty, try CDP as supplement.
                if not cookies:
                    try:
                        result = await asyncio.wait_for(
                            tab.send(uc.cdp.storage.get_cookies(browser_context_id=None)),
                            timeout=4.0,
                        )
                        cdp_cookies = result.get("cookies", []) if isinstance(result, dict) else result
                        if isinstance(cdp_cookies, list) and cdp_cookies:
                            cookies = [to_json(cookie) for cookie in cdp_cookies]
                    except Exception as cdp_err:
                        debug_logger.log_warning(
                            "network_interceptor",
                            "get_cookies",
                            f"CDP fallback also failed: {type(cdp_err).__name__}",
                        )

            except Exception as js_err:
                debug_logger.log_warning(
                    "network_interceptor",
                    "get_cookies",
                    f"JS cookie read failed: {type(js_err).__name__}: {js_err}",
                )

            # Filter by URLs if specified
            if urls and isinstance(cookies, list):
                from urllib.parse import urlparse

                filtered = []
                for cookie in cookies:
                    cookie_domain = cookie.get("domain", "").lstrip(".")
                    for url in urls:
                        url_host = urlparse(url).hostname or ""
                        if cookie_domain in url_host or url_host.endswith(f".{cookie_domain}"):
                            filtered.append(cookie)
                            break
                return filtered

            return cookies if isinstance(cookies, list) else []

        except Exception as e:
            raise Exception(f"Failed to get cookies: {str(e)}")

    async def emulate_network_conditions(
        self,
        tab: Tab,
        offline: bool = False,
        latency: int = 0,
        download_throughput: int = -1,
        upload_throughput: int = -1,
    ):
        """
        Emulate network conditions.

        tab: Tab - The browser tab.
        offline: bool - Whether to emulate offline mode.
        latency: int - Additional latency (ms).
        download_throughput: int - Download speed (bytes/sec).
        upload_throughput: int - Upload speed (bytes/sec).
        Returns: bool - True if successful.
        """
        try:
            await tab.send(
                uc.cdp.network.emulate_network_conditions(
                    offline=offline,
                    latency=latency,
                    download_throughput=download_throughput,
                    upload_throughput=upload_throughput,
                )
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to emulate network conditions: {str(e)}")

    async def clear_instance_data(self, instance_id: str):
        """
        Clear all network data for an instance.

        instance_id: str - The browser instance identifier.
        """
        async with self._lock:
            if instance_id in self._instance_requests:
                for req_id in self._instance_requests[instance_id]:
                    self._requests.pop(req_id, None)
                    self._responses.pop(req_id, None)
                del self._instance_requests[instance_id]


def _patch_stale_imports() -> None:
    """
    The MCP server's `hot_reload()` reloads modules but does not rebind the
    imported class symbols in the server module. That means code changes in this
    module might not take effect until a full server restart.

    To make hot reload reliable, patch the previously imported class object (if
    any) so updated method implementations are used immediately.
    """
    import sys

    for mod_name in ("__main__", "server"):
        mod = sys.modules.get(mod_name)
        if not mod:
            continue
        stale_cls = getattr(mod, "NetworkInterceptor", None)
        if stale_cls and getattr(stale_cls, "__module__", None) == __name__:
            try:
                stale_cls.set_cookie = NetworkInterceptor.set_cookie  # type: ignore[attr-defined]
            except Exception:
                pass


_patch_stale_imports()
