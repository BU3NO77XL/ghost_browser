"""
Tests for instance recovery and the "reuse vs recreate" decision.

Key questions tested:
- Can you reuse an existing active instance across multiple operations?
- What happens when you try to use a stored-but-dead instance?
- Does the system correctly tell you an instance is dead vs alive?
- Is there any actual recovery mechanism (reconnect) or must you always recreate?
"""

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from browser_manager import BrowserManager
from persistent_storage import persistent_storage
from models import BrowserOptions, BrowserState


class TestInstanceReuse:
    """Test reusing an existing active instance across multiple operations."""

    @pytest.mark.asyncio
    async def test_instance_survives_multiple_navigations(self, browser_manager):
        """Same instance should work across multiple navigate calls."""
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)
        tab = await browser_manager.get_tab(instance.instance_id)

        # Navigate multiple times on same instance
        await tab.get("https://httpbin.org/html")
        await asyncio.sleep(1)
        url1 = await tab.evaluate("window.location.href")
        assert "httpbin.org" in url1

        await tab.get("https://httpbin.org/json")
        await asyncio.sleep(1)
        url2 = await tab.evaluate("window.location.href")
        assert "json" in url2

        await tab.get("https://httpbin.org/html")
        await asyncio.sleep(1)
        url3 = await tab.evaluate("window.location.href")
        assert "html" in url3

        # Instance should still be healthy
        health = await browser_manager.check_instance_health(instance.instance_id)
        assert health["healthy"] is True

        await browser_manager.close_instance(instance.instance_id)

    @pytest.mark.asyncio
    async def test_instance_id_stable_across_operations(self, browser_manager):
        """Instance ID must not change during normal operations."""
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)
        original_id = instance.instance_id

        tab = await browser_manager.get_tab(original_id)
        await tab.get("https://httpbin.org/html")
        await asyncio.sleep(1)

        # Get instance again — should be same object
        instances = await browser_manager.list_instances()
        found = next((i for i in instances if i.instance_id == original_id), None)
        assert found is not None, "Instance should still exist with same ID"
        assert found.instance_id == original_id

        await browser_manager.close_instance(original_id)

    @pytest.mark.asyncio
    async def test_get_tab_returns_same_tab_object(self, browser_manager):
        """get_tab called twice should return the same tab for same instance."""
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)

        tab1 = await browser_manager.get_tab(instance.instance_id)
        tab2 = await browser_manager.get_tab(instance.instance_id)

        # Should be the same object (not a new tab each time)
        assert tab1 is tab2, "get_tab should return the same tab object"

        await browser_manager.close_instance(instance.instance_id)

    @pytest.mark.asyncio
    async def test_state_updates_persist_in_memory(self, browser_manager):
        """update_instance_state should be reflected in list_instances."""
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)
        tab = await browser_manager.get_tab(instance.instance_id)

        await tab.get("https://httpbin.org/html")
        await asyncio.sleep(1)
        url = await tab.evaluate("window.location.href")
        title = await tab.evaluate("document.title")

        await browser_manager.update_instance_state(instance.instance_id, url, title)

        instances = await browser_manager.list_instances()
        found = next((i for i in instances if i.instance_id == instance.instance_id), None)
        assert found is not None
        assert found.current_url == url

        await browser_manager.close_instance(instance.instance_id)


