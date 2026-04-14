"""Tests for browser management functionality."""

import pytest
import asyncio
from models import BrowserOptions, BrowserState


class TestBrowserSpawn:
    """Test browser spawning and initialization."""
    
    @pytest.mark.asyncio
    async def test_spawn_browser_basic(self, browser_manager):
        """Test basic browser spawning."""
        options = BrowserOptions(headless=False)
        instance = await browser_manager.spawn_browser(options)
        
        assert instance is not None
        assert instance.instance_id is not None
        assert instance.state == BrowserState.READY
        
        # Cleanup
        await browser_manager.close_instance(instance.instance_id)
    
    @pytest.mark.asyncio
    async def test_spawn_browser_with_options(self, browser_manager):
        """Test browser spawning with custom options."""
        options = BrowserOptions(
            headless=False,
            viewport_width=1920,
            viewport_height=1080,
            user_agent="TestAgent/1.0"
        )
        instance = await browser_manager.spawn_browser(options)
        
        assert instance is not None
        assert instance.viewport["width"] == 1920
        assert instance.viewport["height"] == 1080
        
        await browser_manager.close_instance(instance.instance_id)
    
    @pytest.mark.asyncio
    async def test_spawn_multiple_browsers(self, browser_manager):
        """Test spawning multiple browser instances."""
        options = BrowserOptions(headless=False)
        
        instance1 = await browser_manager.spawn_browser(options)
        instance2 = await browser_manager.spawn_browser(options)
        
        assert instance1.instance_id != instance2.instance_id
        
        instances = await browser_manager.list_instances()
        assert len(instances) >= 2
        
        await browser_manager.close_instance(instance1.instance_id)
        await browser_manager.close_instance(instance2.instance_id)


class TestBrowserOperations:
    """Test browser operations."""
    
    @pytest.mark.asyncio
    async def test_get_tab(self, browser_manager, browser_instance):
        """Test getting browser tab."""
        tab = await browser_manager.get_tab(browser_instance.instance_id)
        assert tab is not None
    
    @pytest.mark.asyncio
    async def test_get_browser(self, browser_manager, browser_instance):
        """Test getting browser object."""
        browser = await browser_manager.get_browser(browser_instance.instance_id)
        assert browser is not None
    
    @pytest.mark.asyncio
    async def test_list_instances(self, browser_manager, browser_instance):
        """Test listing browser instances."""
        instances = await browser_manager.list_instances()
        assert len(instances) >= 1
        assert any(i.instance_id == browser_instance.instance_id for i in instances)
    
    @pytest.mark.asyncio
    async def test_close_instance(self, browser_manager):
        """Test closing browser instance."""
        options = BrowserOptions(headless=False)
        instance = await browser_manager.spawn_browser(options)
        
        success = await browser_manager.close_instance(instance.instance_id)
        assert success is True
        
        # Verify instance is gone
        tab = await browser_manager.get_tab(instance.instance_id)
        assert tab is None


class TestBrowserHealth:
    """Test browser health checking."""
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, browser_manager, browser_instance):
        """Test health check on healthy instance."""
        health = await browser_manager.check_instance_health(browser_instance.instance_id)
        
        assert health is not None
        assert health['healthy'] is True
        assert 'reason' in health
        assert health['can_recover'] is True
    
    @pytest.mark.asyncio
    async def test_health_check_nonexistent(self, browser_manager):
        """Test health check on non-existent instance."""
        health = await browser_manager.check_instance_health("nonexistent-id")
        
        assert health is not None
        assert health['healthy'] is False
        assert 'Tab not found' in health['reason']
