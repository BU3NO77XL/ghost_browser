"""Storage CDP domain handler for origin data management, quota, and cache tracking via CDP."""

import asyncio
from typing import Any, Dict

from nodriver import Tab, cdp

from core.debug_logger import debug_logger


class StorageCDPHandler:
    """Handles browser storage CDP operations via CDP Storage domain."""

    @staticmethod
    async def clear_data_for_origin(
        tab: Tab, origin: str, storage_types: str
    ) -> bool:
        """
        Clear storage data for a given origin.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin to clear data for (e.g., 'https://example.com').
            storage_types (str): Comma-separated list of storage types to clear
                (e.g., 'cookies,localStorage' or 'all').

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "StorageCDPHandler",
            "clear_data_for_origin",
            f"Clearing storage data for origin: {origin}, types: {storage_types}",
        )
        try:
            await tab.send(
                cdp.storage.clear_data_for_origin(
                    origin=origin, storage_types=storage_types
                )
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
                "StorageCDPHandler",
                "clear_data_for_origin",
                e,
                {"origin": origin, "storage_types": storage_types},
            )
            raise

    @staticmethod
    async def get_usage_and_quota(tab: Tab, origin: str) -> Dict[str, Any]:
        """
        Get storage usage and quota for a given origin.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin to query (e.g., 'https://example.com').

        Returns:
            Dict[str, Any]: Dict with 'usage', 'quota', 'override_active',
                'usage_breakdown', and computed 'usage_mb' fields.
        """
        debug_logger.log_info(
            "StorageCDPHandler",
            "get_usage_and_quota",
            f"Getting usage and quota for origin: {origin}",
        )
        try:
            result = await tab.send(
                cdp.storage.get_usage_and_quota(origin=origin)
            )
            usage = result.usage
            quota = result.quota
            override_active = result.override_active
            usage_breakdown = result.usage_breakdown

            # Convert usage_breakdown items to plain dicts if needed
            breakdown_list = []
            if usage_breakdown:
                for item in usage_breakdown:
                    if hasattr(item, "__dict__"):
                        breakdown_list.append(vars(item))
                    elif isinstance(item, dict):
                        breakdown_list.append(item)
                    else:
                        breakdown_list.append(str(item))

            usage_mb = round(usage / (1024 * 1024), 2)

            return {
                "usage": usage,
                "quota": quota,
                "override_active": override_active,
                "usage_breakdown": breakdown_list,
                "usage_mb": usage_mb,
            }
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
                "StorageCDPHandler",
                "get_usage_and_quota",
                e,
                {"origin": origin},
            )
            raise

    @staticmethod
    async def track_cache_storage_for_origin(tab: Tab, origin: str) -> bool:
        """
        Start tracking cache storage for a given origin.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin to track (e.g., 'https://example.com').

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "StorageCDPHandler",
            "track_cache_storage_for_origin",
            f"Tracking cache storage for origin: {origin}",
        )
        try:
            await tab.send(
                cdp.storage.track_cache_storage_for_origin(origin=origin)
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
                "StorageCDPHandler",
                "track_cache_storage_for_origin",
                e,
                {"origin": origin},
            )
            raise

    @staticmethod
    async def untrack_cache_storage_for_origin(tab: Tab, origin: str) -> bool:
        """
        Stop tracking cache storage for a given origin.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin to untrack (e.g., 'https://example.com').

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "StorageCDPHandler",
            "untrack_cache_storage_for_origin",
            f"Untracking cache storage for origin: {origin}",
        )
        try:
            await tab.send(
                cdp.storage.untrack_cache_storage_for_origin(origin=origin)
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
                "StorageCDPHandler",
                "untrack_cache_storage_for_origin",
                e,
                {"origin": origin},
            )
            raise
