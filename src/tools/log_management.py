"""Log management MCP tools for browser log entries and violation reporting via CDP."""

from typing import Dict, List

from core.log_handler import LogHandler
from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("log-management")
    async def log_enable(instance_id: str) -> bool:
        """
        Enable the Log domain for a browser instance.

        Must be called before log entries are reported to the client. Enables
        collection of browser log entries via CDP.

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
        return await LogHandler.enable_log(tab)

    @section_tool("log-management")
    async def log_disable(instance_id: str) -> bool:
        """
        Disable the Log domain for a browser instance.

        Prevents further log entries from being reported to the client.

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
        return await LogHandler.disable_log(tab)

    @section_tool("log-management")
    async def log_clear(instance_id: str) -> bool:
        """
        Clear the browser log for a browser instance.

        Removes all collected log entries from the browser's log buffer.

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
        return await LogHandler.clear_log(tab)

    @section_tool("log-management")
    async def log_start_violations_report(
        instance_id: str, settings: List[Dict]
    ) -> bool:
        """
        Start violation reporting for a browser instance.

        Begins reporting violations (e.g., long tasks, long layouts) based on
        the provided settings. Each setting specifies a violation type and a
        threshold in milliseconds.

        Example:
            log_start_violations_report("abc123", [
                {"name": "longTask", "threshold": 200.0},
                {"name": "longLayout", "threshold": 30.0}
            ])

        Args:
            instance_id (str): Browser instance ID.
            settings (List[Dict]): List of violation settings. Each dict must
                contain:
                - name (str): The violation type name (e.g., "longTask").
                - threshold (float): The threshold in milliseconds.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await LogHandler.start_violations_report(tab, settings)

    @section_tool("log-management")
    async def log_stop_violations_report(instance_id: str) -> bool:
        """
        Stop violation reporting for a browser instance.

        Stops the ongoing violation report started by log_start_violations_report.

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
        return await LogHandler.stop_violations_report(tab)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
