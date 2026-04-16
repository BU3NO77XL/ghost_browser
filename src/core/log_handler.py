"""Log domain handler for browser log entries and violation reporting via CDP."""

import asyncio
from typing import Any, Dict, List

from nodriver import Tab, cdp

from core.debug_logger import debug_logger


class LogHandler:
    """Handles browser log operations via CDP Log domain."""

    @staticmethod
    async def enable_log(tab: Tab) -> bool:
        """
        Enable the Log domain, sending collected entries to the client.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info("LogHandler", "enable_log", "Enabling Log domain")
        try:
            await tab.send(cdp.log.enable())
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
            debug_logger.log_error("LogHandler", "enable_log", e, {})
            raise

    @staticmethod
    async def disable_log(tab: Tab) -> bool:
        """
        Disable the Log domain, preventing further log entries from being reported.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info("LogHandler", "disable_log", "Disabling Log domain")
        try:
            await tab.send(cdp.log.disable())
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
            debug_logger.log_error("LogHandler", "disable_log", e, {})
            raise

    @staticmethod
    async def clear_log(tab: Tab) -> bool:
        """
        Clear the browser log.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info("LogHandler", "clear_log", "Clearing Log")
        try:
            await tab.send(cdp.log.clear())
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
            debug_logger.log_error("LogHandler", "clear_log", e, {})
            raise

    @staticmethod
    async def start_violations_report(tab: Tab, settings: List[Dict[str, Any]]) -> bool:
        """
        Start violation reporting with the given settings.

        Args:
            tab (Tab): The browser tab object.
            settings (List[Dict[str, Any]]): List of violation settings, each with
                'name' (str) and 'threshold' (float) keys.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "LogHandler",
            "start_violations_report",
            f"Starting violations report with {len(settings)} setting(s)",
        )
        try:
            config = [
                cdp.log.ViolationSetting(
                    name=s["name"],
                    threshold=float(s["threshold"]),
                )
                for s in settings
            ]
            await tab.send(cdp.log.start_violations_report(config=config))
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
                "LogHandler", "start_violations_report", e, {"settings": settings}
            )
            raise

    @staticmethod
    async def stop_violations_report(tab: Tab) -> bool:
        """
        Stop violation reporting.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info("LogHandler", "stop_violations_report", "Stopping violations report")
        try:
            await tab.send(cdp.log.stop_violations_report())
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
            debug_logger.log_error("LogHandler", "stop_violations_report", e, {})
            raise
