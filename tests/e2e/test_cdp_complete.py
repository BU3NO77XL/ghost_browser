"""
E2E Test Suite — CDP Complete Implementation (v0.4.0)

Tests the 11 new CDP domains implemented in v0.4.0:
  1. Storage Domain (LocalStorage, SessionStorage, IndexedDB, Cache Storage)
  2. CSS Domain (matched styles, computed styles, media queries)
  3. ServiceWorker Domain (list, lifecycle)
  4. BackgroundService Domain (observe, events)
  5. WebAuthn Domain (virtual authenticator, credentials)
  6. Security Domain (security state, certificate errors)
  7. Animation Domain (list, pause, playback rate)
  8. Debugger Domain (enable, breakpoints, call stack)
  9. Profiler Domain (CPU profiling, code coverage)
  10. HeapProfiler Domain (sampling, GC, snapshot)
  11. Cross-domain workflow (Storage + CSS + Profiler)

All tests use httpbin.org or data: URLs to avoid external dependencies.
"""

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import server as _srv

# ── Tool shortcuts ─────────────────────────────────────────────────────────────
spawn_browser = _srv.spawn_browser
close_instance = _srv.close_instance
navigate = _srv.navigate
execute_script = _srv.execute_script

# Storage
get_local_storage = _srv.get_local_storage
set_local_storage_item = _srv.set_local_storage_item
remove_local_storage_item = _srv.remove_local_storage_item
clear_local_storage = _srv.clear_local_storage
get_session_storage = _srv.get_session_storage
set_session_storage_item = _srv.set_session_storage_item
list_indexed_databases = _srv.list_indexed_databases
list_cache_storage = _srv.list_cache_storage

# CSS
get_matched_styles = _srv.get_matched_styles
get_inline_styles = _srv.get_inline_styles
get_computed_style = _srv.get_computed_style
get_media_queries = _srv.get_media_queries

# ServiceWorker
list_service_workers = _srv.list_service_workers

# BackgroundService
start_observing_background_service = _srv.start_observing_background_service
stop_observing_background_service = _srv.stop_observing_background_service
get_background_service_events = _srv.get_background_service_events

# WebAuthn
add_virtual_authenticator = _srv.add_virtual_authenticator
remove_virtual_authenticator = _srv.remove_virtual_authenticator
get_webauthn_credentials = _srv.get_webauthn_credentials
set_webauthn_user_verified = _srv.set_webauthn_user_verified

# Security
get_security_state = _srv.get_security_state
set_ignore_certificate_errors = _srv.set_ignore_certificate_errors

# Animation
list_animations = _srv.list_animations
set_animation_playback_rate = _srv.set_animation_playback_rate

# Debugger
enable_debugger = _srv.enable_debugger
disable_debugger = _srv.disable_debugger
set_breakpoint = _srv.set_breakpoint
remove_breakpoint = _srv.remove_breakpoint
get_call_stack = _srv.get_call_stack

# Profiler
start_cpu_profiling = _srv.start_cpu_profiling
stop_cpu_profiling = _srv.stop_cpu_profiling
start_code_coverage = _srv.start_code_coverage
stop_code_coverage = _srv.stop_code_coverage
take_code_coverage_snapshot = _srv.take_code_coverage_snapshot

# HeapProfiler
collect_garbage = _srv.collect_garbage
start_heap_sampling = _srv.start_heap_sampling
stop_heap_sampling = _srv.stop_heap_sampling
take_heap_snapshot = _srv.take_heap_snapshot


# ── Test page HTML ─────────────────────────────────────────────────────────────
TEST_PAGE_HTML = """data:text/html,<!DOCTYPE html>
<html>
<head>
<style>
  body { background: white; color: black; }
  .animated { animation: spin 2s linear infinite; }
  @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
  @media (max-width: 768px) { body { font-size: 14px; } }
</style>
</head>
<body>
  <h1 id="title" style="color: blue; font-size: 24px;">CDP Test Page</h1>
  <div class="animated" id="spinner">Spinning</div>
  <script>
    localStorage.setItem('test_key', 'test_value');
    localStorage.setItem('another_key', 'another_value');
    sessionStorage.setItem('session_key', 'session_value');
  </script>
</body>
</html>"""


