"""SystemInfo domain handler for querying browser/GPU/process information via CDP."""

import asyncio
from typing import Any, Dict, List

from nodriver import Tab, cdp

from core.debug_logger import debug_logger


class SystemInfoHandler:
    """Handles system information queries via CDP SystemInfo domain."""

    @staticmethod
    async def get_info(tab: Tab) -> Dict[str, Any]:
        """
        Return information about the system.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            Dict with keys ``gpu``, ``model_name``, and ``command_line``.
        """
        debug_logger.log_info("SystemInfoHandler", "get_info", "Fetching system info")
        try:
            result = await tab.send(cdp.system_info.get_info())
            # Convert the GPUInfo object to a serialisable dict.
            gpu_obj = result.gpu
            try:
                gpu = vars(gpu_obj)
            except TypeError:
                gpu = str(gpu_obj)
            return {
                "gpu": gpu,
                "model_name": result.model_name,
                "command_line": result.command_line,
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
            debug_logger.log_error("SystemInfoHandler", "get_info", e, {})
            raise

    @staticmethod
    async def get_feature_state(tab: Tab, feature_flag: str) -> Dict[str, bool]:
        """
        Return the state of a browser feature flag.

        Args:
            tab (Tab): The browser tab object.
            feature_flag (str): The name of the feature flag to query.

        Returns:
            Dict with key ``feature_enabled`` (bool).
        """
        debug_logger.log_info(
            "SystemInfoHandler",
            "get_feature_state",
            f"Fetching feature state for '{feature_flag}'",
        )
        try:
            result = await tab.send(cdp.system_info.get_feature_state(feature_flag))
            return {"feature_enabled": bool(result.feature_enabled)}
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
                "SystemInfoHandler",
                "get_feature_state",
                e,
                {"feature_flag": feature_flag},
            )
            raise

    @staticmethod
    async def get_process_info(tab: Tab) -> List[Dict[str, Any]]:
        """
        Return information about all running processes.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            List of dicts each with ``id``, ``type``, and ``cpu_time`` keys.
        """
        debug_logger.log_info("SystemInfoHandler", "get_process_info", "Fetching process info")
        try:
            result = await tab.send(cdp.system_info.get_process_info())
            processes = [
                {
                    "id": getattr(item, "id", None),
                    "type": getattr(item, "type", None),
                    "cpu_time": getattr(item, "cpu_time", None),
                }
                for item in result
            ]
            return processes
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("SystemInfoHandler", "get_process_info", e, {})
            raise