class TestDeadInstanceBehavior:
    """Test what happens when you try to use a dead/stale instance."""

    @pytest.mark.asyncio
    async def test_dead_instance_get_tab_returns_none(self, browser_manager):
        """After closing, get_tab should return None."""
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)
        instance_id = instance.instance_id

        await browser_manager.close_instance(instance_id)

        tab = await browser_manager.get_tab(instance_id)
        assert tab is None, "Closed instance should have no tab"

    @pytest.mark.asyncio
    async def test_dead_instance_not_in_list(self, browser_manager):
        """After closing, instance should not appear in list_instances."""
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)
        instance_id = instance.instance_id

        await browser_manager.close_instance(instance_id)

        instances = await browser_manager.list_instances()
        active_ids = {i.instance_id for i in instances}
        assert instance_id not in active_ids, "Closed instance should not be in active list"

    @pytest.mark.asyncio
    async def test_stored_only_instance_cannot_be_used(self, browser_manager):
        """
        CRITICAL: A stored-but-dead instance cannot be recovered.
        
        This documents the fundamental limitation: there is NO reconnect mechanism.
        If an instance is in storage but not in memory, it's dead and must be recreated.
        """
        # Inject a fake "stored" instance
        fake_id = "fake-stored-instance-xyz"
        persistent_storage.store_instance(fake_id, {
            "state": "ready",
            "created_at": "2026-01-01T00:00:00",
            "current_url": "https://instagram.com",
            "title": "Instagram"
        })

        # Verify it's in storage but not in memory
        tab = await browser_manager.get_tab(fake_id)
        assert tab is None, "Stored-only instance has no live tab"

        health = await browser_manager.check_instance_health(fake_id)
        assert health["healthy"] is False, "Stored-only instance is not healthy"
        assert health["can_recover"] is False, "Stored-only instance cannot be recovered"

        # The ONLY option is to spawn a new browser
        # This is the correct behavior — document it explicitly
        assert health["reason"] == "Tab not found"

        # Cleanup
        persistent_storage.remove_instance(fake_id)

    @pytest.mark.asyncio
    async def test_close_already_closed_instance_is_safe(self, browser_manager):
        """Closing an already-closed instance should not raise."""
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)

        await browser_manager.close_instance(instance.instance_id)

        # Second close should not raise
        try:
            result = await browser_manager.close_instance(instance.instance_id)
            # May return False (not found) — that's acceptable
            assert isinstance(result, bool)
        except Exception as e:
            pytest.fail(f"Second close raised unexpectedly: {e}")


class TestNoRecoveryMechanism:
    """
    Document and test the absence of a reconnect/recovery mechanism.
    
    This is important for the AI to understand: there is no way to
    "reconnect" to an existing browser session. The only recovery is
    spawn_browser() to create a new instance.
    """

    @pytest.mark.asyncio
    async def test_no_reconnect_api_exists(self, browser_manager):
        """
        Verify there is no reconnect method — this is by design.
        The correct flow is: detect dead → close → spawn new.
        """
        assert not hasattr(browser_manager, 'reconnect'), \
            "No reconnect method should exist — use spawn_browser instead"
        assert not hasattr(browser_manager, 'recover_instance'), \
            "No recover_instance method should exist"

    @pytest.mark.asyncio
    async def test_health_check_guides_recovery_decision(self, browser_manager):
        """
        Health check should provide enough info to decide: reuse or recreate.
        
        healthy=True + can_recover=True → reuse the instance
        healthy=False + can_recover=False → close and spawn new
        """
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)
        instance = await browser_manager.spawn_browser(options)

        # Healthy instance
        health = await browser_manager.check_instance_health(instance.instance_id)
        assert health["healthy"] is True
        assert health["can_recover"] is True
        # → Decision: reuse this instance

        await browser_manager.close_instance(instance.instance_id)

        # Dead instance
        health_dead = await browser_manager.check_instance_health(instance.instance_id)
        assert health_dead["healthy"] is False
        assert health_dead["can_recover"] is False
        # → Decision: spawn new browser

    @pytest.mark.asyncio
    async def test_spawn_new_after_dead_works(self, browser_manager):
        """
        The correct recovery flow: detect dead → spawn new → continue.
        """
        options = BrowserOptions(headless=False, viewport_width=1280, viewport_height=720)

        # Spawn and kill first instance
        inst1 = await browser_manager.spawn_browser(options)
        await browser_manager.close_instance(inst1.instance_id)

        # Spawn new instance (recovery)
        inst2 = await browser_manager.spawn_browser(options)
        assert inst2.instance_id != inst1.instance_id, "New instance should have different ID"

        tab = await browser_manager.get_tab(inst2.instance_id)
        assert tab is not None

        health = await browser_manager.check_instance_health(inst2.instance_id)
        assert health["healthy"] is True

        await browser_manager.close_instance(inst2.instance_id)
