"""
Tests for browser_management.py tools layer.

Verifies:
- spawn_browser orchestrates browser_manager + persistent_storage
- navigate orchestrates browser_manager + cookie_manager + login_handler
- JavaScript execution via execute_script
- Health checks and instance lifecycle
"""

import asyncio

import pytest

from core.models import BrowserOptions, BrowserState


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
            headless=False, viewport_width=1920, viewport_height=1080, user_agent="TestAgent/1.0"
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
        assert health["healthy"] is True
        assert "reason" in health
        assert health["can_recover"] is True

    @pytest.mark.asyncio
    async def test_health_check_nonexistent(self, browser_manager):
        """Test health check on non-existent instance."""
        health = await browser_manager.check_instance_health("nonexistent-id")

        assert health is not None
        assert health["healthy"] is False
        assert "Tab not found" in health["reason"]



# ─────────────────────────────────────────────────────────────────────────────
# JavaScript Execution (from test_javascript.py)
# ─────────────────────────────────────────────────────────────────────────────


class TestJavaScriptExecution:
    """Test JavaScript execution capabilities."""

    @pytest.mark.asyncio
    async def test_simple_expression(self, browser_tab):
        """Test evaluating simple expression."""
        result = await browser_tab.evaluate("2 + 2")
        assert result == 4

    @pytest.mark.asyncio
    async def test_string_expression(self, browser_tab):
        """Test evaluating string expression."""
        result = await browser_tab.evaluate("'Hello' + ' ' + 'World'")
        assert result == "Hello World"

    @pytest.mark.asyncio
    async def test_dom_access(self, navigated_tab):
        """Test accessing DOM."""
        title = await navigated_tab.evaluate("document.title")
        assert title is not None

        url = await navigated_tab.evaluate("window.location.href")
        assert "httpbin.org" in url

    @pytest.mark.asyncio
    async def test_set_and_get_variable(self, browser_tab):
        """Test setting and getting JavaScript variable."""
        await browser_tab.evaluate("window.testVar = 'test_value'")
        result = await browser_tab.evaluate("window.testVar")
        assert result == "test_value"


class TestDOMManipulation:
    """Test DOM manipulation."""

    @pytest.mark.asyncio
    async def test_query_selector(self, navigated_tab):
        """Test querySelector."""
        has_body = await navigated_tab.evaluate("!!document.querySelector('body')")
        assert has_body is True

    @pytest.mark.asyncio
    async def test_create_element(self, navigated_tab):
        """Test creating DOM element."""
        result = await navigated_tab.evaluate("""
            (function() {
                const div = document.createElement('div');
                div.id = 'test-div';
                div.textContent = 'Test Content';
                document.body.appendChild(div);
                return document.getElementById('test-div').textContent;
            })()
        """)
        assert result == "Test Content"

    @pytest.mark.asyncio
    async def test_get_element_properties(self, navigated_tab):
        """Test getting element properties."""
        tag_name = await navigated_tab.evaluate("document.body.tagName")
        child_count = await navigated_tab.evaluate("document.body.children.length")

        assert tag_name == "BODY"
        assert isinstance(child_count, int)
