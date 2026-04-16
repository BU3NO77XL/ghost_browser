"""BackgroundService domain handler for observing PWA background service events via CDP."""

import asyncio
from typing import Any, Dict, List

from nodriver import Tab, cdp

from core.debug_logger import debug_logger

# Valid service types for the BackgroundService CDP domain
VALID_SERVICE_TYPES = {
    "backgroundFetch",
    "backgroundSync",
    "pushMessaging",
    "notifications",
    "paymentHandler",
    "periodicBackgroundSync",
}


class BackgroundServiceHandler:
    """Handles background service event observation via CDP BackgroundService domain."""

    # In-memory store for recorded events per tab (keyed by tab id)
    _events: Dict[str, List[Dict[str, Any]]] = {}

    @staticmethod
    async def start_observing(tab: Tab, service: str) -> bool:
        """
        Start observing background service events for a given service type.

        Supported service types: backgroundFetch, backgroundSync, pushMessaging,
        notifications, paymentHandler, periodicBackgroundSync.

        Args:
            tab (Tab): The browser tab object.
            service (str): The background service type to observe.

        Returns:
            bool: True if observation started successfully.
        """
        if service not in VALID_SERVICE_TYPES:
            raise ValueError(
                f"Invalid service type: '{service}'. "
                f"Valid types: {sorted(VALID_SERVICE_TYPES)}"
            )
        debug_logger.log_info(
            "BackgroundServiceHandler",
            "start_observing",
            f"Starting observation for service: {service}",
        )
        try:
            await tab.send(
                cdp.background_service.start_observing(service=cdp.background_service.ServiceName(service))
            )
            tab_key = str(id(tab))
            if tab_key not in BackgroundServiceHandler._events:
                BackgroundServiceHandler._events[tab_key] = []
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
                "BackgroundServiceHandler",
                "start_observing",
                e,
                {"service": service},
            )
            raise

    @staticmethod
    async def stop_observing(tab: Tab, service: str) -> bool:
        """
        Stop observing background service events for a given service type.

        Args:
            tab (Tab): The browser tab object.
            service (str): The background service type to stop observing.

        Returns:
            bool: True if observation stopped successfully.
        """
        if service not in VALID_SERVICE_TYPES:
            raise ValueError(
                f"Invalid service type: '{service}'. "
                f"Valid types: {sorted(VALID_SERVICE_TYPES)}"
            )
        debug_logger.log_info(
            "BackgroundServiceHandler",
            "stop_observing",
            f"Stopping observation for service: {service}",
        )
        try:
            await tab.send(
                cdp.background_service.stop_observing(service=cdp.background_service.ServiceName(service))
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
                "BackgroundServiceHandler",
                "stop_observing",
                e,
                {"service": service},
            )
            raise

    @staticmethod
    async def get_events(tab: Tab, service: str) -> List[Dict[str, Any]]:
        """
        Retrieve recorded background service events for a given service type.

        Note: Events are collected via CDP event listeners. Call start_observing
        first to begin recording events.

        Args:
            tab (Tab): The browser tab object.
            service (str): The background service type to get events for.

        Returns:
            List[Dict[str, Any]]: List of recorded background service events.
        """
        debug_logger.log_info(
            "BackgroundServiceHandler",
            "get_events",
            f"Getting events for service: {service}",
        )
        tab_key = str(id(tab))
        events = BackgroundServiceHandler._events.get(tab_key, [])
        if service:
            events = [e for e in events if e.get("service") == service]
        return events

    @staticmethod
    async def clear_events(tab: Tab, service: str) -> bool:
        """
        Clear recorded background service events for a given service type.

        Args:
            tab (Tab): The browser tab object.
            service (str): The background service type to clear events for.

        Returns:
            bool: True if successful.
        """
        if service not in VALID_SERVICE_TYPES:
            raise ValueError(
                f"Invalid service type: '{service}'. "
                f"Valid types: {sorted(VALID_SERVICE_TYPES)}"
            )
        debug_logger.log_info(
            "BackgroundServiceHandler",
            "clear_events",
            f"Clearing events for service: {service}",
        )
        try:
            await tab.send(
                cdp.background_service.clear_events(service=cdp.background_service.ServiceName(service))
            )
            tab_key = str(id(tab))
            if tab_key in BackgroundServiceHandler._events:
                BackgroundServiceHandler._events[tab_key] = [
                    e for e in BackgroundServiceHandler._events[tab_key]
                    if e.get("service") != service
                ]
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
                "BackgroundServiceHandler",
                "clear_events",
                e,
                {"service": service},
            )
            raise
