"""Debugger management MCP tools for JavaScript debugging via CDP."""

from typing import Any, Dict, List, Optional

from core.debugger_handler import DebuggerHandler
from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("debugger-management")
    async def enable_debugger(instance_id: str) -> str:
        """
        Enable the JavaScript debugger for a browser instance.

        Must be called before using other debugger tools. Returns a debugger ID
        that identifies this debugging session.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            str: The debugger session ID.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DebuggerHandler.enable_debugger(tab)

    @section_tool("debugger-management")
    async def disable_debugger(instance_id: str) -> bool:
        """
        Disable the JavaScript debugger for a browser instance.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DebuggerHandler.disable_debugger(tab)

    @section_tool("debugger-management")
    async def set_breakpoint(
        instance_id: str,
        url: str,
        line_number: int,
        column_number: int = 0,
        condition: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Set a JavaScript breakpoint at a specific URL and line number.

        The debugger will pause execution when the breakpoint is hit, allowing
        inspection of variables and the call stack.

        Example:
            set_breakpoint("abc123", "https://example.com/app.js", 42)
            # Sets a breakpoint at line 42 of app.js

            set_breakpoint("abc123", "app.js", 100, condition="x > 5")
            # Conditional breakpoint: only pauses when x > 5

        Args:
            instance_id (str): Browser instance ID.
            url (str): The URL or URL pattern of the script.
            line_number (int): The line number (0-indexed).
            column_number (int): The column number (0-indexed, default 0).
            condition (Optional[str]): Optional JavaScript condition expression.

        Returns:
            Dict[str, Any]: Breakpoint info with breakpoint_id and resolved locations.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DebuggerHandler.set_breakpoint(
            tab, url, line_number, column_number, condition
        )

    @section_tool("debugger-management")
    async def remove_breakpoint(instance_id: str, breakpoint_id: str) -> bool:
        """
        Remove a JavaScript breakpoint by its ID.

        Args:
            instance_id (str): Browser instance ID.
            breakpoint_id (str): The breakpoint ID (from set_breakpoint).

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DebuggerHandler.remove_breakpoint(tab, breakpoint_id)

    @section_tool("debugger-management")
    async def resume_execution(instance_id: str) -> bool:
        """
        Resume JavaScript execution after a breakpoint pause.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DebuggerHandler.resume_execution(tab)

    @section_tool("debugger-management")
    async def step_over(instance_id: str) -> bool:
        """
        Step over the current statement (execute current line, stop at next).

        Use when paused at a breakpoint to advance one line without entering
        function calls.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DebuggerHandler.step_over(tab)

    @section_tool("debugger-management")
    async def step_into(instance_id: str) -> bool:
        """
        Step into the current function call.

        Use when paused at a breakpoint to enter the function being called
        on the current line.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DebuggerHandler.step_into(tab)

    @section_tool("debugger-management")
    async def get_call_stack(instance_id: str) -> List[Dict[str, Any]]:
        """
        Get the current JavaScript call stack.

        Returns the stack trace showing the sequence of function calls that
        led to the current execution point.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            List[Dict[str, Any]]: List of call frames with function name and location.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DebuggerHandler.get_call_stack(tab)

    @section_tool("debugger-management")
    async def evaluate_on_call_frame(
        instance_id: str, call_frame_id: str, expression: str
    ) -> Dict[str, Any]:
        """
        Evaluate a JavaScript expression on a specific call frame when paused.

        Allows inspecting variables and executing code in the context of a
        specific stack frame during a debugging session.

        Example:
            evaluate_on_call_frame("abc123", "frame-0", "myVariable")
            # Returns the value of myVariable in the current frame

        Args:
            instance_id (str): Browser instance ID.
            call_frame_id (str): The call frame ID (from CDP Debugger.paused event).
            expression (str): The JavaScript expression to evaluate.

        Returns:
            Dict[str, Any]: Evaluation result with type, value, and any exception info.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DebuggerHandler.evaluate_on_call_frame(
            tab, call_frame_id, expression
        )

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
