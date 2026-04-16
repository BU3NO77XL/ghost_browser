"""Storage domain handler for LocalStorage, SessionStorage, IndexedDB, and Cache Storage."""

import asyncio
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.debug_logger import debug_logger
from core.response_handler import response_handler


class StorageHandler:
    """Handles browser storage operations via CDP Storage domain."""

    @staticmethod
    async def get_local_storage(tab: Tab, origin: str) -> Dict[str, str]:
        """
        Get all localStorage items for an origin.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin (e.g., 'https://example.com').

        Returns:
            Dict[str, str]: Dictionary of key-value pairs.
        """
        debug_logger.log_info(
            "StorageHandler",
            "get_local_storage",
            f"Getting localStorage for origin: {origin}",
        )
        try:
            storage_id = {"securityOrigin": origin, "isLocalStorage": True}
            result = await tab.send(cdp.dom_storage.get_dom_storage_items(storage_id))

            # Convert list of [key, value] pairs to dictionary
            items = {}
            if result and "entries" in result:
                for entry in result["entries"]:
                    if len(entry) >= 2:
                        items[entry[0]] = entry[1]

            debug_logger.log_info(
                "StorageHandler",
                "get_local_storage",
                f"Retrieved {len(items)} localStorage items",
            )
            return items
        except asyncio.TimeoutError:
            debug_logger.log_error(
                "StorageHandler",
                "get_local_storage",
                Exception("Operation timed out"),
                {"origin": origin},
            )
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                debug_logger.log_error(
                    "StorageHandler",
                    "get_local_storage",
                    e,
                    {"origin": origin, "error_type": "websocket"},
                )
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("StorageHandler", "get_local_storage", e, {"origin": origin})
            raise

    @staticmethod
    async def set_local_storage_item(tab: Tab, origin: str, key: str, value: str) -> bool:
        """
        Set a localStorage item.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin (e.g., 'https://example.com').
            key (str): The key to set.
            value (str): The value to set.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "StorageHandler",
            "set_local_storage_item",
            f"Setting localStorage item: {key} for origin: {origin}",
        )
        try:
            storage_id = {"securityOrigin": origin, "isLocalStorage": True}
            await tab.send(cdp.dom_storage.set_dom_storage_item(storage_id, key, value))
            debug_logger.log_info(
                "StorageHandler",
                "set_local_storage_item",
                f"Successfully set localStorage item: {key}",
            )
            return True
        except asyncio.TimeoutError:
            debug_logger.log_error(
                "StorageHandler",
                "set_local_storage_item",
                Exception("Operation timed out"),
                {"origin": origin, "key": key},
            )
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                debug_logger.log_error(
                    "StorageHandler",
                    "set_local_storage_item",
                    e,
                    {"origin": origin, "key": key, "error_type": "websocket"},
                )
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "StorageHandler",
                "set_local_storage_item",
                e,
                {"origin": origin, "key": key},
            )
            raise

    @staticmethod
    async def remove_local_storage_item(tab: Tab, origin: str, key: str) -> bool:
        """
        Remove a localStorage item.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin (e.g., 'https://example.com').
            key (str): The key to remove.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "StorageHandler",
            "remove_local_storage_item",
            f"Removing localStorage item: {key} for origin: {origin}",
        )
        try:
            storage_id = {"securityOrigin": origin, "isLocalStorage": True}
            await tab.send(cdp.dom_storage.remove_dom_storage_item(storage_id, key))
            debug_logger.log_info(
                "StorageHandler",
                "remove_local_storage_item",
                f"Successfully removed localStorage item: {key}",
            )
            return True
        except asyncio.TimeoutError:
            debug_logger.log_error(
                "StorageHandler",
                "remove_local_storage_item",
                Exception("Operation timed out"),
                {"origin": origin, "key": key},
            )
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                debug_logger.log_error(
                    "StorageHandler",
                    "remove_local_storage_item",
                    e,
                    {"origin": origin, "key": key, "error_type": "websocket"},
                )
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "StorageHandler",
                "remove_local_storage_item",
                e,
                {"origin": origin, "key": key},
            )
            raise

    @staticmethod
    async def clear_local_storage(tab: Tab, origin: str) -> bool:
        """
        Clear all localStorage items for an origin.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin (e.g., 'https://example.com').

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "StorageHandler",
            "clear_local_storage",
            f"Clearing localStorage for origin: {origin}",
        )
        try:
            storage_id = {"securityOrigin": origin, "isLocalStorage": True}
            await tab.send(cdp.dom_storage.clear(storage_id))
            debug_logger.log_info(
                "StorageHandler",
                "clear_local_storage",
                f"Successfully cleared localStorage for origin: {origin}",
            )
            return True
        except asyncio.TimeoutError:
            debug_logger.log_error(
                "StorageHandler",
                "clear_local_storage",
                Exception("Operation timed out"),
                {"origin": origin},
            )
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                debug_logger.log_error(
                    "StorageHandler",
                    "clear_local_storage",
                    e,
                    {"origin": origin, "error_type": "websocket"},
                )
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("StorageHandler", "clear_local_storage", e, {"origin": origin})
            raise

    @staticmethod
    async def get_session_storage(tab: Tab, origin: str) -> Dict[str, str]:
        """
        Get all sessionStorage items for an origin.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin (e.g., 'https://example.com').

        Returns:
            Dict[str, str]: Dictionary of key-value pairs.
        """
        debug_logger.log_info(
            "StorageHandler",
            "get_session_storage",
            f"Getting sessionStorage for origin: {origin}",
        )
        try:
            storage_id = {"securityOrigin": origin, "isLocalStorage": False}
            result = await tab.send(cdp.dom_storage.get_dom_storage_items(storage_id))

            # Convert list of [key, value] pairs to dictionary
            items = {}
            if result and "entries" in result:
                for entry in result["entries"]:
                    if len(entry) >= 2:
                        items[entry[0]] = entry[1]

            debug_logger.log_info(
                "StorageHandler",
                "get_session_storage",
                f"Retrieved {len(items)} sessionStorage items",
            )
            return items
        except asyncio.TimeoutError:
            debug_logger.log_error(
                "StorageHandler",
                "get_session_storage",
                Exception("Operation timed out"),
                {"origin": origin},
            )
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                debug_logger.log_error(
                    "StorageHandler",
                    "get_session_storage",
                    e,
                    {"origin": origin, "error_type": "websocket"},
                )
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("StorageHandler", "get_session_storage", e, {"origin": origin})
            raise

    @staticmethod
    async def set_session_storage_item(tab: Tab, origin: str, key: str, value: str) -> bool:
        """
        Set a sessionStorage item.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin (e.g., 'https://example.com').
            key (str): The key to set.
            value (str): The value to set.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "StorageHandler",
            "set_session_storage_item",
            f"Setting sessionStorage item: {key} for origin: {origin}",
        )
        try:
            storage_id = {"securityOrigin": origin, "isLocalStorage": False}
            await tab.send(cdp.dom_storage.set_dom_storage_item(storage_id, key, value))
            debug_logger.log_info(
                "StorageHandler",
                "set_session_storage_item",
                f"Successfully set sessionStorage item: {key}",
            )
            return True
        except asyncio.TimeoutError:
            debug_logger.log_error(
                "StorageHandler",
                "set_session_storage_item",
                Exception("Operation timed out"),
                {"origin": origin, "key": key},
            )
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                debug_logger.log_error(
                    "StorageHandler",
                    "set_session_storage_item",
                    e,
                    {"origin": origin, "key": key, "error_type": "websocket"},
                )
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "StorageHandler",
                "set_session_storage_item",
                e,
                {"origin": origin, "key": key},
            )
            raise

    @staticmethod
    async def remove_session_storage_item(tab: Tab, origin: str, key: str) -> bool:
        """
        Remove a sessionStorage item.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin (e.g., 'https://example.com').
            key (str): The key to remove.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "StorageHandler",
            "remove_session_storage_item",
            f"Removing sessionStorage item: {key} for origin: {origin}",
        )
        try:
            storage_id = {"securityOrigin": origin, "isLocalStorage": False}
            await tab.send(cdp.dom_storage.remove_dom_storage_item(storage_id, key))
            debug_logger.log_info(
                "StorageHandler",
                "remove_session_storage_item",
                f"Successfully removed sessionStorage item: {key}",
            )
            return True
        except asyncio.TimeoutError:
            debug_logger.log_error(
                "StorageHandler",
                "remove_session_storage_item",
                Exception("Operation timed out"),
                {"origin": origin, "key": key},
            )
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                debug_logger.log_error(
                    "StorageHandler",
                    "remove_session_storage_item",
                    e,
                    {"origin": origin, "key": key, "error_type": "websocket"},
                )
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "StorageHandler",
                "remove_session_storage_item",
                e,
                {"origin": origin, "key": key},
            )
            raise

    @staticmethod
    async def clear_session_storage(tab: Tab, origin: str) -> bool:
        """
        Clear all sessionStorage items for an origin.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin (e.g., 'https://example.com').

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "StorageHandler",
            "clear_session_storage",
            f"Clearing sessionStorage for origin: {origin}",
        )
        try:
            storage_id = {"securityOrigin": origin, "isLocalStorage": False}
            await tab.send(cdp.dom_storage.clear(storage_id))
            debug_logger.log_info(
                "StorageHandler",
                "clear_session_storage",
                f"Successfully cleared sessionStorage for origin: {origin}",
            )
            return True
        except asyncio.TimeoutError:
            debug_logger.log_error(
                "StorageHandler",
                "clear_session_storage",
                Exception("Operation timed out"),
                {"origin": origin},
            )
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                debug_logger.log_error(
                    "StorageHandler",
                    "clear_session_storage",
                    e,
                    {"origin": origin, "error_type": "websocket"},
                )
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("StorageHandler", "clear_session_storage", e, {"origin": origin})
            raise

    # IndexedDB Methods

    @staticmethod
    async def _enable_indexed_db(tab: Tab) -> None:
        """
        Enable IndexedDB domain (helper method).

        Args:
            tab (Tab): The browser tab object.
        """
        try:
            await tab.send(cdp.indexed_db.enable())
            debug_logger.log_info(
                "StorageHandler",
                "_enable_indexed_db",
                "IndexedDB domain enabled",
            )
        except Exception as e:
            debug_logger.log_error("StorageHandler", "_enable_indexed_db", e, {})
            # Don't raise - domain might already be enabled

    @staticmethod
    async def list_indexed_databases(tab: Tab, origin: str) -> List[str]:
        """
        List all IndexedDB database names for an origin.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin (e.g., 'https://example.com').

        Returns:
            List[str]: List of database names.
        """
        debug_logger.log_info(
            "StorageHandler",
            "list_indexed_databases",
            f"Listing IndexedDB databases for origin: {origin}",
        )
        try:
            # Enable IndexedDB domain first
            await StorageHandler._enable_indexed_db(tab)

            # Request database names
            result = await tab.send(cdp.indexed_db.request_database_names(security_origin=origin))

            # Handle both dict and object responses
            if hasattr(result, "database_names"):
                database_names = result.database_names or []
            elif isinstance(result, dict):
                database_names = result.get("databaseNames", [])
            else:
                database_names = []

            debug_logger.log_info(
                "StorageHandler",
                "list_indexed_databases",
                f"Found {len(database_names)} IndexedDB databases",
            )
            return database_names
        except asyncio.TimeoutError:
            debug_logger.log_error(
                "StorageHandler",
                "list_indexed_databases",
                Exception("Operation timed out"),
                {"origin": origin},
            )
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                debug_logger.log_error(
                    "StorageHandler",
                    "list_indexed_databases",
                    e,
                    {"origin": origin, "error_type": "websocket"},
                )
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "StorageHandler", "list_indexed_databases", e, {"origin": origin}
            )
            raise

    @staticmethod
    async def get_database_schema(tab: Tab, origin: str, database_name: str) -> Dict[str, Any]:
        """
        Get IndexedDB database schema including object stores and indexes.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin (e.g., 'https://example.com').
            database_name (str): The database name.

        Returns:
            Dict[str, Any]: Database schema with object stores and indexes.
        """
        debug_logger.log_info(
            "StorageHandler",
            "get_database_schema",
            f"Getting schema for database: {database_name} at origin: {origin}",
        )
        try:
            # Enable IndexedDB domain first
            await StorageHandler._enable_indexed_db(tab)

            # Request database schema
            result = await tab.send(
                cdp.indexed_db.request_database(security_origin=origin, database_name=database_name)
            )

            database_info = result.get("databaseWithObjectStores", {}) if result else {}

            debug_logger.log_info(
                "StorageHandler",
                "get_database_schema",
                f"Retrieved schema for database: {database_name}",
            )
            return database_info
        except asyncio.TimeoutError:
            debug_logger.log_error(
                "StorageHandler",
                "get_database_schema",
                Exception("Operation timed out"),
                {"origin": origin, "database_name": database_name},
            )
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                debug_logger.log_error(
                    "StorageHandler",
                    "get_database_schema",
                    e,
                    {"origin": origin, "database_name": database_name, "error_type": "websocket"},
                )
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "StorageHandler",
                "get_database_schema",
                e,
                {"origin": origin, "database_name": database_name},
            )
            raise

    @staticmethod
    async def get_object_store_data(
        tab: Tab,
        origin: str,
        database_name: str,
        object_store_name: str,
        skip_count: int = 0,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Get data from an IndexedDB object store.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin (e.g., 'https://example.com').
            database_name (str): The database name.
            object_store_name (str): The object store name.
            skip_count (int): Number of records to skip (for pagination).
            page_size (int): Maximum number of records to return.

        Returns:
            Dict[str, Any]: Object store data with entries and metadata.
        """
        debug_logger.log_info(
            "StorageHandler",
            "get_object_store_data",
            f"Getting data from object store: {object_store_name} in database: {database_name}",
        )
        try:
            # Enable IndexedDB domain first
            await StorageHandler._enable_indexed_db(tab)

            # Request object store data
            result = await tab.send(
                cdp.indexed_db.request_data(
                    security_origin=origin,
                    database_name=database_name,
                    object_store_name=object_store_name,
                    index_name="",  # Empty string for object store (not index)
                    skip_count=skip_count,
                    page_size=page_size,
                )
            )

            # Extract data entries
            object_store_data = result if result else {}

            # Handle large responses
            if object_store_data:
                handled_response = response_handler.handle_response(
                    object_store_data,
                    fallback_filename_prefix=f"indexeddb_{database_name}_{object_store_name}",
                    metadata={
                        "origin": origin,
                        "database_name": database_name,
                        "object_store_name": object_store_name,
                        "skip_count": skip_count,
                        "page_size": page_size,
                    },
                )

                debug_logger.log_info(
                    "StorageHandler",
                    "get_object_store_data",
                    f"Retrieved data from object store: {object_store_name}",
                )
                return handled_response

            return object_store_data
        except asyncio.TimeoutError:
            debug_logger.log_error(
                "StorageHandler",
                "get_object_store_data",
                Exception("Operation timed out"),
                {
                    "origin": origin,
                    "database_name": database_name,
                    "object_store_name": object_store_name,
                },
            )
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                debug_logger.log_error(
                    "StorageHandler",
                    "get_object_store_data",
                    e,
                    {
                        "origin": origin,
                        "database_name": database_name,
                        "object_store_name": object_store_name,
                        "error_type": "websocket",
                    },
                )
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "StorageHandler",
                "get_object_store_data",
                e,
                {
                    "origin": origin,
                    "database_name": database_name,
                    "object_store_name": object_store_name,
                },
            )
            raise

    @staticmethod
    async def delete_indexed_database(tab: Tab, origin: str, database_name: str) -> bool:
        """
        Delete an IndexedDB database.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin (e.g., 'https://example.com').
            database_name (str): The database name to delete.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "StorageHandler",
            "delete_indexed_database",
            f"Deleting IndexedDB database: {database_name} at origin: {origin}",
        )
        try:
            # Enable IndexedDB domain first
            await StorageHandler._enable_indexed_db(tab)

            # Delete database
            await tab.send(
                cdp.indexed_db.delete_database(security_origin=origin, database_name=database_name)
            )

            debug_logger.log_info(
                "StorageHandler",
                "delete_indexed_database",
                f"Successfully deleted database: {database_name}",
            )
            return True
        except asyncio.TimeoutError:
            debug_logger.log_error(
                "StorageHandler",
                "delete_indexed_database",
                Exception("Operation timed out"),
                {"origin": origin, "database_name": database_name},
            )
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                debug_logger.log_error(
                    "StorageHandler",
                    "delete_indexed_database",
                    e,
                    {"origin": origin, "database_name": database_name, "error_type": "websocket"},
                )
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "StorageHandler",
                "delete_indexed_database",
                e,
                {"origin": origin, "database_name": database_name},
            )
            raise

    # -------------------------------------------------------------------------
    # Cache Storage methods
    # -------------------------------------------------------------------------

    @staticmethod
    async def list_cache_storage(tab: Tab, security_origin: str) -> List[str]:
        """
        List all Cache Storage cache names for a given origin.

        Args:
            tab (Tab): The browser tab object.
            security_origin (str): The origin (e.g., 'https://example.com').

        Returns:
            List[str]: List of cache names.
        """
        debug_logger.log_info(
            "StorageHandler",
            "list_cache_storage",
            f"Listing caches for origin: {security_origin}",
        )
        try:
            result = await tab.send(
                cdp.cache_storage.request_cache_names(security_origin=security_origin)
            )
            caches = result if result else []
            names = [c.cache_name for c in caches]
            debug_logger.log_info(
                "StorageHandler",
                "list_cache_storage",
                f"Found {len(names)} caches",
            )
            return names
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "StorageHandler",
                "list_cache_storage",
                e,
                {"security_origin": security_origin},
            )
            raise

    @staticmethod
    async def get_cached_response(
        tab: Tab,
        security_origin: str,
        cache_name: str,
        request_url: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached response from Cache Storage.

        Args:
            tab (Tab): The browser tab object.
            security_origin (str): The origin (e.g., 'https://example.com').
            cache_name (str): The name of the cache.
            request_url (str): The URL of the cached request.

        Returns:
            Optional[Dict[str, Any]]: Response headers and body info, or None if not found.
        """
        debug_logger.log_info(
            "StorageHandler",
            "get_cached_response",
            f"Getting cached response for URL: {request_url} in cache: {cache_name}",
        )
        try:
            result = await tab.send(
                cdp.cache_storage.request_cached_response(
                    cache_id=cdp.cache_storage.CacheId(f"{security_origin}|{cache_name}"),
                    request_url=request_url,
                    request_headers=[],
                )
            )
            if result is None:
                return None
            response = result
            headers = {h.name: h.value for h in (response.headers or [])}
            return {
                "status": response.status,
                "status_text": response.status_text,
                "headers": headers,
                "body_size": response.body_size,
            }
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg or "no entry" in error_msg:
                return None
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "StorageHandler",
                "get_cached_response",
                e,
                {
                    "security_origin": security_origin,
                    "cache_name": cache_name,
                    "request_url": request_url,
                },
            )
            raise

    @staticmethod
    async def delete_cache(tab: Tab, security_origin: str, cache_name: str) -> bool:
        """
        Delete a Cache Storage cache by name.

        Args:
            tab (Tab): The browser tab object.
            security_origin (str): The origin (e.g., 'https://example.com').
            cache_name (str): The name of the cache to delete.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "StorageHandler",
            "delete_cache",
            f"Deleting cache: {cache_name} at origin: {security_origin}",
        )
        try:
            await tab.send(
                cdp.cache_storage.delete_cache(
                    cache_id=cdp.cache_storage.CacheId(f"{security_origin}|{cache_name}")
                )
            )
            debug_logger.log_info(
                "StorageHandler",
                "delete_cache",
                f"Successfully deleted cache: {cache_name}",
            )
            return True
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "StorageHandler",
                "delete_cache",
                e,
                {"security_origin": security_origin, "cache_name": cache_name},
            )
            raise
