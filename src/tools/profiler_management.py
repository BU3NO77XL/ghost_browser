"""Profiler management MCP tools for CPU profiling and code coverage."""

from typing import Any, Dict, Optional

from core.login_guard import check_pending_login_guard
from core.profiler_handler import ProfilerHandler


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("profiler-management")
    async def start_cpu_profiling(instance_id: str) -> bool:
        """
        Start CPU profiling for a browser instance.

        Records JavaScript execution time to identify performance bottlenecks.
        Call stop_cpu_profiling() to end the session and get the profile data.

        Example:
            start_cpu_profiling("abc123")
            # ... perform actions to profile ...
            profile = stop_cpu_profiling("abc123")

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            bool: True if profiling started successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await ProfilerHandler.start_profiling(tab)

    @section_tool("profiler-management")
    async def stop_cpu_profiling(instance_id: str) -> Dict[str, Any]:
        """
        Stop CPU profiling and return the profile data.

        Profile data includes a call tree of JavaScript functions with hit counts.
        Large profiles are automatically truncated to prevent memory issues.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Dict[str, Any]: CPU profile with nodes, start_time, end_time, samples,
                            and truncated flag if data was truncated.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await ProfilerHandler.stop_profiling(tab)

    @section_tool("profiler-management")
    async def start_code_coverage(
        instance_id: str, call_count: bool = False, detailed: bool = False
    ) -> bool:
        """
        Start collecting JavaScript code coverage data.

        Tracks which lines/functions of JavaScript code are executed.
        Useful for identifying dead code and measuring test coverage.

        Args:
            instance_id (str): Browser instance ID.
            call_count (bool): Whether to collect call counts (more overhead).
            detailed (bool): Whether to collect block-level coverage (vs function-level).

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await ProfilerHandler.start_precise_coverage(tab, call_count, detailed)

    @section_tool("profiler-management")
    async def stop_code_coverage(instance_id: str) -> bool:
        """
        Stop collecting JavaScript code coverage data.

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
        return await ProfilerHandler.stop_precise_coverage(tab)

    @section_tool("profiler-management")
    async def take_code_coverage_snapshot(
        instance_id: str, url_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Take a snapshot of the current code coverage data.

        Returns coverage information for all loaded scripts, showing which
        functions and ranges have been executed.

        Example:
            take_code_coverage_snapshot("abc123", url_filter="app.js")
            # Returns coverage only for scripts matching "app.js"

        Args:
            instance_id (str): Browser instance ID.
            url_filter (Optional[str]): Optional URL substring to filter results.

        Returns:
            Dict[str, Any]: Coverage data with scripts, functions, and covered ranges.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await ProfilerHandler.take_precise_coverage(tab, url_filter)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
