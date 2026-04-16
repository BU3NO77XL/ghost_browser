"""Pytest configuration and fixtures."""

import asyncio
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.browser_manager import BrowserManager
from core.debug_logger import debug_logger
from core.login_watcher import login_watcher
from core.manual_login_handler import manual_login_handler
from core.models import BrowserOptions
from core.network_interceptor import NetworkInterceptor

# Detect CI environment - browser tests need no_sandbox in containers
IS_CI = os.getenv("CI") == "true"


def skip_if_ci(reason="Requires real browser"):
    """Skip test if running in CI environment."""
    return pytest.mark.skipif(IS_CI, reason=reason)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def browser_manager():
    """Create a fresh BrowserManager for each test."""
    manager = BrowserManager()
    yield manager
    # Cleanup all instances after test
    try:
        instances = await manager.list_instances()
        for instance in instances:
            try:
                await manager.close_instance(instance.instance_id)
            except Exception:
                pass
    except Exception:
        pass


@pytest_asyncio.fixture(scope="function")
async def browser_instance(browser_manager):
    """Create a browser instance for testing."""
    if IS_CI:
        pytest.skip("Skipping browser spawn test in CI (no display)")
    # Use headless=True for faster tests
    options = BrowserOptions(headless=True, viewport_width=1280, viewport_height=720)
    instance = await browser_manager.spawn_browser(options)
    yield instance
    # Cleanup is handled by browser_manager fixture


@pytest_asyncio.fixture(scope="function")
async def browser_tab(browser_manager, browser_instance):
    """Get the main tab of a browser instance."""
    tab = await browser_manager.get_tab(browser_instance.instance_id)
    yield tab


@pytest.fixture(scope="function")
def network_interceptor():
    """Create a NetworkInterceptor for testing."""
    return NetworkInterceptor()


@pytest.fixture(autouse=True)
def enable_debug_logging():
    """Enable debug logging for all tests."""
    debug_logger.enable()
    yield


@pytest_asyncio.fixture(scope="function")
async def navigated_tab(browser_manager, browser_instance):
    """Get a tab that's already navigated to a test page."""
    tab = await browser_manager.get_tab(browser_instance.instance_id)
    await tab.get("https://httpbin.org/html")
    await asyncio.sleep(0.3)  # Reduced from 1s
    yield tab
