"""Cookie and storage management tools."""

from typing import Any, Dict, List, Optional

from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]
    network_interceptor = deps["network_interceptor"]

    @section_tool("cookies-storage")
    async def get_cookies(
        instance_id: str, urls: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cookies for current page or specific URLs.

        Args:
            instance_id (str): Browser instance ID.
            urls (Optional[List[str]]): Optional list of URLs to get cookies for.

        Returns:
            List[Dict[str, Any]]: List of cookies.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await network_interceptor.get_cookies(tab, urls)

    @section_tool("cookies-storage")
    async def set_cookie(
        instance_id: str,
        name: str,
        value: str,
        url: Optional[str] = None,
        domain: Optional[str] = None,
        path: str = "/",
        secure: bool = False,
        http_only: bool = False,
        same_site: Optional[str] = None,
    ) -> bool:
        """
        Set a cookie.

        Args:
            instance_id (str): Browser instance ID.
            name (str): Cookie name.
            value (str): Cookie value.
            url (Optional[str]): The request-URI to associate with the cookie.
            domain (Optional[str]): Cookie domain.
            path (str): Cookie path.
            secure (bool): Secure flag.
            http_only (bool): HttpOnly flag.
            same_site (Optional[str]): SameSite attribute ('Strict', 'Lax', or 'None').

        Returns:
            bool: True if set successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")

        if not url and not domain:
            current_url = tab.url if hasattr(tab, "url") else None
            if current_url:
                url = current_url
            else:
                raise Exception("At least one of 'url' or 'domain' must be specified")

        cookie = {
            "name": name,
            "value": value,
            "path": path,
            "secure": secure,
            "http_only": http_only,
        }
        if url:
            cookie["url"] = url
        if domain:
            cookie["domain"] = domain
        if same_site:
            cookie["same_site"] = same_site
        return await network_interceptor.set_cookie(tab, cookie)

    @section_tool("cookies-storage")
    async def clear_cookies(instance_id: str, url: Optional[str] = None) -> bool:
        """
        Clear cookies.

        Args:
            instance_id (str): Browser instance ID.
            url (Optional[str]): Optional URL to clear cookies for (clears all if not specified).

        Returns:
            bool: True if cleared successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await network_interceptor.clear_cookies(tab, url)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
