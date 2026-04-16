"""Element interaction tools: click, type, scroll, screenshot, etc."""

import base64
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from core.debug_logger import debug_logger
from core.login_guard import check_pending_login_guard
from core.temp_file_manager import temp_file_manager


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]
    dom_handler = deps["dom_handler"]
    response_handler = deps["response_handler"]

    @section_tool("element-interaction")
    async def query_elements(
        instance_id: str,
        selector: str,
        text_filter: Optional[str] = None,
        visible_only: bool = True,
        limit: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query DOM elements.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector or XPath (starts with '//').
            text_filter (Optional[str]): Filter by text content.
            visible_only (bool): Only return visible elements.
            limit (Optional[Any]): Maximum number of elements to return.

        Returns:
            List[Dict[str, Any]]: List of matching elements with their properties.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        debug_logger.log_info(
            "Server", "query_elements", f"Received limit parameter: {limit} (type: {type(limit)})"
        )
        elements = await dom_handler.query_elements(tab, selector, text_filter, visible_only, limit)
        debug_logger.log_info(
            "Server", "query_elements", f"DOM handler returned {len(elements)} elements"
        )
        result = []
        for i, elem in enumerate(elements):
            try:
                if hasattr(elem, "model_dump"):
                    elem_dict = elem.model_dump()
                elif hasattr(elem, "dict"):
                    elem_dict = elem.dict()
                else:
                    elem_dict = elem
                result.append(elem_dict)
            except Exception as e:
                debug_logger.log_error("Server", "query_elements", e, {"element_index": i})
        return result if result else []

    @section_tool("element-interaction")
    async def click_element(
        instance_id: str,
        selector: str,
        text_match: Optional[str] = None,
        timeout: int = 10000,
    ) -> bool:
        """
        Click an element.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector or XPath.
            text_match (Optional[str]): Click element with matching text.
            timeout (int): Timeout in milliseconds.

        Returns:
            bool: True if clicked successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        if isinstance(timeout, str):
            timeout = int(timeout)
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await dom_handler.click_element(tab, selector, text_match, timeout)

    @section_tool("element-interaction")
    async def type_text(
        instance_id: str,
        selector: str,
        text: str,
        clear_first: bool = True,
        delay_ms: int = 50,
        parse_newlines: bool = False,
        shift_enter: bool = False,
    ) -> bool:
        """
        Type text into an input field.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector or XPath.
            text (str): Text to type.
            clear_first (bool): Clear field before typing.
            delay_ms (int): Delay between keystrokes in milliseconds.
            parse_newlines (bool): If True, parse \\n as Enter key presses.
            shift_enter (bool): If True, use Shift+Enter instead of Enter.

        Returns:
            bool: True if typed successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        if isinstance(delay_ms, str):
            delay_ms = int(delay_ms)
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await dom_handler.type_text(
            tab, selector, text, clear_first, delay_ms, parse_newlines, shift_enter
        )

    @section_tool("element-interaction")
    async def paste_text(
        instance_id: str, selector: str, text: str, clear_first: bool = True
    ) -> bool:
        """
        Paste text instantly into an input field.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector or XPath.
            text (str): Text to paste.
            clear_first (bool): Clear field before pasting.

        Returns:
            bool: True if pasted successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await dom_handler.paste_text(tab, selector, text, clear_first)

    @section_tool("element-interaction")
    async def select_option(
        instance_id: str,
        selector: str,
        value: Optional[str] = None,
        text: Optional[str] = None,
        index: Optional[Any] = None,
    ) -> bool:
        """
        Select an option from a dropdown.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector for the select element.
            value (Optional[str]): Option value attribute.
            text (Optional[str]): Option text content.
            index (Optional[Any]): Option index (0-based).

        Returns:
            bool: True if selected successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")

        converted_index = None
        if index is not None:
            try:
                converted_index = int(index)
            except (ValueError, TypeError):
                raise Exception(f"Invalid index value: {index}. Must be a number.")

        return await dom_handler.select_option(tab, selector, value, text, converted_index)

    @section_tool("element-interaction")
    async def get_element_state(instance_id: str, selector: str) -> Dict[str, Any]:
        """
        Get complete state of an element.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector or XPath.

        Returns:
            Dict[str, Any]: Element state including attributes, style, position, etc.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await dom_handler.get_element_state(tab, selector)

    @section_tool("element-interaction")
    async def wait_for_element(
        instance_id: str,
        selector: str,
        timeout: int = 30000,
        visible: bool = True,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Wait for an element to appear.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector or XPath.
            timeout (int): Timeout in milliseconds.
            visible (bool): Wait for element to be visible.
            text_content (Optional[str]): Wait for specific text content.

        Returns:
            bool: True if element found.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        if isinstance(timeout, str):
            timeout = int(timeout)
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await dom_handler.wait_for_element(tab, selector, timeout, visible, text_content)

    @section_tool("element-interaction")
    async def scroll_page(
        instance_id: str,
        direction: str = "down",
        amount: int = 500,
        smooth: bool = True,
    ) -> bool:
        """
        Scroll the page.

        Args:
            instance_id (str): Browser instance ID.
            direction (str): 'down', 'up', 'left', 'right', 'top', or 'bottom'.
            amount (int): Pixels to scroll.
            smooth (bool): Use smooth scrolling.

        Returns:
            bool: True if scrolled successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        if isinstance(amount, str):
            amount = int(amount)
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await dom_handler.scroll_page(tab, direction, amount, smooth)

    @section_tool("element-interaction")
    async def execute_script(
        instance_id: str, script: str, args: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute JavaScript in page context.

        Args:
            instance_id (str): Browser instance ID.
            script (str): JavaScript code to execute.
            args (Optional[List[Any]]): Arguments to pass to the script.

        Returns:
            Dict[str, Any]: Script execution result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        try:
            result = await dom_handler.execute_script(tab, script, args)
            return {"success": True, "result": result, "error": None}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    @section_tool("element-interaction")
    async def get_page_content(instance_id: str, include_frames: bool = False) -> Dict[str, Any]:
        """
        Get page HTML and text content.

        Args:
            instance_id (str): Browser instance ID.
            include_frames (bool): Include iframe information.

        Returns:
            Dict[str, Any]: Page content including HTML, text, and metadata.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        content = await dom_handler.get_page_content(tab, include_frames)
        return response_handler.handle_response(
            content,
            "page_content",
            {"instance_id": instance_id, "include_frames": include_frames},
        )

    @section_tool("element-interaction")
    async def save_page_html(
        instance_id: str,
        output_path: str,
        selector: Optional[str] = None,
        include_doctype: bool = True,
    ) -> Dict[str, Any]:
        """
        Serialize the current page DOM and save it directly to disk.

        The HTML content is written by the server process — it never travels
        through the MCP protocol — so there is no payload size limit.  This is
        the recommended way to capture large pages (>50 KB) for pixel-perfect
        cloning.

        Args:
            instance_id (str): Browser instance ID.
            output_path (str): Absolute or workspace-relative path where the
                HTML file should be written, e.g.
                "C:/Users/user/Desktop/project/index.html".
                Parent directories are created automatically.
            selector (Optional[str]): CSS selector of the element whose
                outerHTML should be saved.  Defaults to the full page
                (document.documentElement.outerHTML).
            include_doctype (bool): Prepend <!DOCTYPE html> when saving the
                full page (ignored when selector is provided).

        Returns:
            Dict[str, Any]: {
                "file_path": absolute path written,
                "file_size_kb": size in KB,
                "url": page URL at time of capture,
                "selector": selector used (null = full page),
            }
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")

        # Serialize DOM inside the browser — no size limit
        if selector:
            js = f"""
            (function() {{
                var el = document.querySelector({json.dumps(selector)});
                if (!el) return null;
                return el.outerHTML;
            }})()
            """
        else:
            js = "document.documentElement.outerHTML"

        html = await tab.evaluate(js)
        if html is None:
            raise Exception(
                f"Element not found for selector: {selector}"
                if selector
                else "Failed to serialize page HTML"
            )

        # Prepend doctype for full-page saves
        if not selector and include_doctype and not html.lstrip().lower().startswith("<!doctype"):
            html = "<!DOCTYPE html>\n" + html

        dest = Path(output_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")

        page_url = await tab.evaluate("window.location.href")

        return {
            "file_path": str(dest.absolute()),
            "file_size_kb": round(dest.stat().st_size / 1024, 2),
            "url": page_url,
            "selector": selector,
        }

    @section_tool("element-interaction")
    async def take_screenshot(
        instance_id: str,
        full_page: bool = False,
        format: str = "png",
        file_path: Optional[str] = None,
    ) -> Union[str, Dict[str, Any]]:
        """
        Take a screenshot of the page.

        Args:
            instance_id (str): Browser instance ID.
            full_page (bool): Capture full page (not just viewport).
            format (str): Image format ('png' or 'jpeg').
            file_path (Optional[str]): Optional file path to save screenshot to.

        Returns:
            Union[str, Dict]: File path if file_path provided, otherwise base64 data or file info.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        import io

        from PIL import Image

        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")

        if file_path:
            save_path = Path(file_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            await tab.save_screenshot(save_path)
            return f"Screenshot saved. AI agents should use the Read tool to view this image: {str(save_path.absolute())}"

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            await tab.save_screenshot(tmp_path)

            with Image.open(tmp_path) as img:
                if img.mode in ("RGBA", "LA", "P") and format.lower() == "jpeg":
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(
                        img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None
                    )
                    img = background

                output_buffer = io.BytesIO()
                if format.lower() == "jpeg":
                    img.save(output_buffer, format="JPEG", quality=85, optimize=True)
                else:
                    img.save(output_buffer, format="PNG", optimize=True)

                compressed_bytes = output_buffer.getvalue()
                base64_size = len(compressed_bytes) * 1.33
                estimated_tokens = int(base64_size / 4)

                if estimated_tokens > 20000:
                    file_size_kb = len(compressed_bytes) / 1024
                    return {
                        "error": "screenshot_too_large",
                        "estimated_tokens": estimated_tokens,
                        "file_size_kb": round(file_size_kb, 2),
                        "message": (
                            "Screenshot is too large to return inline. "
                            "Call take_screenshot again with an explicit file_path pointing to "
                            "your workspace, e.g. file_path='C:/Users/.../project/screenshot.png'."
                        ),
                    }

                return base64.b64encode(compressed_bytes).decode("utf-8")

        finally:
            if tmp_path.exists():
                os.unlink(tmp_path)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