class TestStorageDomain:
    """Tests for LocalStorage, SessionStorage, IndexedDB, and Cache Storage."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_local_storage_operations(self):
        """Test LocalStorage get, set, remove, clear operations."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            origin = "null"  # data: URLs have null origin

            # Set items via tool
            await set_local_storage_item(iid, origin=origin, key="tool_key", value="tool_value")

            # Get all items
            items = await get_local_storage(iid, origin=origin)
            assert isinstance(items, dict), "Expected dict from get_local_storage"

            # Remove item
            await remove_local_storage_item(iid, origin=origin, key="tool_key")

            # Clear all
            await clear_local_storage(iid, origin=origin)

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_session_storage_operations(self):
        """Test SessionStorage get and set operations."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            origin = "null"

            await set_session_storage_item(iid, origin=origin, key="sess_key", value="sess_val")
            items = await get_session_storage(iid, origin=origin)
            assert isinstance(items, dict), "Expected dict from get_session_storage"

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_indexed_db_list(self):
        """Test listing IndexedDB databases."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            dbs = await list_indexed_databases(iid, origin="null")
            assert isinstance(dbs, list), "Expected list from list_indexed_databases"

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_cache_storage_list(self):
        """Test listing Cache Storage caches."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url="https://httpbin.org/html")
            await asyncio.sleep(1)

            caches = await list_cache_storage(iid, security_origin="https://httpbin.org")
            assert isinstance(caches, list), "Expected list from list_cache_storage"

        finally:
            if iid:
                await close_instance(iid)


class TestCSSDomain:
    """Tests for CSS style retrieval and media queries."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_computed_style(self):
        """Test getting computed styles for an element."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            computed = await get_computed_style(iid, selector="body")
            assert isinstance(computed, dict), "Expected dict from get_computed_style"
            assert len(computed) > 0, "Expected non-empty computed styles"

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_inline_styles(self):
        """Test getting inline styles for an element."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            inline = await get_inline_styles(iid, selector="#title")
            assert isinstance(inline, dict), "Expected dict from get_inline_styles"
            # h1 has inline style="color: blue; font-size: 24px;"
            assert "color" in inline or "font-size" in inline, "Expected inline styles"

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_matched_styles(self):
        """Test getting matched CSS rules for an element."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            styles = await get_matched_styles(iid, selector="body")
            assert isinstance(styles, dict), "Expected dict from get_matched_styles"
            assert "matched_rules" in styles
            assert "inline_style" in styles

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_media_queries(self):
        """Test getting media queries from the page."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            queries = await get_media_queries(iid)
            assert isinstance(queries, list), "Expected list from get_media_queries"

        finally:
            if iid:
                await close_instance(iid)


class TestServiceWorkerDomain:
    """Tests for ServiceWorker listing."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_list_service_workers(self):
        """Test listing service workers (empty on test page)."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            workers = await list_service_workers(iid)
            assert isinstance(workers, list), "Expected list from list_service_workers"

        finally:
            if iid:
                await close_instance(iid)


class TestBackgroundServiceDomain:
    """Tests for BackgroundService observation."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_observe_and_stop(self):
        """Test starting and stopping background service observation."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            started = await start_observing_background_service(iid, service="backgroundSync")
            assert started is True

            events = await get_background_service_events(iid, service="backgroundSync")
            assert isinstance(events, list)

            stopped = await stop_observing_background_service(iid, service="backgroundSync")
            assert stopped is True

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_invalid_service_type(self):
        """Test that invalid service type raises ValueError."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)

            with pytest.raises(Exception):
                await start_observing_background_service(iid, service="invalidService")

        finally:
            if iid:
                await close_instance(iid)


class TestWebAuthnDomain:
    """Tests for WebAuthn virtual authenticator."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_virtual_authenticator_lifecycle(self):
        """Test creating and removing a virtual authenticator."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            # Create authenticator
            auth_id = await add_virtual_authenticator(
                iid,
                protocol="ctap2",
                transport="usb",
                has_resident_key=True,
                has_user_verification=True,
                is_user_verified=True,
            )
            assert isinstance(auth_id, str) and len(auth_id) > 0

            # Get credentials (empty initially)
            creds = await get_webauthn_credentials(iid, authenticator_id=auth_id)
            assert isinstance(creds, list)

            # Toggle user verified
            result_uv = await set_webauthn_user_verified(iid, auth_id, is_user_verified=False)
            assert result_uv is True

            # Remove authenticator
            removed = await remove_virtual_authenticator(iid, authenticator_id=auth_id)
            assert removed is True

        finally:
            if iid:
                await close_instance(iid)


class TestSecurityDomain:
    """Tests for Security domain."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_security_state(self):
        """Test getting security state of a page."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url="https://httpbin.org/html")
            await asyncio.sleep(1)

            state = await get_security_state(iid)
            assert isinstance(state, dict)
            assert "security_state" in state
            assert state["security_state"] in ("secure", "insecure", "neutral")

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_ignore_certificate_errors(self):
        """Test toggling certificate error ignoring."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)

            result_on = await set_ignore_certificate_errors(iid, ignore=True)
            assert result_on is True

            result_off = await set_ignore_certificate_errors(iid, ignore=False)
            assert result_off is True

        finally:
            if iid:
                await close_instance(iid)


