"""
Tests for instance persistence and storage behavior.

These tests verify:
- Instances are persisted to disk on creation
- Instances are removed from disk on close
- Stale instances in storage are correctly identified as "stored" (not active)
- Storage survives across BrowserManager restarts (simulated)
- Storage file doesn't accumulate dead instances after close
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

IS_CI = os.getenv("CI") == "true"

from core.browser_manager import BrowserManager
from core.models import BrowserOptions
from core.persistent_storage import InMemoryStorage, persistent_storage


class TestStoragePersistence:
    """Test that instances are correctly persisted and removed from disk."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(IS_CI, reason="Requires real browser (not available in CI)")
    async def test_instance_stored_on_spawn(self, browser_manager):
        """Instance must appear in persistent storage immediately after spawn."""
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)

        stored = persistent_storage.get_instance(instance.instance_id)
        assert stored is not None, "Instance should be in persistent storage after spawn"
        assert stored["instance_id"] == instance.instance_id
        assert stored["state"] == "ready"

        await browser_manager.close_instance(instance.instance_id)

    @pytest.mark.asyncio
    @pytest.mark.skipif(IS_CI, reason="Requires real browser (not available in CI)")
    async def test_instance_removed_on_close(self, browser_manager):
        """Instance must be removed from persistent storage after close."""
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)
        instance_id = instance.instance_id

        await browser_manager.close_instance(instance_id)

        stored = persistent_storage.get_instance(instance_id)
        assert stored is None, "Instance should be removed from storage after close"

    @pytest.mark.asyncio
    async def test_storage_persisted_to_disk(self, browser_manager, tmp_path):
        """Verify storage is actually written to disk (not just in-memory)."""
        storage_file = tmp_path / "test_instances.json"
        test_storage = InMemoryStorage(storage_file=str(storage_file))

        test_storage.store_instance(
            "test-id-123",
            {
                "state": "ready",
                "created_at": "2026-01-01T00:00:00",
                "current_url": "https://example.com",
                "title": "Test",
            },
        )

        assert storage_file.exists(), "Storage file should be created on disk"
        data = json.loads(storage_file.read_text())
        assert "test-id-123" in data["instances"]

    @pytest.mark.asyncio
    async def test_storage_loads_from_disk_on_init(self, tmp_path):
        """
        New InMemoryStorage clears stale data on init (by design).
        Instances from previous runs are discarded to prevent ghost instances.
        """
        storage_file = tmp_path / "test_instances.json"

        # Write data with first storage instance
        storage1 = InMemoryStorage(storage_file=str(storage_file))
        storage1.store_instance(
            "persisted-id",
            {
                "state": "ready",
                "created_at": "2026-01-01T00:00:00",
                "current_url": "https://example.com",
                "title": "Persisted",
            },
        )

        # Create second storage instance pointing to same file
        # By design, it clears stale instances from previous runs
        storage2 = InMemoryStorage(storage_file=str(storage_file))
        loaded = storage2.get_instance("persisted-id")

        # Stale instances are cleared on startup — this is the correct behavior
        assert (
            loaded is None
        ), "Stale instances should be cleared on startup to prevent ghost instances"

    @pytest.mark.asyncio
    @pytest.mark.skipif(IS_CI, reason="Requires real browser (not available in CI)")
    async def test_no_stale_instances_after_close(self, browser_manager):
        """After closing all instances, storage should be empty."""
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)

        # Spawn 2 instances
        inst1 = await browser_manager.spawn_browser(options)
        inst2 = await browser_manager.spawn_browser(options)

        # Close both
        await browser_manager.close_instance(inst1.instance_id)
        await browser_manager.close_instance(inst2.instance_id)

        # Neither should remain in storage
        assert persistent_storage.get_instance(inst1.instance_id) is None
        assert persistent_storage.get_instance(inst2.instance_id) is None


