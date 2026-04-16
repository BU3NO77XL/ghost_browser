"""Storage management MCP tools for LocalStorage, SessionStorage, IndexedDB, and Cache Storage."""

from typing import Any, Dict, List, Optional

from core.login_guard import check_pending_login_guard
from core.storage_handler import StorageHandler


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    # -------------------------------------------------------------------------
    # LocalStorage tools
    # -------------------------------------------------------------------------

    @section_tool("storage-management")
    async def get_local_storage(instance_id: str, origin: str) -> Dict[str, str]:
        """
        Get all LocalStorage items for a given origin.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin (e.g., 'https://example.com').

        Returns:
            Dict[str, str]: Key-value pairs from LocalStorage.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.get_local_storage(tab, origin)

    @section_tool("storage-management")
    async def set_local_storage_item(instance_id: str, origin: str, key: str, value: str) -> bool:
        """
        Set a LocalStorage item for a given origin.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin (e.g., 'https://example.com').
            key (str): The storage key.
            value (str): The storage value.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.set_local_storage_item(tab, origin, key, value)

    @section_tool("storage-management")
    async def remove_local_storage_item(instance_id: str, origin: str, key: str) -> bool:
        """
        Remove a LocalStorage item for a given origin.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin (e.g., 'https://example.com').
            key (str): The storage key to remove.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.remove_local_storage_item(tab, origin, key)

    @section_tool("storage-management")
    async def clear_local_storage(instance_id: str, origin: str) -> bool:
        """
        Clear all LocalStorage items for a given origin.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin (e.g., 'https://example.com').

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.clear_local_storage(tab, origin)

    # -------------------------------------------------------------------------
    # SessionStorage tools
    # -------------------------------------------------------------------------

    @section_tool("storage-management")
    async def get_session_storage(instance_id: str, origin: str) -> Dict[str, str]:
        """
        Get all SessionStorage items for a given origin.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin (e.g., 'https://example.com').

        Returns:
            Dict[str, str]: Key-value pairs from SessionStorage.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.get_session_storage(tab, origin)

    @section_tool("storage-management")
    async def set_session_storage_item(instance_id: str, origin: str, key: str, value: str) -> bool:
        """
        Set a SessionStorage item for a given origin.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin (e.g., 'https://example.com').
            key (str): The storage key.
            value (str): The storage value.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.set_session_storage_item(tab, origin, key, value)

    @section_tool("storage-management")
    async def remove_session_storage_item(instance_id: str, origin: str, key: str) -> bool:
        """
        Remove a SessionStorage item for a given origin.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin (e.g., 'https://example.com').
            key (str): The storage key to remove.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.remove_session_storage_item(tab, origin, key)

    @section_tool("storage-management")
    async def clear_session_storage(instance_id: str, origin: str) -> bool:
        """
        Clear all SessionStorage items for a given origin.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin (e.g., 'https://example.com').

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.clear_session_storage(tab, origin)

    # -------------------------------------------------------------------------
    # IndexedDB tools
    # -------------------------------------------------------------------------

    @section_tool("storage-management")
    async def list_indexed_databases(instance_id: str, origin: str) -> List[str]:
        """
        List all IndexedDB database names for a given origin.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin (e.g., 'https://example.com').

        Returns:
            List[str]: List of database names.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.list_indexed_databases(tab, origin)

    @section_tool("storage-management")
    async def get_indexed_db_schema(
        instance_id: str, origin: str, database_name: str
    ) -> Dict[str, Any]:
        """
        Get the schema of an IndexedDB database (object stores and indexes).

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin (e.g., 'https://example.com').
            database_name (str): The database name.

        Returns:
            Dict[str, Any]: Database schema including object stores and indexes.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.get_database_schema(tab, origin, database_name)

    @section_tool("storage-management")
    async def get_indexed_db_data(
        instance_id: str,
        origin: str,
        database_name: str,
        object_store_name: str,
        index_name: Optional[str] = None,
        skip_count: int = 0,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """
        Query data from an IndexedDB object store.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin (e.g., 'https://example.com').
            database_name (str): The database name.
            object_store_name (str): The object store name.
            index_name (Optional[str]): Optional index name to query by.
            skip_count (int): Number of records to skip (for pagination).
            page_size (int): Maximum number of records to return (default 50).

        Returns:
            Dict[str, Any]: Object store data with keys and values.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.get_object_store_data(
            tab, origin, database_name, object_store_name, index_name, skip_count, page_size
        )

    @section_tool("storage-management")
    async def delete_indexed_database(instance_id: str, origin: str, database_name: str) -> bool:
        """
        Delete an IndexedDB database.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin (e.g., 'https://example.com').
            database_name (str): The database name to delete.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.delete_indexed_database(tab, origin, database_name)

    # -------------------------------------------------------------------------
    # Cache Storage tools
    # -------------------------------------------------------------------------

    @section_tool("storage-management")
    async def list_cache_storage(instance_id: str, security_origin: str) -> List[str]:
        """
        List all Cache Storage cache names for a given origin.

        Args:
            instance_id (str): Browser instance ID.
            security_origin (str): The origin (e.g., 'https://example.com').

        Returns:
            List[str]: List of cache names.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.list_cache_storage(tab, security_origin)

    @section_tool("storage-management")
    async def get_cached_response(
        instance_id: str,
        security_origin: str,
        cache_name: str,
        request_url: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached response from Cache Storage.

        Args:
            instance_id (str): Browser instance ID.
            security_origin (str): The origin (e.g., 'https://example.com').
            cache_name (str): The name of the cache.
            request_url (str): The URL of the cached request.

        Returns:
            Optional[Dict[str, Any]]: Response headers and metadata, or None if not found.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.get_cached_response(
            tab, security_origin, cache_name, request_url
        )

    @section_tool("storage-management")
    async def delete_cache(instance_id: str, security_origin: str, cache_name: str) -> bool:
        """
        Delete a Cache Storage cache by name.

        Args:
            instance_id (str): Browser instance ID.
            security_origin (str): The origin (e.g., 'https://example.com').
            cache_name (str): The name of the cache to delete.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await StorageHandler.delete_cache(tab, security_origin, cache_name)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