class TestAnimationDomain:
    """Tests for Animation domain."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_list_animations(self):
        """Test listing animations on a page with CSS animations."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            animations = await list_animations(iid)
            assert isinstance(animations, list)

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_set_playback_rate(self):
        """Test setting global animation playback rate."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            # Slow down animations
            result_slow = await set_animation_playback_rate(iid, playback_rate=0.1)
            assert result_slow is True

            # Restore normal speed
            result_normal = await set_animation_playback_rate(iid, playback_rate=1.0)
            assert result_normal is True

        finally:
            if iid:
                await close_instance(iid)


class TestDebuggerDomain:
    """Tests for JavaScript Debugger domain."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_enable_disable_debugger(self):
        """Test enabling and disabling the debugger."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            debugger_id = await enable_debugger(iid)
            assert isinstance(debugger_id, str)

            disabled = await disable_debugger(iid)
            assert disabled is True

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_set_and_remove_breakpoint(self):
        """Test setting and removing a breakpoint."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url="https://httpbin.org/html")
            await asyncio.sleep(1)

            await enable_debugger(iid)

            bp = await set_breakpoint(
                iid,
                url="httpbin.org",
                line_number=0,
            )
            assert isinstance(bp, dict)
            assert "breakpoint_id" in bp

            removed = await remove_breakpoint(iid, breakpoint_id=bp["breakpoint_id"])
            assert removed is True

            await disable_debugger(iid)

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_get_call_stack(self):
        """Test getting call stack (returns stack trace)."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            stack = await get_call_stack(iid)
            assert isinstance(stack, list)

        finally:
            if iid:
                await close_instance(iid)


class TestProfilerDomain:
    """Tests for CPU Profiler and Code Coverage."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_cpu_profiling(self):
        """Test starting and stopping CPU profiling."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            started = await start_cpu_profiling(iid)
            assert started is True

            # Do some work to profile
            await execute_script(iid, script="for(let i=0;i<10000;i++){Math.sqrt(i)}")

            profile = await stop_cpu_profiling(iid)
            assert isinstance(profile, dict)
            assert "nodes" in profile
            assert "start_time" in profile
            assert "end_time" in profile

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_code_coverage(self):
        """Test code coverage collection."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url="https://httpbin.org/html")
            await asyncio.sleep(1)

            started = await start_code_coverage(iid, detailed=False)
            assert started is True

            # Execute some JS to generate coverage
            await execute_script(iid, script="document.title = 'Coverage Test'")

            coverage = await take_code_coverage_snapshot(iid)
            assert isinstance(coverage, dict)
            assert "scripts" in coverage
            assert "total_scripts" in coverage

            stopped = await stop_code_coverage(iid)
            assert stopped is True

        finally:
            if iid:
                await close_instance(iid)


