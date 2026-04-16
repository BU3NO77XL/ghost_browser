"""Storage CDP management MCP tools for origin data management, quota, and cache tracking via CDP."""

from core.login_guard import check_pending_login_guard
from core.storage_cdp_handler import StorageCDPHandler


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("storage-cdp-management")
    async def storage_clear_data_for_origin(
        instance_id: str, origin: str, storage_types: str = "all"
    ) -> bool:
        """
        Clear storage data for a given origin.

        Removes stored data (cookies, localStorage, etc.) for the specified origin.
        Use 'all' to clear all storage types, or provide a comma-separated list
        such as 'cookies,localStorage'.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin to clear data for (e.g., 'https://example.com').
            storage_types (str): Comma-separated list of storage types to clear
                (e.g., 'cookies,localStorage' or 'all'). Defaults to 'all'.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageCDPHandler.clear_data_for_origin(tab, origin, storage_types)

    @section_tool("storage-cdp-management")
    async def storage_get_usage_and_quota(instance_id: str, origin: str) -> dict:
        """
        Get storage usage and quota for a given origin.

        Returns the current storage usage in bytes and the storage quota for
        the specified origin, along with a convenience 'usage_mb' field.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin to query (e.g., 'https://example.com').

        Returns:
            dict: Contains 'usage' (bytes), 'quota' (bytes), 'override_active' (bool),
                'usage_breakdown' (list), and 'usage_mb' (float, computed convenience field).
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageCDPHandler.get_usage_and_quota(tab, origin)

    @section_tool("storage-cdp-management")
    async def storage_track_cache_storage_for_origin(instance_id: str, origin: str) -> bool:
        """
        Start tracking cache storage for a given origin.

        Registers the origin for cache storage tracking, enabling the browser
        to emit cache storage events for that origin.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin to track (e.g., 'https://example.com').

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageCDPHandler.track_cache_storage_for_origin(tab, origin)

    @section_tool("storage-cdp-management")
    async def storage_untrack_cache_storage_for_origin(instance_id: str, origin: str) -> bool:
        """
        Stop tracking cache storage for a given origin.

        Unregisters the origin from cache storage tracking, stopping cache
        storage events from being emitted for that origin.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin to untrack (e.g., 'https://example.com').

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageCDPHandler.untrack_cache_storage_for_origin(tab, origin)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