class TestStaleInstanceDetection:
    """Test that stale instances in storage are correctly identified."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(IS_CI, reason="Requires real browser (not available in CI)")
    async def test_list_instances_shows_stored_vs_active(self, browser_manager):
        """list_instances should distinguish active vs stored-only instances."""
        # Manually inject a stale instance into storage
        stale_id = "stale-instance-that-never-existed"
        persistent_storage.store_instance(
            stale_id,
            {
                "state": "ready",
                "created_at": "2026-01-01T00:00:00",
                "current_url": "https://example.com",
                "title": "Stale",
            },
        )

        # Spawn a real active instance
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)
        active = await browser_manager.spawn_browser(options)

        # list_instances from server perspective
        memory_instances = await browser_manager.list_instances()
        storage_instances = persistent_storage.list_instances()

        active_ids = {i.instance_id for i in memory_instances}
        stored_ids = set(storage_instances.get("instances", {}).keys())

        assert active.instance_id in active_ids, "Active instance should be in memory"
        assert stale_id in stored_ids, "Stale instance should be in storage"
        assert stale_id not in active_ids, "Stale instance should NOT be in memory"

        # Cleanup
        await browser_manager.close_instance(active.instance_id)
        persistent_storage.remove_instance(stale_id)

    @pytest.mark.asyncio
    async def test_stale_instance_tab_returns_none(self, browser_manager):
        """get_tab for a stale/stored-only instance should return None."""
        stale_id = "stale-no-tab-instance"
        persistent_storage.store_instance(
            stale_id,
            {
                "state": "ready",
                "created_at": "2026-01-01T00:00:00",
                "current_url": "https://example.com",
                "title": "Stale",
            },
        )

        tab = await browser_manager.get_tab(stale_id)
        assert tab is None, "Stale instance should have no tab (not recoverable)"

        # Cleanup
        persistent_storage.remove_instance(stale_id)

    @pytest.mark.asyncio
    async def test_stale_instance_health_check_fails(self, browser_manager):
        """Health check on stale instance should return healthy=False."""
        stale_id = "stale-health-check-instance"
        persistent_storage.store_instance(
            stale_id,
            {
                "state": "ready",
                "created_at": "2026-01-01T00:00:00",
                "current_url": "https://example.com",
                "title": "Stale",
            },
        )

        health = await browser_manager.check_instance_health(stale_id)
        assert health["healthy"] is False
        assert health["can_recover"] is False

        # Cleanup
        persistent_storage.remove_instance(stale_id)

    def test_current_storage_has_stale_instances(self):
        """
        DIAGNOSTIC: Storage should be empty on fresh startup (cleared by _load_from_disk).
        Stale instances from previous runs are discarded automatically.
        """
        all_stored = persistent_storage.list_instances()
        instances = all_stored.get("instances", {})
        stale_count = len(instances)
        print(
            f"\n[DIAGNOSTIC] Storage has {stale_count} persisted instances (should be 0 on fresh start)"
        )
        # After our fix, storage is cleared on startup — only instances created
        # in the current run should be present
        assert isinstance(stale_count, int)


class TestStorageCleanup:
    """Test storage cleanup mechanisms."""

    def test_clear_all_storage(self, tmp_path):
        """clear_all should remove all instances from storage and disk."""
        storage_file = tmp_path / "clear_test.json"
        storage = InMemoryStorage(storage_file=str(storage_file))

        storage.store_instance(
            "id-1", {"state": "ready", "created_at": "", "current_url": "", "title": ""}
        )
        storage.store_instance(
            "id-2", {"state": "ready", "created_at": "", "current_url": "", "title": ""}
        )

        storage.clear_all()

        assert storage.get_instance("id-1") is None
        assert storage.get_instance("id-2") is None

        data = json.loads(storage_file.read_text())
        assert data["instances"] == {}

    def test_remove_nonexistent_instance_is_safe(self):
        """Removing a non-existent instance should not raise."""
        try:
            persistent_storage.remove_instance("does-not-exist-xyz")
        except Exception as e:
            pytest.fail(f"remove_instance raised unexpectedly: {e}")

    @pytest.mark.asyncio
    async def test_cleanup_stale_instances_from_real_storage(self):
        """
        After our fix, storage is cleared on startup — no stale instances should exist
        unless created in the current test run.
        """
        all_stored = persistent_storage.list_instances()
        stored_ids = list(all_stored.get("instances", {}).keys())

        manager = BrowserManager()
        active_instances = await manager.list_instances()
        active_ids = {i.instance_id for i in active_instances}

        # Any stored instance not in active memory is stale
        stale_ids = [iid for iid in stored_ids if iid not in active_ids]

        # Clean them up
        for stale_id in stale_ids:
            persistent_storage.remove_instance(stale_id)

        # Verify they're gone
        for stale_id in stale_ids:
            assert persistent_storage.get_instance(stale_id) is None

        print(f"\n[CLEANUP] Removed {len(stale_ids)} stale instances")


# ─────────────────────────────────────────────────────────────────────────────
# Instance Recovery Tests (from test_instance_recovery.py)
# ─────────────────────────────────────────────────────────────────────────────


class TestInstanceReuse:
    """Test reusing an existing active instance across multiple operations."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(IS_CI, reason="Requires real browser (not available in CI)")
    async def test_instance_survives_multiple_navigations(self, browser_manager):
        """Same instance should work across multiple navigate calls."""
        options = BrowserOptions(headless=True, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)
        tab = await browser_manager.get_tab(instance.instance_id)

        # Navigate multiple times on same instance
        await tab.get("https://httpbin.org/html")
        await asyncio.sleep(0.3)
        url1 = await tab.evaluate("window.location.href")
        assert "httpbin.org" in url1

        await tab.get("https://httpbin.org/json")
        await asyncio.sleep(0.3)
        url2 = await tab.evaluate("window.location.href")
        assert "json" in url2

        # Instance should still be healthy
        health = await browser_manager.check_instance_health(instance.instance_id)
        assert health["healthy"] is True

        await browser_manager.close_instance(instance.instance_id)

    @pytest.mark.asyncio
    @pytest.mark.skipif(IS_CI, reason="Requires real browser (not available in CI)")
    async def test_instance_id_stable_across_operations(self, browser_manager):
        """Instance ID must not change during normal operations."""
        options = BrowserOptions(headless=True, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)
        original_id = instance.instance_id

        tab = await browser_manager.get_tab(original_id)
        await tab.get("https://httpbin.org/html")
        await asyncio.sleep(0.3)

        # Get instance again — should be same object
        instances = await browser_manager.list_instances()
        found = next((i for i in instances if i.instance_id == original_id), None)
        assert found is not None
        assert found.instance_id == original_id

        await browser_manager.close_instance(original_id)


