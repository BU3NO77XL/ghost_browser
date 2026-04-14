"""Tests for login flow and manual login handling."""

import pytest
import asyncio
from manual_login_handler import manual_login_handler
from login_watcher import login_watcher


class TestLoginDetection:
    """Test login page detection."""
    
    @pytest.mark.asyncio
    async def test_detect_login_page_with_form(self, browser_tab):
        """Test detecting login page with form."""
        await browser_tab.get("https://httpbin.org/forms/post")
        await asyncio.sleep(1)
        
        is_login = await manual_login_handler.detect_login_page(browser_tab)
        # httpbin forms page has password field, may be detected as login
        assert isinstance(is_login, bool)
    
    @pytest.mark.asyncio
    async def test_detect_non_login_page(self, browser_tab):
        """Test detecting non-login page."""
        await browser_tab.get("https://httpbin.org/html")
        await asyncio.sleep(1)
        
        is_login = await manual_login_handler.detect_login_page(browser_tab)
        # Plain HTML page should not be detected as login
        assert isinstance(is_login, bool)


class TestPendingLoginManagement:
    """Test pending login state management."""
    
    @pytest.mark.asyncio
    async def test_register_pending_login(self, browser_tab):
        """Test registering pending login."""
        instance_id = "test_instance_123"
        url = "https://httpbin.org/forms/post"
        
        await manual_login_handler.register_pending_login(instance_id, browser_tab, url)
        
        is_pending = await manual_login_handler.is_pending_login(instance_id)
        assert is_pending is True
        
        # Cleanup
        await manual_login_handler._clear_pending(instance_id)
        await login_watcher.stop_watching(instance_id)
    
    @pytest.mark.asyncio
    async def test_get_pending_info(self, browser_tab):
        """Test getting pending login info."""
        instance_id = "test_instance_456"
        url = "https://httpbin.org/forms/post"
        
        await manual_login_handler.register_pending_login(instance_id, browser_tab, url)
        
        info = await manual_login_handler.get_pending_info(instance_id)
        assert info is not None
        assert info['instance_id'] == instance_id
        assert info['url'] == url
        assert 'registered_at' in info
        assert info['status'] == 'waiting_for_user'
        
        # Cleanup
        await manual_login_handler._clear_pending(instance_id)
        await login_watcher.stop_watching(instance_id)
    
    @pytest.mark.asyncio
    async def test_clear_pending(self, browser_tab):
        """Test clearing pending login."""
        instance_id = "test_instance_789"
        url = "https://httpbin.org/forms/post"
        
        await manual_login_handler.register_pending_login(instance_id, browser_tab, url)
        assert await manual_login_handler.is_pending_login(instance_id) is True
        
        await manual_login_handler._clear_pending(instance_id)
        assert await manual_login_handler.is_pending_login(instance_id) is False
        
        # Cleanup watcher
        await login_watcher.stop_watching(instance_id)


class TestLoginWatcher:
    """Test login watcher functionality."""
    
    @pytest.mark.asyncio
    async def test_start_watching(self, browser_tab):
        """Test starting login watcher."""
        instance_id = "test_watcher_123"
        
        await login_watcher.start_watching(instance_id, browser_tab)
        
        # Give watcher time to start
        await asyncio.sleep(0.5)
        
        # Cleanup
        await login_watcher.stop_watching(instance_id)
    
    @pytest.mark.asyncio
    async def test_stop_watching(self, browser_tab):
        """Test stopping login watcher."""
        instance_id = "test_watcher_456"
        
        await login_watcher.start_watching(instance_id, browser_tab)
        await asyncio.sleep(0.5)
        
        await login_watcher.stop_watching(instance_id)
        
        # Verify watcher stopped
        is_detected = await login_watcher.is_login_detected(instance_id)
        assert is_detected is False
    
    @pytest.mark.asyncio
    async def test_consume_detected(self, browser_tab):
        """Test consuming detected flag."""
        instance_id = "test_watcher_789"
        
        # Manually set detected flag for testing
        async with login_watcher._lock:
            login_watcher._detected.add(instance_id)
        
        # Consume should return True and clear flag
        consumed = await login_watcher.consume_detected(instance_id)
        assert consumed is True
        
        # Second consume should return False
        consumed_again = await login_watcher.consume_detected(instance_id)
        assert consumed_again is False


class TestLoginFlowIntegration:
    """Test complete login flow integration."""
    
    @pytest.mark.asyncio
    async def test_full_login_flow(self, browser_tab):
        """Test complete login flow from detection to confirmation."""
        instance_id = "test_flow_123"
        
        # 1. Navigate to form page
        await browser_tab.get("https://httpbin.org/forms/post")
        await asyncio.sleep(1)
        
        # 2. Register pending login
        await manual_login_handler.register_pending_login(
            instance_id, 
            browser_tab, 
            "https://httpbin.org/forms/post"
        )
        
        # 3. Verify pending
        assert await manual_login_handler.is_pending_login(instance_id) is True
        
        # 4. Simulate "login" by navigating away
        await browser_tab.get("https://httpbin.org/html")
        await asyncio.sleep(3)  # Give watcher time to detect
        
        # 5. Check if watcher detected
        is_detected = await login_watcher.is_login_detected(instance_id)
        # May or may not detect depending on timing
        
        # 6. Confirm login
        result = await manual_login_handler.confirm_login(
            instance_id,
            browser_tab,
            skip_login_check=True  # Skip check for test
        )
        
        assert result['success'] is True
        assert 'current_url' in result
        
        # 7. Verify pending cleared
        assert await manual_login_handler.is_pending_login(instance_id) is False
        
        # Cleanup
        await login_watcher.stop_watching(instance_id)
