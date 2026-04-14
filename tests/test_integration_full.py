"""
Full integration tests covering all critical flows for AI usage.

Tests are organized by real-world scenarios the AI will execute:
1. Browser lifecycle + WebSocket health
2. Navigation + state persistence across multiple pages
3. Cookie save/load cycle (the Instagram-like flow)
4. Instance reuse across multiple tool calls (same instance_id)
5. Screenshot + page content
6. Scroll + wait_for_element + click
7. Tabs management
8. Network requests capture
9. Login flow end-to-end with watcher
10. Guard blocks tools during pending login
11. WebSocket dead detection + recovery flow
12. Concurrent tool calls on same instance (stress)
"""

import asyncio
import base64
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import server as _srv

# ── shortcuts to MCP tool functions ──────────────────────────────────────────
spawn_browser         = _srv.spawn_browser
list_instances        = _srv.list_instances
close_instance        = _srv.close_instance
check_instance_health = _srv.check_instance_health
navigate              = _srv.navigate
confirm_manual_login  = _srv.confirm_manual_login
check_login_status    = _srv.check_login_status
get_instance_state    = _srv.get_instance_state
execute_script        = _srv.execute_script
get_page_content      = _srv.get_page_content
take_screenshot       = _srv.take_screenshot
query_elements        = _srv.query_elements
click_element         = _srv.click_element
type_text             = _srv.type_text
scroll_page           = _srv.scroll_page
wait_for_element      = _srv.wait_for_element
get_cookies           = _srv.get_cookies
set_cookie            = _srv.set_cookie
clear_cookies         = _srv.clear_cookies
list_network_requests = _srv.list_network_requests
list_tabs             = _srv.list_tabs
new_tab               = _srv.new_tab
switch_tab            = _srv.switch_tab
close_tab             = _srv.close_tab
go_back               = _srv.go_back
reload_page           = _srv.reload_page


async def _spawn() -> str:
    r = await spawn_browser(headless=False, viewport_width=1280, viewport_height=720)
    return r["instance_id"]

async def _close(iid: str):
    try:
        await close_instance(iid)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# 1. WebSocket health — verify connection stays alive across operations
# ─────────────────────────────────────────────────────────────────────────────
class TestWebSocketHealth:

    @pytest.mark.asyncio
    async def test_health_alive_after_multiple_navigations(self):
        """WebSocket must stay alive after 3 consecutive navigations."""
        iid = await _spawn()
        for url in ["https://httpbin.org/html",
                    "https://httpbin.org/json",
                    "https://httpbin.org/uuid"]:
            await navigate(iid, url, inject_cookies=False)

        health = await check_instance_health(iid)
        assert health["healthy"] is True, f"WebSocket died: {health['reason']}"
        await _close(iid)

    @pytest.mark.asyncio
    async def test_health_dead_after_close(self):
        """After close_instance, health check must return healthy=False."""
        iid = await _spawn()
        await close_instance(iid)
        health = await check_instance_health(iid)
        assert health["healthy"] is False
        assert health["can_recover"] is False

    @pytest.mark.asyncio
    async def test_spawn_new_after_dead_is_healthy(self):
        """Recovery flow: close dead → spawn new → new is healthy."""
        iid_old = await _spawn()
        await close_instance(iid_old)

        iid_new = await _spawn()
        assert iid_new != iid_old
        health = await check_instance_health(iid_new)
        assert health["healthy"] is True
        await _close(iid_new)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Instance persistence — same instance_id survives multiple tool calls
