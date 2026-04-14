"""
FINAL SMOKE TEST — Pre-integration validation.

Simulates a complete real AI session end-to-end:
  1. Spawn browser
  2. Navigate to a page
  3. Interact with DOM
  4. Execute scripts
  5. Take screenshot
  6. Set / get / clear cookies
  7. Navigate multiple pages (instance reuse)
  8. Health check throughout
  9. Login flow (detect → wait → confirm → continue)
  10. Guard blocks tools during pending login
  11. Tabs (open, switch, close)
  12. Network capture
  13. Close instance → verify gone from storage
  14. Spawn new instance after close (recovery)

All 14 steps must pass for the system to be considered production-ready.
"""

import asyncio
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import server as _srv
from manual_login_handler import manual_login_handler
from login_watcher import login_watcher
from persistent_storage import persistent_storage


# ── MCP tool shortcuts ────────────────────────────────────────────────────────
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


class TestFinalSmoke:
    """Single sequential test that walks through the entire AI workflow."""

    @pytest.mark.asyncio
    async def test_full_ai_session(self):
        iid = None
        try:
            # ── STEP 1: Spawn ─────────────────────────────────────────────────
            print("\n[1/14] Spawning browser...")
            result = await spawn_browser(headless=False, viewport_width=1280, viewport_height=720)
            iid = result["instance_id"]
            assert iid, "No instance_id returned"
            assert result["viewport"]["width"] == 1280

            # Verify in list and storage
            instances = await list_instances()
            assert any(i["instance_id"] == iid for i in instances)
            assert persistent_storage.get_instance(iid) is not None
            print(f"    OK — instance {iid[:8]}...")

            # ── STEP 2: Navigate ──────────────────────────────────────────────
            print("[2/14] Navigating to httpbin.org/html...")
            nav = await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
            assert nav["success"] is True
            assert nav["login_required"] is False
            assert "httpbin.org" in nav["url"]
            print(f"    OK — url={nav['url']}")

            # ── STEP 3: DOM interaction ───────────────────────────────────────
            print("[3/14] DOM interaction (query, scroll, wait)...")
            elements = await query_elements(iid, "body")
            assert len(elements) >= 1

            assert await scroll_page(iid, direction="down", amount=200) is True
            assert await scroll_page(iid, direction="top") is True
            assert await wait_for_element(iid, "body", timeout=3000) is True
            assert await wait_for_element(iid, "#nonexistent-xyz", timeout=1000) is False
            print("    OK")

            # ── STEP 4: Execute script ────────────────────────────────────────
            print("[4/14] Executing JavaScript...")
            r = await execute_script(iid, "2 + 2")
            assert r["success"] is True and r["result"] == 4

            r2 = await execute_script(iid, "document.title")
            assert r2["success"] is True and isinstance(r2["result"], str)

            r3 = await execute_script(iid, "window.__smoke = 'ok'; window.__smoke")
            assert r3["result"] == "ok"
            print("    OK")

            # ── STEP 5: Screenshot ────────────────────────────────────────────
            print("[5/14] Taking screenshot...")
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                spath = f.name
            shot = await take_screenshot(iid, file_path=spath)
            assert isinstance(shot, str)
            assert Path(spath).exists() and Path(spath).stat().st_size > 0
            Path(spath).unlink()
            print("    OK")

            # ── STEP 6: Cookies ───────────────────────────────────────────────
            print("[6/14] Cookie set / get / clear...")
            assert await set_cookie(iid, name="smoke_session", value="abc123",
                                    domain="httpbin.org", path="/") is True
            assert await set_cookie(iid, name="smoke_csrf", value="xyz789",
                                    domain="httpbin.org", path="/") is True

            cookies = await get_cookies(iid)
            assert isinstance(cookies, list)

            assert await clear_cookies(iid) is True
            print("    OK")

            # ── STEP 7: Navigate multiple pages (instance reuse) ──────────────
            print("[7/14] Navigating 4 more pages on same instance...")
            pages = [
                "https://httpbin.org/json",
                "https://httpbin.org/uuid",
                "https://httpbin.org/ip",
                "https://httpbin.org/html",
            ]
            for url in pages:
                r = await navigate(iid, url, inject_cookies=False)
                assert r["success"] is True, f"Failed: {url}"
            print("    OK — same instance_id used throughout")

            # ── STEP 8: Health check ──────────────────────────────────────────
            print("[8/14] WebSocket health check...")
            health = await check_instance_health(iid)
            assert health["healthy"] is True, f"WebSocket dead: {health['reason']}"
            assert health["can_recover"] is True
            print(f"    OK — {health['reason']}")

            # ── STEP 9: Instance state ────────────────────────────────────────
            print("[9/14] Instance state after navigations...")
            state = await get_instance_state(iid)
            assert state is not None
            assert "httpbin.org" in state["url"]
            assert state["ready_state"] in ("complete", "interactive", "loading")
            assert state["viewport"]["width"] > 0
            print(f"    OK — url={state['url']}")

            # ── STEP 10: Login flow ───────────────────────────────────────────
            print("[10/14] Login flow (detect -> pending -> confirm -> resume)...")
            tab = await _srv.browser_manager.get_tab(iid)

            # Register as pending (simulates navigate() detecting login page)
            await manual_login_handler.register_pending_login(
                iid, tab, "https://httpbin.org/html"
            )

            # Verify pending
            status = await check_login_status(iid)
            assert status["pending_manual_login"] is True
            assert status["is_authenticated"] is False

            # Tools must be blocked
            blocked = await execute_script(iid, "1+1")
            assert blocked.get("blocked") is True, f"Tool not blocked: {blocked}"

            # Simulate watcher detecting login
            async with login_watcher._lock:
                login_watcher._detected.add(iid)

            # Confirm login
            confirm = await confirm_manual_login(iid)
            assert confirm["success"] is True
            assert "current_url" in confirm

            # Verify unblocked
            status2 = await check_login_status(iid)
            assert status2["pending_manual_login"] is False
            assert status2["is_authenticated"] is True

            # Tools work again
            r = await execute_script(iid, "1+1")
            assert r["success"] is True and r["result"] == 2
            print("    OK — login flow complete, tools unblocked")

            # ── STEP 11: Tabs ─────────────────────────────────────────────────
            print("[11/14] Tabs (list, new, switch, close)...")
            tabs = await list_tabs(iid)
            assert len(tabs) >= 1
            original_tab_id = tabs[0]["tab_id"]

            new_t = await new_tab(iid, url="about:blank")
            assert "tab_id" in new_t

            assert await switch_tab(iid, original_tab_id) is True
            assert await close_tab(iid, new_t["tab_id"]) is True
            print("    OK")

            # ── STEP 12: Network capture ──────────────────────────────────────
            print("[12/14] Network requests capture...")
            await navigate(iid, "https://httpbin.org/html", inject_cookies=False)
            await asyncio.sleep(0.5)
            reqs = await list_network_requests(iid)
            assert isinstance(reqs, list)
            assert len(reqs) > 0
            assert any("httpbin.org" in r.get("url", "") for r in reqs)
            print(f"    OK — {len(reqs)} requests captured")

            # ── STEP 13: Close + verify gone ──────────────────────────────────
            print("[13/14] Close instance and verify cleanup...")
            assert await close_instance(iid) is True

            instances_after = await list_instances()
            assert not any(i["instance_id"] == iid for i in instances_after)
            assert persistent_storage.get_instance(iid) is None

            health_dead = await check_instance_health(iid)
            assert health_dead["healthy"] is False
            assert health_dead["can_recover"] is False
            print("    OK — instance gone from memory and storage")

            # ── STEP 14: Spawn new after close (recovery) ─────────────────────
            print("[14/14] Spawn new instance after close (recovery flow)...")
            result2 = await spawn_browser(headless=False, viewport_width=1280, viewport_height=720)
            iid2 = result2["instance_id"]
            assert iid2 != iid, "New instance must have different ID"

            health2 = await check_instance_health(iid2)
            assert health2["healthy"] is True

            nav2 = await navigate(iid2, "https://httpbin.org/html", inject_cookies=False)
            assert nav2["success"] is True

            await close_instance(iid2)
            print("    OK — new instance healthy and functional")

            print("\n[SMOKE TEST PASSED] System is ready for AI integration.")

        except Exception:
            if iid:
                try:
                    await close_instance(iid)
                except Exception:
                    pass
            raise
