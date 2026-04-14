"""Tests for JavaScript execution."""

import pytest
import asyncio


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
    async def test_complex_expression(self, navigated_tab):
        """Test complex JavaScript expression - nodriver may return list of pairs or dict."""
        # Return individual values to avoid serialization issues
        width = await navigated_tab.evaluate("window.innerWidth")
        height = await navigated_tab.evaluate("window.innerHeight")
        user_agent = await navigated_tab.evaluate("navigator.userAgent")
        
        assert isinstance(width, (int, float))
        assert isinstance(height, (int, float))
        assert isinstance(user_agent, str)
        assert len(user_agent) > 0
    
    @pytest.mark.asyncio
    async def test_set_and_get_variable(self, browser_tab):
        """Test setting and getting JavaScript variable."""
        await browser_tab.evaluate("window.testVar = 'test_value'")
        result = await browser_tab.evaluate("window.testVar")
        assert result == "test_value"
    
    @pytest.mark.asyncio
    async def test_async_operation(self, browser_tab):
        """Test async JavaScript operation - nodriver may not await Promise results."""
        # Use synchronous approach instead of async IIFE (nodriver limitation)
        await browser_tab.evaluate("window._asyncDone = false")
        await browser_tab.evaluate("""
            (async function() {
                await new Promise(resolve => setTimeout(resolve, 100));
                window._asyncDone = true;
            })()
        """)
        await asyncio.sleep(0.3)
        result = await browser_tab.evaluate("window._asyncDone")
        assert result is True


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
        """Test getting element properties - use separate evaluate calls to avoid dict serialization issues."""
        tag_name = await navigated_tab.evaluate("document.body.tagName")
        child_count = await navigated_tab.evaluate("document.body.children.length")
        
        assert tag_name == 'BODY'
        assert isinstance(child_count, int)
