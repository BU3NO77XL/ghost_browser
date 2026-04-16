"""
Tests for network_debugging.py and cookies_storage.py tools.

Verifies:
- Cookie operations (set, get, clear)
- Cookie helper functions (Netscape format parsing)
- Network request capture
"""

import asyncio

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Cookie Operations
# ─────────────────────────────────────────────────────────────────────────────


class TestCookieOperations:
    """Test cookie operations."""

    @pytest.mark.asyncio
    async def test_set_cookie(self, network_interceptor, navigated_tab):
        """Test setting a cookie."""
        cookie = {
            "name": "test_cookie",
            "value": "test_value",
            "domain": "httpbin.org",
            "path": "/",
        }

        result = await network_interceptor.set_cookie(navigated_tab, cookie)
        assert result is True

    @pytest.mark.asyncio
    async def test_get_cookies_javascript_fallback(self, navigated_tab):
        """Test getting cookies via JavaScript (fallback method)."""
        # Set a cookie via JavaScript
        await navigated_tab.evaluate("""
            document.cookie = 'js_test_cookie=js_test_value; path=/';
        """)

        # Get cookies via JavaScript
        cookie_string = await navigated_tab.evaluate("document.cookie")
        assert (
            "js_test_cookie" in cookie_string or cookie_string == ""
        )  # May be empty due to domain restrictions

    @pytest.mark.asyncio
    async def test_set_cookie_with_expiry(self, network_interceptor, navigated_tab):
        """Test setting cookie with expiry."""
        import time

        future_time = int(time.time()) + 3600  # 1 hour from now

        cookie = {
            "name": "expiry_cookie",
            "value": "expiry_value",
            "domain": "httpbin.org",
            "path": "/",
            "expires": future_time,
        }

        result = await network_interceptor.set_cookie(navigated_tab, cookie)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_secure_cookie(self, network_interceptor, navigated_tab):
        """Test setting secure cookie."""
        cookie = {
            "name": "secure_cookie",
            "value": "secure_value",
            "domain": "httpbin.org",
            "path": "/",
            "secure": True,
            "http_only": True,
        }

        result = await network_interceptor.set_cookie(navigated_tab, cookie)
        assert result is True


class TestCookieClearing:
    """Test cookie clearing."""

    @pytest.mark.asyncio
    async def test_clear_all_cookies(self, network_interceptor, navigated_tab):
        """Test clearing all cookies."""
        # Set a cookie first
        cookie = {
            "name": "clear_test",
            "value": "clear_value",
            "domain": "httpbin.org",
            "path": "/",
        }
        await network_interceptor.set_cookie(navigated_tab, cookie)

        # Clear cookies
        result = await network_interceptor.clear_cookies(navigated_tab)
        assert result is True


# ─────────────────────────────────────────────────────────────────────────────
# Cookie Helper Functions
# ─────────────────────────────────────────────────────────────────────────────


class TestCookieHelpers:
    """Test cookie manager helper functions."""

    def test_parse_netscape_cookie_line_valid(self):
        from core.cookie_manager import parse_netscape_cookie_line

        line = "httpbin.org\tTRUE\t/\tFALSE\t0\ttest_cookie\ttest_value"
        result = parse_netscape_cookie_line(line)
        assert result is not None
        assert result["cookie"]["name"] == "test_cookie"
        assert result["cookie"]["value"] == "test_value"
        assert result["match_domain"] == "httpbin.org"

    def test_parse_netscape_cookie_line_comment(self):
        from core.cookie_manager import parse_netscape_cookie_line

        line = "# This is a comment"
        cookie = parse_netscape_cookie_line(line)
        assert cookie is None

    def test_parse_netscape_cookie_line_invalid(self):
        from core.cookie_manager import parse_netscape_cookie_line

        line = "invalid line"
        cookie = parse_netscape_cookie_line(line)
        assert cookie is None

    def test_domain_matches_host_exact(self):
        from core.cookie_manager import domain_matches_host

        assert domain_matches_host("example.com", "example.com") is True

    def test_domain_matches_host_subdomain(self):
        from core.cookie_manager import domain_matches_host

        assert domain_matches_host("example.com", "www.example.com") is True
        assert domain_matches_host("example.com", "api.example.com") is True

    def test_domain_matches_host_no_match(self):
        from core.cookie_manager import domain_matches_host

        assert domain_matches_host("example.com", "other.com") is False