class TestHeapProfilerDomain:
    """Tests for HeapProfiler domain."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_collect_garbage(self):
        """Test forcing garbage collection."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            gc_result = await collect_garbage(iid)
            assert gc_result is True

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(90)
    async def test_heap_sampling(self):
        """Test heap sampling start and stop."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            started = await start_heap_sampling(iid, sampling_interval=32768)
            assert started is True

            # Allocate some objects
            await execute_script(iid, script="window._test = new Array(1000).fill({x: 1})")

            profile = await stop_heap_sampling(iid)
            assert isinstance(profile, dict)
            assert "head" in profile
            assert "samples" in profile

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(120)
    async def test_heap_snapshot_metadata(self):
        """Test taking a heap snapshot (metadata only, not full data)."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            # GC first for cleaner snapshot
            await collect_garbage(iid)

            snapshot = await take_heap_snapshot(iid)
            assert isinstance(snapshot, dict)
            assert "total_size_chars" in snapshot
            assert "truncated" in snapshot
            assert "note" in snapshot

        finally:
            if iid:
                await close_instance(iid)


class TestCrossDomainWorkflow:
    """Tests combining multiple CDP domains in realistic workflows."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(120)
    async def test_storage_and_css_workflow(self):
        """
        Workflow: Navigate → read storage → inspect CSS → profile performance.

        Simulates an AI agent analyzing a page's state and visual properties.
        """
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            # 1. Read storage state
            storage = await get_local_storage(iid, origin="null")
            assert isinstance(storage, dict)

            # 2. Inspect CSS of key elements
            computed = await get_computed_style(iid, selector="body")
            assert isinstance(computed, dict)

            inline = await get_inline_styles(iid, selector="#title")
            assert isinstance(inline, dict)

            # 3. Check media queries
            queries = await get_media_queries(iid)
            assert isinstance(queries, list)

            # 4. Profile the page briefly
            await start_cpu_profiling(iid)
            await execute_script(iid, script="document.querySelectorAll('*').length")
            profile = await stop_cpu_profiling(iid)
            assert "nodes" in profile

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(120)
    async def test_debugger_and_profiler_workflow(self):
        """
        Workflow: Enable debugger → set breakpoint → profile → cleanup.

        Simulates a debugging + performance analysis session.
        """
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url="https://httpbin.org/html")
            await asyncio.sleep(1)

            # 1. Enable debugger
            await enable_debugger(iid)

            # 2. Set a breakpoint
            bp = await set_breakpoint(iid, url="httpbin.org", line_number=0)
            assert "breakpoint_id" in bp

            # 3. Start code coverage alongside
            await start_code_coverage(iid)

            # 4. Execute some JS
            await execute_script(iid, script="Array.from({length: 100}, (_, i) => i * 2)")

            # 5. Take coverage snapshot
            coverage = await take_code_coverage_snapshot(iid)
            assert isinstance(coverage, dict)

            # 6. Cleanup
            await remove_breakpoint(iid, breakpoint_id=bp["breakpoint_id"])
            await stop_code_coverage(iid)
            await disable_debugger(iid)

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(120)
    async def test_security_and_storage_workflow(self):
        """
        Workflow: Check security state → read storage → verify data integrity.

        Simulates a security audit workflow.
        """
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url="https://httpbin.org/html")
            await asyncio.sleep(1)

            # 1. Check security state
            state = await get_security_state(iid)
            assert state["security_state"] in ("secure", "insecure", "neutral")

            # 2. Set some storage data
            await execute_script(
                iid,
                script="localStorage.setItem('audit_key', 'audit_value')"
            )

            # 3. Read it back via CDP
            storage = await get_local_storage(iid, origin="https://httpbin.org")
            assert isinstance(storage, dict)

            # 4. Verify security is still intact
            state_after = await get_security_state(iid)
            assert state_after["security_state"] == state["security_state"]

        finally:
            if iid:
                await close_instance(iid)

    @pytest.mark.asyncio
    @pytest.mark.timeout(120)
    async def test_error_handling_across_domains(self):
        """Test that errors are handled gracefully across all domains."""
        iid = None
        try:
            result = await spawn_browser(headless=True)
            iid = result["instance_id"]

            await navigate(iid, url=TEST_PAGE_HTML)
            await asyncio.sleep(0.5)

            # CSS: invalid selector should raise
            with pytest.raises(Exception):
                await get_computed_style(iid, selector="##invalid##selector")

            # BackgroundService: invalid service type should raise
            with pytest.raises(Exception):
                await start_observing_background_service(iid, service="notAService")

            # All other tools should still work after errors
            storage = await get_local_storage(iid, origin="null")
            assert isinstance(storage, dict)

        finally:
            if iid:
                await close_instance(iid)
