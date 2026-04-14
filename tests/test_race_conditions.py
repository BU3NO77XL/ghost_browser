"""Tests for race conditions and thread safety."""

import pytest
import asyncio
from manual_login_handler import manual_login_handler
from login_watcher import login_watcher


class TestConcurrentAccess:
    """Test concurrent access to shared resources."""
    
    @pytest.mark.asyncio
    async def test_concurrent_pending_login_checks(self):
        """Test concurrent checks for pending login."""
        tasks = []
        for i in range(50):
            task = manual_login_handler.is_pending_login(f"test_instance_{i}")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete without exceptions
        assert all(isinstance(r, bool) for r in results)
        assert len(results) == 50
    
    @pytest.mark.asyncio
    async def test_concurrent_watcher_checks(self):
        """Test concurrent watcher checks."""
        tasks = []
        for i in range(50):
            task = login_watcher.is_login_detected(f"test_instance_{i}")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete without exceptions
        assert all(isinstance(r, bool) for r in results)
        assert len(results) == 50
    
    @pytest.mark.asyncio
    async def test_concurrent_pending_info_access(self):
        """Test concurrent access to pending info."""
        tasks = []
        for i in range(30):
            task = manual_login_handler.get_pending_info(f"test_instance_{i}")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete without exceptions
        assert all(r is None or isinstance(r, dict) for r in results)
        assert len(results) == 30
    
    @pytest.mark.asyncio
    async def test_concurrent_register_and_check(self, browser_tab):
        """Test concurrent register and check operations."""
        instance_ids = [f"test_concurrent_{i}" for i in range(10)]
        
        # Register all concurrently
        register_tasks = [
            manual_login_handler.register_pending_login(
                instance_id,
                browser_tab,
                f"https://test.com/{instance_id}"
            )
            for instance_id in instance_ids
        ]
        await asyncio.gather(*register_tasks)
        
        # Check all concurrently
        check_tasks = [
            manual_login_handler.is_pending_login(instance_id)
            for instance_id in instance_ids
        ]
        results = await asyncio.gather(*check_tasks)
        
        # All should be pending
        assert all(r is True for r in results)
        
        # Cleanup
        for instance_id in instance_ids:
            await manual_login_handler._clear_pending(instance_id)
            await login_watcher.stop_watching(instance_id)
    
    @pytest.mark.asyncio
    async def test_concurrent_clear_operations(self, browser_tab):
        """Test concurrent clear operations."""
        instance_ids = [f"test_clear_{i}" for i in range(10)]
        
        # Register all
        for instance_id in instance_ids:
            await manual_login_handler.register_pending_login(
                instance_id,
                browser_tab,
                f"https://test.com/{instance_id}"
            )
        
        # Clear all concurrently
        clear_tasks = [
            manual_login_handler._clear_pending(instance_id)
            for instance_id in instance_ids
        ]
        await asyncio.gather(*clear_tasks)
        
        # Verify all cleared
        check_tasks = [
            manual_login_handler.is_pending_login(instance_id)
            for instance_id in instance_ids
        ]
        results = await asyncio.gather(*check_tasks)
        
        assert all(r is False for r in results)
        
        # Cleanup watchers
        for instance_id in instance_ids:
            await login_watcher.stop_watching(instance_id)


class TestLockProtection:
    """Test that locks properly protect shared state."""
    
    @pytest.mark.asyncio
    async def test_no_race_in_pending_state(self, browser_tab):
        """Test no race condition in pending state updates."""
        instance_id = "test_race_pending"
        
        # Rapidly register and clear
        async def register_clear_cycle():
            await manual_login_handler.register_pending_login(
                instance_id, browser_tab, "https://test.com"
            )
            await asyncio.sleep(0.001)
            await manual_login_handler._clear_pending(instance_id)
        
        tasks = [register_clear_cycle() for _ in range(10)]
        await asyncio.gather(*tasks)
        
        # Final state should be consistent
        is_pending = await manual_login_handler.is_pending_login(instance_id)
        assert isinstance(is_pending, bool)
        
        # Cleanup
        await login_watcher.stop_watching(instance_id)
    
    @pytest.mark.asyncio
    async def test_no_race_in_watcher_state(self):
        """Test no race condition in watcher state."""
        instance_id = "test_race_watcher"
        
        # Rapidly add and remove from detected set
        async def add_remove_cycle():
            async with login_watcher._lock:
                login_watcher._detected.add(instance_id)
            await asyncio.sleep(0.001)
            async with login_watcher._lock:
                login_watcher._detected.discard(instance_id)
        
        tasks = [add_remove_cycle() for _ in range(10)]
        await asyncio.gather(*tasks)
        
        # Final state should be consistent
        is_detected = await login_watcher.is_login_detected(instance_id)
        assert isinstance(is_detected, bool)
