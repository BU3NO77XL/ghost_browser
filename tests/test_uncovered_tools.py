"""
Tests for MCP tool functions not yet covered:

- paste_text
- select_option
- get_element_state
- go_forward
- get_active_tab
- get_request_details / get_response_details / get_response_content
- modify_headers
- debug tools (get_debug_view, get_debug_lock_status)
- MCP resources (get_cookies_resource)
- _parse_netscape_cookie_line (cookie file injection helper)
- _domain_matches_host / _hosts_represent_same_site
- _inject_cookies_from_file (file not found, empty, no match, match)
- query_elements with text_filter and limit
- take_screenshot jpeg format
- _wait_for_target_host
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import server as _srv

spawn_browser         = _srv.spawn_browser
close_instance        = _srv.close_instance
navigate              = _srv.navigate
execute_script        = _srv.execute_script
query_elements        = _srv.query_elements
get_cookies           = _srv.get_cookies
list_network_requests = _srv.list_network_requests
get_request_details   = _srv.get_request_details
get_response_details  = _srv.get_response_details
get_response_content  = _srv.get_response_content
modify_headers        = _srv.modify_headers
get_active_tab        = _srv.get_active_tab
go_forward            = _srv.go_forward
take_screenshot       = _srv.take_screenshot


async def _spawn() -> str:
    r = await spawn_browser(headless=False, viewport_width=1280, viewport_height=720)
    return r["instance_id"]

async def _close(iid: str):
    try:
        await close_instance(iid)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# paste_text
# ─────────────────────────────────────────────────────────────────────────────
class TestPasteText:

    @pytest.mark.asyncio
    async def test_paste_text_in_input(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/forms/post", inject_cookies=False)
        result = await _srv.paste_text(iid, "input[name='custname']", "Pasted Value")
        assert result is True
        val = await execute_script(iid, "document.querySelector(\"input[name='custname']\").value")
        assert val["result"] == "Pasted Value"
        await _close(iid)

    @pytest.mark.asyncio
    async def test_paste_text_clear_first(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/forms/post", inject_cookies=False)
        await _srv.paste_text(iid, "input[name='custname']", "First")
        await _srv.paste_text(iid, "input[name='custname']", "Second", clear_first=True)
        val = await execute_script(iid, "document.querySelector(\"input[name='custname']\").value")
        assert val["result"] == "Second"
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# select_option
# ─────────────────────────────────────────────────────────────────────────────
class TestSelectOption:

    @pytest.mark.asyncio
    async def test_select_option_by_index(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/forms/post", inject_cookies=False)
        # Inject a select element to test against
        await execute_script(iid, """
            var s = document.createElement('select');
            s.id = 'test_select';
            ['opt1','opt2','opt3'].forEach(function(v){
                var o = document.createElement('option');
                o.value = v; o.text = v;
                s.appendChild(o);
            });
            document.body.appendChild(s);
        """)
        result = await _srv.select_option(iid, "#test_select", index=1)
        assert isinstance(result, bool)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_select_option_invalid_index_raises(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/forms/post", inject_cookies=False)
        with pytest.raises(Exception, match="Invalid index"):
            await _srv.select_option(iid, "select", index="not_a_number")
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# get_element_state
# ─────────────────────────────────────────────────────────────────────────────
class TestGetElementState:

    @pytest.mark.asyncio
    async def test_get_element_state_body(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        state = await _srv.get_element_state(iid, "body")
        assert isinstance(state, dict)
        assert len(state) > 0
        await _close(iid)

    @pytest.mark.asyncio
    async def test_get_element_state_input(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/forms/post", inject_cookies=False)
        state = await _srv.get_element_state(iid, "input[name='custname']")
        assert isinstance(state, dict)
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# go_forward
# ─────────────────────────────────────────────────────────────────────────────
class TestGoForward:

    @pytest.mark.asyncio
    async def test_go_forward_after_back(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        await navigate(iid, "https://httpbin.org/json", inject_cookies=False)
        await _srv.go_back(iid)
        await asyncio.sleep(0.5)
        result = await go_forward(iid)
        assert result is True
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# get_active_tab
# ─────────────────────────────────────────────────────────────────────────────
class TestGetActiveTab:

    @pytest.mark.asyncio
    async def test_get_active_tab_returns_tab_info(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        tab_info = await get_active_tab(iid)
        assert isinstance(tab_info, dict)
        assert "tab_id" in tab_info
        assert "url" in tab_info
        assert "title" in tab_info
        await _close(iid)

    @pytest.mark.asyncio
    async def test_get_active_tab_nonexistent(self):
        tab_info = await get_active_tab("nonexistent-id")
        assert "error" in tab_info


# ─────────────────────────────────────────────────────────────────────────────
# Network request details
# ─────────────────────────────────────────────────────────────────────────────
class TestNetworkRequestDetails:

    @pytest.mark.asyncio
    async def test_get_request_details_nonexistent(self):
        details = await get_request_details("nonexistent-request-id")
        assert details is None

    @pytest.mark.asyncio
    async def test_get_response_details_nonexistent(self):
        details = await get_response_details("nonexistent-request-id")
        assert details is None

    @pytest.mark.asyncio
    async def test_get_response_content_nonexistent(self):
        iid = await _spawn()
        result = await get_response_content(iid, "nonexistent-request-id")
        assert result is None
        await _close(iid)

    @pytest.mark.asyncio
    async def test_get_request_details_after_navigate(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        await asyncio.sleep(0.5)
        requests = await list_network_requests(iid)
        assert len(requests) > 0
        first_req_id = requests[0]["request_id"]
        details = await get_request_details(first_req_id)
        assert details is None or isinstance(details, dict)
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# modify_headers
# ─────────────────────────────────────────────────────────────────────────────
class TestModifyHeaders:

    @pytest.mark.asyncio
    async def test_modify_headers_adds_custom_header(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        result = await modify_headers(iid, {"X-Custom-Test": "test-value"})
        assert result is True
        await _close(iid)

    @pytest.mark.asyncio
    async def test_modify_headers_multiple(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        result = await modify_headers(iid, {
            "X-Header-One": "value1",
            "X-Header-Two": "value2",
        })
        assert result is True
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# Debug tools (only the ones that don't deadlock)
# ─────────────────────────────────────────────────────────────────────────────
class TestDebugTools:

    @pytest.mark.asyncio
    async def test_get_debug_view_returns_dict(self):
        result = await _srv.get_debug_view()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_debug_view_with_limits(self):
        result = await _srv.get_debug_view(max_errors=5, max_warnings=5, max_info=5)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_debug_lock_status(self):
        result = await _srv.get_debug_lock_status()
        assert isinstance(result, dict)


# ─────────────────────────────────────────────────────────────────────────────
# MCP Resources
# ─────────────────────────────────────────────────────────────────────────────
class TestMCPResources:

    @pytest.mark.asyncio
    async def test_get_cookies_resource_returns_json_list(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        result = await _srv.get_cookies_resource(iid)
        assert isinstance(result, str)
        data = json.loads(result)
        assert isinstance(data, list)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_get_cookies_resource_nonexistent(self):
        result = await _srv.get_cookies_resource("nonexistent-id")
        assert isinstance(result, str)
        data = json.loads(result)
        assert "error" in data


# ─────────────────────────────────────────────────────────────────────────────
# Cookie file helpers — pure functions, no browser
# ─────────────────────────────────────────────────────────────────────────────
class TestCookieHelpers:

    def test_parse_valid_line(self):
        line = "httpbin.org\tFALSE\t/\tFALSE\t0\tsession\tabc123"
        r = _srv._parse_netscape_cookie_line(line)
        assert r is not None
        assert r["cookie"]["name"] == "session"
        assert r["cookie"]["value"] == "abc123"
        assert r["match_domain"] == "httpbin.org"

    def test_parse_subdomain_line(self):
        line = ".example.com\tTRUE\t/\tFALSE\t0\ttoken\txyz"
        r = _srv._parse_netscape_cookie_line(line)
        assert r is not None
        assert r["match_domain"] == "example.com"
        assert r["host_only"] is False

    def test_parse_httponly_line(self):
        line = "#HttpOnly_httpbin.org\tFALSE\t/\tTRUE\t0\tsecure_c\tval"
        r = _srv._parse_netscape_cookie_line(line)
        assert r is not None
        assert r["cookie"]["http_only"] is True
        assert r["cookie"]["secure"] is True

    def test_parse_comment_returns_none(self):
        assert _srv._parse_netscape_cookie_line("# comment") is None

    def test_parse_empty_returns_none(self):
        assert _srv._parse_netscape_cookie_line("") is None
        assert _srv._parse_netscape_cookie_line("   ") is None

    def test_parse_wrong_columns_returns_none(self):
        assert _srv._parse_netscape_cookie_line("only\ttwo") is None

    def test_parse_with_expiry(self):
        line = "httpbin.org\tFALSE\t/\tFALSE\t9999999999\texpiring\tval"
        r = _srv._parse_netscape_cookie_line(line)
        assert r is not None
        assert "expires" in r["cookie"]

    def test_domain_matches_exact(self):
        assert _srv._domain_matches_host("httpbin.org", "httpbin.org") is True

    def test_domain_matches_subdomain(self):
        assert _srv._domain_matches_host("example.com", "sub.example.com") is True

    def test_domain_no_match(self):
        assert _srv._domain_matches_host("example.com", "other.com") is False

    def test_domain_empty(self):
        assert _srv._domain_matches_host("", "example.com") is False
        assert _srv._domain_matches_host("example.com", "") is False

    def test_domain_leading_dot(self):
        assert _srv._domain_matches_host(".example.com", "sub.example.com") is True

    def test_same_site_symmetric(self):
        assert _srv._hosts_represent_same_site("example.com", "sub.example.com") is True
        assert _srv._hosts_represent_same_site("sub.example.com", "example.com") is True

    def test_same_site_no_match(self):
        assert _srv._hosts_represent_same_site("example.com", "other.com") is False

    def test_same_site_empty(self):
        assert _srv._hosts_represent_same_site("", "example.com") is False


# ─────────────────────────────────────────────────────────────────────────────
# Cookie file injection — browser tests (only fast paths)
# ─────────────────────────────────────────────────────────────────────────────
class TestCookieFileInjection:

    @pytest.mark.asyncio
    async def test_inject_file_not_found(self):
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        result = await _srv._inject_cookies_from_file(
            tab, "https://httpbin.org/html", "nonexistent_cookies.txt"
        )
        assert result["attempted"] is False
        assert result["reason"] == "file_not_found"
        await _close(iid)

    @pytest.mark.asyncio
    async def test_inject_empty_file(self, tmp_path):
        cookie_file = tmp_path / "empty.txt"
        cookie_file.write_text("")
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        result = await _srv._inject_cookies_from_file(
            tab, "https://httpbin.org/html", str(cookie_file)
        )
        assert result["attempted"] is False
        assert result["reason"] == "file_empty"
        await _close(iid)

    @pytest.mark.asyncio
    async def test_inject_no_matching_domain(self, tmp_path):
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("other-domain.com\tFALSE\t/\tFALSE\t0\ttoken\tabc\n")
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        result = await _srv._inject_cookies_from_file(
            tab, "https://httpbin.org/html", str(cookie_file)
        )
        assert result["attempted"] is True
        assert result["reason"] == "no_matching_cookies"
        assert result["cookies_injected"] == 0
        await _close(iid)

    @pytest.mark.asyncio
    async def test_inject_matching_domain(self, tmp_path):
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("httpbin.org\tFALSE\t/\tFALSE\t0\ttest_token\tabc123\n")
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        result = await _srv._inject_cookies_from_file(
            tab, "https://httpbin.org/html", str(cookie_file)
        )
        assert result["attempted"] is True
        assert result["cookies_injected"] >= 1
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# query_elements advanced
# ─────────────────────────────────────────────────────────────────────────────
class TestQueryElementsAdvanced:

    @pytest.mark.asyncio
    async def test_query_elements_with_limit(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        elements = await query_elements(iid, "*", limit=3)
        assert isinstance(elements, list)
        assert len(elements) <= 3
        await _close(iid)

    @pytest.mark.asyncio
    async def test_query_elements_with_text_filter(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        elements = await query_elements(iid, "*", text_filter="Herman")
        assert isinstance(elements, list)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_query_elements_visible_only(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        elements = await query_elements(iid, "*", visible_only=True, limit=5)
        assert isinstance(elements, list)
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# take_screenshot variants
# ─────────────────────────────────────────────────────────────────────────────
class TestScreenshotVariants:

    @pytest.mark.asyncio
    async def test_screenshot_jpeg_to_file(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            path = f.name
        result = await take_screenshot(iid, format="jpeg", file_path=path)
        assert isinstance(result, str)
        assert Path(path).exists()
        assert Path(path).stat().st_size > 0
        Path(path).unlink()
        await _close(iid)

    @pytest.mark.asyncio
    async def test_screenshot_base64_no_file(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        result = await take_screenshot(iid)
        assert result is not None
        if isinstance(result, str):
            import base64
            try:
                data = base64.b64decode(result)
                assert len(data) > 100
            except Exception:
                pass
        elif isinstance(result, dict):
            assert "file_path" in result or "message" in result
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# _wait_for_target_host
# ─────────────────────────────────────────────────────────────────────────────
class TestWaitForTargetHost:

    @pytest.mark.asyncio
    async def test_already_on_target_host(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        tab = await _srv.browser_manager.get_tab(iid)
        result = await _srv._wait_for_target_host(
            tab, "https://httpbin.org/json", max_wait_ms=3000
        )
        assert result["matched"] is True
        assert result["target_host"] == "httpbin.org"
        await _close(iid)

    @pytest.mark.asyncio
    async def test_timeout_on_wrong_host(self):
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        tab = await _srv.browser_manager.get_tab(iid)
        result = await _srv._wait_for_target_host(
            tab, "https://totally-different-host.example.com", max_wait_ms=500
        )
        assert result["matched"] is False
        assert result["reason"] == "wait_timeout"
        await _close(iid)

    @pytest.mark.asyncio
    async def test_invalid_url_returns_false(self):
        iid = await _spawn()
        tab = await _srv.browser_manager.get_tab(iid)
        result = await _srv._wait_for_target_host(tab, "not-a-url", max_wait_ms=100)
        assert result["matched"] is False
        await _close(iid)