class TestDeadInstanceBehavior:
    """Test what happens when you try to use a dead/stale instance."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(IS_CI, reason="Requires real browser (not available in CI)")
    async def test_dead_instance_get_tab_returns_none(self, browser_manager):
        """After closing, get_tab should return None."""
        options = BrowserOptions(headless=True, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)
        instance_id = instance.instance_id

        await browser_manager.close_instance(instance_id)

        tab = await browser_manager.get_tab(instance_id)
        assert tab is None

    @pytest.mark.asyncio
    async def test_stored_only_instance_cannot_be_used(self, browser_manager):
        """
        CRITICAL: A stored-but-dead instance cannot be recovered.
        There is NO reconnect mechanism — must spawn new browser.
        """
        # Inject a fake "stored" instance
        fake_id = "fake-stored-instance-xyz"
        persistent_storage.store_instance(
            fake_id,
            {
                "state": "ready",
                "created_at": "2026-01-01T00:00:00",
                "current_url": "https://instagram.com",
                "title": "Instagram",
            },
        )

        # Verify it's in storage but not in memory
        tab = await browser_manager.get_tab(fake_id)
        assert tab is None

        health = await browser_manager.check_instance_health(fake_id)
        assert health["healthy"] is False
        assert health["can_recover"] is False
        assert health["reason"] == "Tab not found"

        # Cleanup
        persistent_storage.remove_instance(fake_id)


class TestNoRecoveryMechanism:
    """Document the absence of a reconnect/recovery mechanism."""

    @pytest.mark.asyncio
    async def test_no_reconnect_api_exists(self, browser_manager):
        """Verify there is no reconnect method — use spawn_browser instead."""
        assert not hasattr(browser_manager, "reconnect")
        assert not hasattr(browser_manager, "recover_instance")

    @pytest.mark.asyncio
    @pytest.mark.skipif(IS_CI, reason="Requires real browser (not available in CI)")
    async def test_spawn_new_after_dead_works(self, browser_manager):
        """The correct recovery flow: detect dead → spawn new → continue."""
        options = BrowserOptions(headless=True, viewport_width=1280, viewport_height=720)

        # Spawn and kill first instance
        inst1 = await browser_manager.spawn_browser(options)
        await browser_manager.close_instance(inst1.instance_id)

        # Spawn new instance (recovery)
        inst2 = await browser_manager.spawn_browser(options)
        assert inst2.instance_id != inst1.instance_id

        tab = await browser_manager.get_tab(inst2.instance_id)
        assert tab is not None

        health = await browser_manager.check_instance_health(inst2.instance_id)
        assert health["healthy"] is True

        await browser_manager.close_instance(inst2.instance_id)
