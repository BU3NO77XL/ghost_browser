"""System info management MCP tools for querying browser/GPU/process information via CDP."""

import os
import platform
import sys
from pathlib import Path
from typing import Any, Dict, List

from core.login_guard import check_pending_login_guard
from core.system_info_handler import SystemInfoHandler


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("system-info-management")
    async def get_server_info() -> Dict[str, Any]:
        """
        Return information about the MCP server process itself.

        Use this to discover the server's working directory and OS so you can
        build correct absolute output_path values when calling file-extraction
        or save_page_html tools.

        Returns:
            Dict with:
                cwd         — current working directory of the server process
                platform    — operating system name (Windows / Linux / Darwin)
                python      — Python version string
                path_sep    — path separator for this OS (\\ on Windows, / elsewhere)
                home        — user home directory
        """
        return {
            "cwd": str(Path.cwd().absolute()),
            "platform": platform.system(),
            "python": sys.version.split()[0],
            "path_sep": os.sep,
            "home": str(Path.home()),
        }

    @section_tool("system-info-management")
    async def system_info_get_info(instance_id: str) -> Dict[str, Any]:
        """
        Return information about the system for a browser instance.

        Queries the CDP SystemInfo domain to retrieve GPU information, model
        name, and command line used to launch the browser.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Dict with keys ``gpu``, ``model_name``, and ``command_line``.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await SystemInfoHandler.get_info(tab)

    @section_tool("system-info-management")
    async def system_info_get_feature_state(instance_id: str, feature_flag: str) -> Dict[str, bool]:
        """
        Return the state of a browser feature flag for a browser instance.

        Queries the CDP SystemInfo domain to check whether a specific browser
        feature flag is enabled.

        Args:
            instance_id (str): Browser instance ID.
            feature_flag (str): The name of the feature flag to query.

        Returns:
            Dict with key ``feature_enabled`` (bool).
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await SystemInfoHandler.get_feature_state(tab, feature_flag)

    @section_tool("system-info-management")
    async def system_info_get_process_info(
        instance_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Return information about all running browser processes for a browser instance.

        Queries the CDP SystemInfo domain to retrieve a list of all running
        browser processes with their IDs, types, and CPU times.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            List of dicts each with ``id``, ``type``, and ``cpu_time`` keys.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await SystemInfoHandler.get_process_info(tab)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