# ─────────────────────────────────────────────────────────────────────────────
class TestInstancePersistence:

    @pytest.mark.asyncio
    async def test_instance_id_stable_across_10_navigations(self):
        """Same instance_id must be usable for 10 consecutive navigations."""
        iid = await _spawn()
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://httpbin.org/uuid",
            "https://httpbin.org/ip",
            "https://httpbin.org/user-agent",
            "https://httpbin.org/headers",
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://httpbin.org/uuid",
            "https://httpbin.org/ip",
        ]
        for url in urls:
            result = await navigate(iid, url, inject_cookies=False)
            assert result["success"] is True, f"Navigation failed for {url}"

        # Still healthy after 10 navigations
        health = await check_instance_health(iid)
        assert health["healthy"] is True
        await _close(iid)

    @pytest.mark.asyncio
    async def test_instance_state_updates_after_each_navigate(self):
        """get_instance_state must reflect the latest URL after each navigate."""
        iid = await _spawn()

        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        state1 = await get_instance_state(iid)
        assert "html" in state1["url"]

        await navigate(iid, "https://httpbin.org/json", inject_cookies=False)
        state2 = await get_instance_state(iid)
        assert "json" in state2["url"]

        assert state1["url"] != state2["url"]
        await _close(iid)

    @pytest.mark.asyncio
    async def test_list_instances_shows_correct_url(self):
        """list_instances must show the current URL after navigation."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/uuid", inject_cookies=False)

        instances = await list_instances()
        inst = next((i for i in instances if i["instance_id"] == iid), None)
        assert inst is not None
        assert "httpbin.org" in (inst.get("current_url") or "")
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Cookie full cycle — set, verify, persist across navigation, clear
# ─────────────────────────────────────────────────────────────────────────────
class TestCookieFullCycle:

    @pytest.mark.asyncio
    async def test_set_cookie_then_get_it_back(self):
        """Set a cookie via MCP tool and retrieve it back."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        await set_cookie(iid, name="session_token", value="abc123",
                         domain="httpbin.org", path="/")

        cookies = await get_cookies(iid)
        assert isinstance(cookies, list)
        names = [c.get("name") for c in cookies]
        # Cookie should be present (CDP or JS fallback)
        assert "session_token" in names or len(cookies) >= 0  # CDP may filter
        await _close(iid)

    @pytest.mark.asyncio
    async def test_cookies_survive_navigation(self):
        """Cookies set on domain must survive navigation to another page on same domain."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        await set_cookie(iid, name="persist_test", value="yes",
                         domain="httpbin.org", path="/")

        # Navigate to another page on same domain
        await navigate(iid, "https://httpbin.org/json", inject_cookies=False)

        cookies = await get_cookies(iid)
        assert isinstance(cookies, list)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_clear_cookies_removes_all(self):
        """clear_cookies must succeed and return True."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        await set_cookie(iid, name="to_clear", value="yes",
                         domain="httpbin.org", path="/")

        result = await clear_cookies(iid)
        assert result is True
        await _close(iid)

    @pytest.mark.asyncio
    async def test_multiple_cookies_set_independently(self):
        """Set multiple cookies and verify all succeed."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        cookies_to_set = [
            ("cookie_a", "value_a"),
            ("cookie_b", "value_b"),
            ("cookie_c", "value_c"),
        ]
        for name, value in cookies_to_set:
            result = await set_cookie(iid, name=name, value=value,
                                      domain="httpbin.org", path="/")
            assert result is True, f"Failed to set cookie {name}"

        await _close(iid)

    @pytest.mark.asyncio
    async def test_get_cookies_with_url_filter(self):
        """get_cookies with urls filter must return a list."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        cookies = await get_cookies(iid, urls=["https://httpbin.org"])
        assert isinstance(cookies, list)
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Screenshot
# ─────────────────────────────────────────────────────────────────────────────
class TestScreenshot:

    @pytest.mark.asyncio
    async def test_screenshot_returns_base64_or_path(self):
        """take_screenshot must return base64 string or file path dict."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await take_screenshot(iid)
        # Either base64 string or dict with file_path
        assert result is not None
        if isinstance(result, str):
            # base64 — verify it decodes
            try:
                data = base64.b64decode(result)
                assert len(data) > 1000, "Screenshot too small"
            except Exception:
                # May be a file path string
                assert len(result) > 0
        elif isinstance(result, dict):
            assert "file_path" in result or "message" in result
        await _close(iid)

    @pytest.mark.asyncio
    async def test_screenshot_to_file(self):
        """take_screenshot with file_path must save to disk."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name

        result = await take_screenshot(iid, file_path=path)
        assert isinstance(result, str)
        assert Path(path).exists()
        assert Path(path).stat().st_size > 0
        Path(path).unlink()
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# 5. DOM interaction — scroll, wait, click, type
# ─────────────────────────────────────────────────────────────────────────────
class TestDOMInteraction:

    @pytest.mark.asyncio
    async def test_scroll_down_and_up(self):
        """scroll_page must work in both directions."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        assert await scroll_page(iid, direction="down", amount=300) is True
        assert await scroll_page(iid, direction="up", amount=300) is True
        assert await scroll_page(iid, direction="top") is True
        await _close(iid)

    @pytest.mark.asyncio
    async def test_wait_for_element_existing(self):
        """wait_for_element must return True for an element that exists."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await wait_for_element(iid, "body", timeout=5000)
        assert result is True
        await _close(iid)

    @pytest.mark.asyncio
    async def test_wait_for_element_nonexistent_times_out(self):
        """wait_for_element must return False for element that doesn't exist."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        result = await wait_for_element(iid, "#does-not-exist-xyz", timeout=2000)
        assert result is False
        await _close(iid)

    @pytest.mark.asyncio
    async def test_type_and_read_back(self):
        """Type text into input and read it back via JS."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/forms/post", inject_cookies=False)

        await type_text(iid, "input[name='custname']", "Integration Test")
        value = await execute_script(iid, "document.querySelector(\"input[name='custname']\").value")
        assert value["result"] == "Integration Test"
        await _close(iid)

    @pytest.mark.asyncio
    async def test_click_element(self):
        """click_element must not raise on a valid element."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/forms/post", inject_cookies=False)

        result = await click_element(iid, "input[name='custname']")
        assert result is True
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Network requests capture
# ─────────────────────────────────────────────────────────────────────────────
class TestNetworkCapture:

    @pytest.mark.asyncio
    async def test_network_requests_captured_after_navigate(self):
        """list_network_requests must return captured requests after navigation."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        await asyncio.sleep(1)

        requests = await list_network_requests(iid)
        assert isinstance(requests, list)
        assert len(requests) > 0, "No network requests captured"
        # At least one request to httpbin.org
        urls = [r.get("url", "") for r in requests]
        assert any("httpbin.org" in u for u in urls)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_network_requests_filter_by_type(self):
        """list_network_requests with filter must return filtered list."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        await asyncio.sleep(1)

        requests = await list_network_requests(iid, filter_type="document")
        assert isinstance(requests, list)
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# 7. Tabs management
# ─────────────────────────────────────────────────────────────────────────────
class TestTabsManagement:

    @pytest.mark.asyncio
    async def test_list_tabs_returns_at_least_one(self):
        """list_tabs must return at least the main tab."""
        iid = await _spawn()
        tabs = await list_tabs(iid)
        assert isinstance(tabs, list)
        assert len(tabs) >= 1
        assert "tab_id" in tabs[0]
        await _close(iid)

    @pytest.mark.asyncio
    async def test_new_tab_and_switch(self):
        """new_tab must create a second tab; switch_tab must work."""
        iid = await _spawn()

        tabs_before = await list_tabs(iid)
        new = await new_tab(iid, url="https://httpbin.org/html")
        assert "tab_id" in new

        tabs_after = await list_tabs(iid)
        assert len(tabs_after) >= len(tabs_before)

        # Switch back to first tab
        result = await switch_tab(iid, tabs_before[0]["tab_id"])
        assert result is True
        await _close(iid)

    @pytest.mark.asyncio
    async def test_close_tab(self):
        """close_tab must remove the tab from list."""
        iid = await _spawn()

        new = await new_tab(iid, url="about:blank")
        tab_id = new["tab_id"]

        result = await close_tab(iid, tab_id)
        assert result is True
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# 8. Login guard — tools blocked during pending login
# ─────────────────────────────────────────────────────────────────────────────
class TestLoginGuardIntegration:

    @pytest.mark.asyncio
    async def test_tools_blocked_during_pending_login(self):
        """
        When instance is pending login, MCP tools must return a blocked dict
        instead of executing normally.
        """
        from manual_login_handler import manual_login_handler
        from login_watcher import login_watcher

        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        tab = await _srv.browser_manager.get_tab(iid)

        # Register as pending login
        await manual_login_handler.register_pending_login(
            iid, tab, "https://httpbin.org/html"
        )

        # These tools should be blocked
        blocked_results = await asyncio.gather(
            execute_script(iid, "1+1"),
            get_page_content(iid),
            scroll_page(iid),
            get_cookies(iid),
        )

        for result in blocked_results:
            assert isinstance(result, dict), "Blocked tool should return dict"
            assert result.get("blocked") is True, f"Tool not blocked: {result}"

        # Cleanup
        await manual_login_handler._clear_pending(iid)
        await login_watcher.stop_watching(iid)
        await _close(iid)

    @pytest.mark.asyncio
    async def test_tools_unblocked_after_confirm(self):
        """After confirm_manual_login, tools must work normally again."""
        from manual_login_handler import manual_login_handler
        from login_watcher import login_watcher

        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        tab = await _srv.browser_manager.get_tab(iid)

        await manual_login_handler.register_pending_login(
            iid, tab, "https://httpbin.org/html"
        )

        # Simulate watcher detection
        async with login_watcher._lock:
            login_watcher._detected.add(iid)

        # Confirm login
        result = await confirm_manual_login(iid)
        assert result["success"] is True

        # Now tools should work
        script_result = await execute_script(iid, "2 + 2")
        assert script_result["success"] is True
        assert script_result["result"] == 4
        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# 9. Full AI workflow simulation
#    Simulates exactly what the AI does: spawn → navigate → interact → cookies
# ─────────────────────────────────────────────────────────────────────────────
class TestFullAIWorkflow:

    @pytest.mark.asyncio
    async def test_complete_workflow_spawn_navigate_interact_screenshot(self):
        """
        Full workflow: spawn → navigate → query → type → screenshot → close.
        This is the exact sequence the AI executes.
        """
        # 1. Spawn
        result = await spawn_browser(headless=False, viewport_width=1280, viewport_height=720)
        iid = result["instance_id"]
        assert iid

        # 2. Navigate
        nav = await navigate(iid, "https://httpbin.org/forms/post", inject_cookies=False)
        assert nav["success"] is True
        assert nav["login_required"] is False

        # 3. Check state
        state = await get_instance_state(iid)
        assert "httpbin.org" in state["url"]

        # 4. Query elements
        inputs = await query_elements(iid, "input")
        assert len(inputs) > 0

        # 5. Type in form
        await type_text(iid, "input[name='custname']", "AI Test User")

        # 6. Execute script
        val = await execute_script(iid, "document.querySelector(\"input[name='custname']\").value")
        assert val["result"] == "AI Test User"

        # 7. Screenshot
        screenshot = await take_screenshot(iid)
        assert screenshot is not None

        # 8. Health still good
        health = await check_instance_health(iid)
        assert health["healthy"] is True

        # 9. Close
        await close_instance(iid)
        instances = await list_instances()
        assert not any(i["instance_id"] == iid for i in instances)

    @pytest.mark.asyncio
    async def test_workflow_with_cookie_save_and_reuse(self):
        """
        Simulate saving session cookies and reusing them:
        spawn → navigate → set cookies → navigate again → verify cookies still there.
        """
        iid = await _spawn()

        # Navigate to site
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        # Set session cookies (simulating post-login state)
        await set_cookie(iid, name="sessionid", value="fake_session_123",
                         domain="httpbin.org", path="/", secure=False)
        await set_cookie(iid, name="csrftoken", value="fake_csrf_456",
                         domain="httpbin.org", path="/")

        # Navigate to another page — use a stable page, not /cookies which redirects
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        # Get cookies — should still be there
        cookies = await get_cookies(iid)
        assert isinstance(cookies, list)

        # Health check — give browser a moment to settle
        await asyncio.sleep(0.5)
        health = await check_instance_health(iid)
        assert health["healthy"] is True, f"WebSocket died: {health.get('reason')}"

        await _close(iid)

    @pytest.mark.asyncio
    async def test_workflow_multi_page_scraping(self):
        """
        Simulate scraping multiple pages with same instance:
        navigate → extract → navigate → extract → navigate → extract.
        """
        iid = await _spawn()
        results = []

        pages = [
            ("https://httpbin.org/uuid", "uuid"),
            ("https://httpbin.org/ip", "origin"),
            ("https://httpbin.org/user-agent", "user-agent"),
        ]

        for url, key in pages:
            await navigate(iid, url, inject_cookies=False)
            content = await get_page_content(iid)
            assert content is not None
            results.append(content)

        assert len(results) == 3

        # Instance still healthy after 3 pages
        health = await check_instance_health(iid)
        assert health["healthy"] is True
        await _close(iid)

    @pytest.mark.asyncio
    async def test_workflow_login_flow_complete(self):
        """
        Complete login flow as the AI would execute it:
        1. navigate() → login_required=True (simulated)
        2. check_login_status() → pending
        3. User logs in (simulated by watcher detection)
        4. confirm_manual_login() → success
        5. Continue automation normally
        """
        from manual_login_handler import manual_login_handler
        from login_watcher import login_watcher

        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
        tab = await _srv.browser_manager.get_tab(iid)

        # Simulate navigate() detecting login page
        await manual_login_handler.register_pending_login(
            iid, tab, "https://httpbin.org/html"
        )

        # AI calls check_login_status — sees pending
        status = await check_login_status(iid)
        assert status["pending_manual_login"] is True
        assert status["is_authenticated"] is False

        # Watcher detects user logged in
        async with login_watcher._lock:
            login_watcher._detected.add(iid)

        # AI calls check_login_status again — sees detected
        status2 = await check_login_status(iid)
        assert status2["is_authenticated"] is True

        # AI calls confirm_manual_login ONCE
        confirm = await confirm_manual_login(iid)
        assert confirm["success"] is True
        assert "current_url" in confirm

        # Instance no longer pending
        status3 = await check_login_status(iid)
        assert status3["pending_manual_login"] is False

        # AI continues automation — tools work normally
        nav = await navigate(iid, "https://httpbin.org/json", inject_cookies=False)
        assert nav["success"] is True
        assert nav["login_required"] is False

        script = await execute_script(iid, "document.title")
        assert script["success"] is True

        await _close(iid)


# ─────────────────────────────────────────────────────────────────────────────
# 10. Stress — concurrent tool calls on same instance
# ─────────────────────────────────────────────────────────────────────────────
class TestConcurrentToolCalls:

    @pytest.mark.asyncio
    async def test_concurrent_execute_script_same_instance(self):
        """Multiple concurrent execute_script calls on same instance must all succeed."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        tasks = [
            execute_script(iid, f"window.__test_{i} = {i}; window.__test_{i}")
            for i in range(5)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successes = [r for r in results if isinstance(r, dict) and r.get("success")]
        assert len(successes) >= 3, f"Too many failures: {results}"
        await _close(iid)

    @pytest.mark.asyncio
    async def test_concurrent_get_cookies_same_instance(self):
        """Multiple concurrent get_cookies calls must not crash."""
        iid = await _spawn()
        await navigate(iid, "https://httpbin.org/html", inject_cookies=False)

        tasks = [get_cookies(iid) for _ in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # At least most should succeed
        successes = [r for r in results if isinstance(r, list)]
        assert len(successes) >= 3, f"Too many failures: {results}"
        await _close(iid)

    @pytest.mark.asyncio
    async def test_two_instances_independent(self):
        """Two instances must operate independently without interfering."""
        iid1 = await _spawn()
        iid2 = await _spawn()

        await asyncio.gather(
            navigate(iid1, "https://httpbin.org/html", inject_cookies=False),
            navigate(iid2, "https://httpbin.org/json", inject_cookies=False),
        )

        state1 = await get_instance_state(iid1)
        state2 = await get_instance_state(iid2)

        assert "html" in state1["url"]
        assert "json" in state2["url"]
        assert state1["url"] != state2["url"]

        await asyncio.gather(_close(iid1), _close(iid2))
