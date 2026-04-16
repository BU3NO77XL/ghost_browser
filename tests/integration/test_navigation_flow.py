"""Tests for navigation functionality."""

import asyncio

import pytest


class TestBasicNavigation:
    """Test basic navigation operations."""

    @pytest.mark.asyncio
    async def test_navigate_to_url(self, browser_tab):
        """Test navigating to a URL."""
        await browser_tab.get("https://httpbin.org/html")
        await asyncio.sleep(1)

        url = await browser_tab.evaluate("window.location.href")
        assert "httpbin.org" in url

    @pytest.mark.asyncio
    async def test_navigate_multiple_pages(self, browser_tab):
        """Test navigating to multiple pages."""
        # First page
        await browser_tab.get("https://httpbin.org/html")
        await asyncio.sleep(1)
        url1 = await browser_tab.evaluate("window.location.href")
        assert "html" in url1

        # Second page
        await browser_tab.get("https://httpbin.org/forms/post")
        await asyncio.sleep(1)
        url2 = await browser_tab.evaluate("window.location.href")
        assert "forms" in url2

    @pytest.mark.asyncio
    async def test_page_reload(self, navigated_tab):
        """Test page reload."""
        url_before = await navigated_tab.evaluate("window.location.href")

        await navigated_tab.reload()
        await asyncio.sleep(1)

        url_after = await navigated_tab.evaluate("window.location.href")
        assert url_before == url_after


class TestPageState:
    """Test page state retrieval."""

    @pytest.mark.asyncio
    async def test_get_page_state(self, browser_manager, browser_instance, navigated_tab):
        """Test getting complete page state."""
        state = await browser_manager.get_page_state(browser_instance.instance_id)

        assert state is not None
        assert state.url is not None
        assert "httpbin.org" in state.url
        assert state.ready_state in ["complete", "interactive", "loading"]
        assert isinstance(state.cookies, list)
        assert isinstance(state.local_storage, dict)
        assert isinstance(state.session_storage, dict)
        assert isinstance(state.viewport, dict)
        assert "width" in state.viewport
        assert "height" in state.viewport

    @pytest.mark.asyncio
    async def test_update_instance_state(self, browser_manager, browser_instance, navigated_tab):
        """Test updating instance state."""
        url = await navigated_tab.evaluate("window.location.href")
        title = await navigated_tab.evaluate("document.title")

        await browser_manager.update_instance_state(browser_instance.instance_id, url, title)

        # Verify state was updated
        instances = await browser_manager.list_instances()
        instance = next(i for i in instances if i.instance_id == browser_instance.instance_id)
        assert instance.current_url == url
