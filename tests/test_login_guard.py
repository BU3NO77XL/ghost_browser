"""
Tests for the login guard mechanism.

Verifies that:
- _check_pending_login_guard blocks tools when login is pending
- confirm_manual_login clears the pending state
- The watcher detection flag is consumed correctly
- Tools are unblocked after login confirmation
"""

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from manual_login_handler import manual_login_handler
from login_watcher import login_watcher


# Simulate the guard function from server.py (same logic, no server import needed)
async def _check_pending_login_guard(instance_id: str):
    if not await manual_login_handler.is_pending_login(instance_id):
        return None
    pending = await manual_login_handler.get_pending_info(instance_id)
    return {
        "blocked": True,
        "reason": "INSTANCE_PENDING_MANUAL_LOGIN",
        "instance_id": instance_id,
        "pending_since": pending.get("registered_at") if pending else None,
    }


class TestLoginGuard:
    """Test that the login guard correctly blocks/unblocks tool execution."""

    @pytest.mark.asyncio
    async def test_guard_passes_when_no_pending_login(self):
        """Guard should return None (allow) when no login is pending."""
        result = await _check_pending_login_guard("non-pending-instance")
        assert result is None, "Guard should pass (return None) when no login pending"

    @pytest.mark.asyncio
    async def test_guard_blocks_when_login_pending(self, browser_tab):
        """Guard should return blocking dict when login is pending."""
        instance_id = "guard-test-pending"
        await manual_login_handler.register_pending_login(
            instance_id, browser_tab, "https://httpbin.org/forms/post"
        )

        result = await _check_pending_login_guard(instance_id)
        assert result is not None, "Guard should block when login is pending"
        assert result["blocked"] is True
        assert result["reason"] == "INSTANCE_PENDING_MANUAL_LOGIN"
        assert result["instance_id"] == instance_id

        # Cleanup
        await manual_login_handler._clear_pending(instance_id)
        await login_watcher.stop_watching(instance_id)

    @pytest.mark.asyncio
    async def test_guard_unblocks_after_confirm(self, browser_tab):
        """Guard should pass after confirm_login clears pending state."""
        instance_id = "guard-test-confirm"
        await manual_login_handler.register_pending_login(
            instance_id, browser_tab, "https://httpbin.org/forms/post"
        )

        # Blocked before confirm
        blocked = await _check_pending_login_guard(instance_id)
        assert blocked is not None

        # Confirm login (skip check since we're not on a real login page)
        result = await manual_login_handler.confirm_login(
            instance_id, browser_tab, skip_login_check=True
        )
        assert result["success"] is True

        # Should be unblocked now
        unblocked = await _check_pending_login_guard(instance_id)
        assert unblocked is None, "Guard should pass after login confirmed"

        await login_watcher.stop_watching(instance_id)

    @pytest.mark.asyncio
    async def test_guard_blocks_multiple_instances_independently(self, browser_tab):
        """Guard should track pending state per instance independently."""
        id_pending = "guard-multi-pending"
        id_free = "guard-multi-free"

        await manual_login_handler.register_pending_login(
            id_pending, browser_tab, "https://httpbin.org/forms/post"
        )

        # Pending instance is blocked
        assert await _check_pending_login_guard(id_pending) is not None
        # Free instance is not blocked
        assert await _check_pending_login_guard(id_free) is None

        # Cleanup
        await manual_login_handler._clear_pending(id_pending)
        await login_watcher.stop_watching(id_pending)


class TestWatcherDetectionConsumption:
    """Test that watcher detection flag is consumed atomically."""

    @pytest.mark.asyncio
    async def test_consume_detected_is_atomic(self):
        """consume_detected should return True once then False."""
        instance_id = "consume-test-atomic"

        # Manually set detected
        async with login_watcher._lock:
            login_watcher._detected.add(instance_id)

        # First consume: True
        result1 = await login_watcher.consume_detected(instance_id)
        assert result1 is True

        # Second consume: False (already consumed)
        result2 = await login_watcher.consume_detected(instance_id)
        assert result2 is False

    @pytest.mark.asyncio
    async def test_watcher_detected_skips_login_check(self, browser_tab):
        """
        When watcher detected login, confirm_login should skip the page check.
        This is the fast path: watcher saw URL change → skip DOM check.
        """
        instance_id = "watcher-skip-check"

        await manual_login_handler.register_pending_login(
            instance_id, browser_tab, "https://httpbin.org/forms/post"
        )

        # Simulate watcher detecting login
        async with login_watcher._lock:
            login_watcher._detected.add(instance_id)

        # Consume detected (as server.py does in confirm_manual_login)
        watcher_detected = await login_watcher.consume_detected(instance_id)
        assert watcher_detected is True

        # confirm_login with skip_login_check=True (watcher confirmed)
        result = await manual_login_handler.confirm_login(
            instance_id, browser_tab, skip_login_check=True
        )
        assert result["success"] is True

        await login_watcher.stop_watching(instance_id)

    @pytest.mark.asyncio
    async def test_concurrent_consume_detected_safe(self):
        """Multiple concurrent consume_detected calls should not double-consume."""
        instance_id = "consume-concurrent"

        async with login_watcher._lock:
            login_watcher._detected.add(instance_id)

        # Fire 10 concurrent consume calls
        tasks = [login_watcher.consume_detected(instance_id) for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # Exactly one should return True
        true_count = sum(1 for r in results if r is True)
        assert true_count == 1, f"Exactly one consume should return True, got {true_count}"


class TestPendingLoginStateIntegrity:
    """Test that pending login state is consistent under various conditions."""

    @pytest.mark.asyncio
    async def test_register_twice_is_idempotent(self, browser_tab):
        """Registering the same instance twice should not corrupt state."""
        instance_id = "register-twice"

        await manual_login_handler.register_pending_login(
            instance_id, browser_tab, "https://httpbin.org/forms/post"
        )
        await manual_login_handler.register_pending_login(
            instance_id, browser_tab, "https://httpbin.org/forms/post"
        )

        # Should still be pending (not doubled or corrupted)
        assert await manual_login_handler.is_pending_login(instance_id) is True

        info = await manual_login_handler.get_pending_info(instance_id)
        assert info is not None
        assert info["instance_id"] == instance_id

        # Cleanup
        await manual_login_handler._clear_pending(instance_id)
        await login_watcher.stop_watching(instance_id)

    @pytest.mark.asyncio
    async def test_confirm_without_register_returns_success(self, browser_tab):
        """
        confirm_login on a non-pending instance should still succeed.
        (Instance was never in pending state — just confirm current URL.)
        """
        instance_id = "confirm-no-register"

        result = await manual_login_handler.confirm_login(
            instance_id, browser_tab, skip_login_check=True
        )
        # Should succeed — just returns current URL
        assert result["success"] is True
        assert "current_url" in result

    @pytest.mark.asyncio
    async def test_pending_info_has_required_fields(self, browser_tab):
        """Pending info dict must have all fields the server expects."""
        instance_id = "pending-fields-check"
        url = "https://httpbin.org/forms/post"

        await manual_login_handler.register_pending_login(instance_id, browser_tab, url)

        info = await manual_login_handler.get_pending_info(instance_id)
        assert info is not None

        # Fields the server uses
        assert "instance_id" in info
        assert "url" in info
        assert "registered_at" in info
        assert "status" in info
        assert info["status"] == "waiting_for_user"
        assert info["url"] == url

        # Cleanup
        await manual_login_handler._clear_pending(instance_id)
        await login_watcher.stop_watching(instance_id)
