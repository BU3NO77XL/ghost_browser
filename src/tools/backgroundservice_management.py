"""BackgroundService management MCP tools for observing PWA background service events."""

from typing import Any, Dict, List

from core.backgroundservice_handler import BackgroundServiceHandler, VALID_SERVICE_TYPES
from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("backgroundservice-management")
    async def start_observing_background_service(
        instance_id: str, service: str
    ) -> bool:
        """
        Start observing background service events for a given service type.

        Supported service types:
        - backgroundFetch: Background Fetch API events
        - backgroundSync: Background Sync API events
        - pushMessaging: Push messaging events
        - notifications: Notification events
        - paymentHandler: Payment handler events
        - periodicBackgroundSync: Periodic Background Sync events

        Args:
            instance_id (str): Browser instance ID.
            service (str): The background service type to observe.

        Returns:
            bool: True if observation started successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await BackgroundServiceHandler.start_observing(tab, service)

    @section_tool("backgroundservice-management")
    async def stop_observing_background_service(
        instance_id: str, service: str
    ) -> bool:
        """
        Stop observing background service events for a given service type.

        Args:
            instance_id (str): Browser instance ID.
            service (str): The background service type to stop observing.

        Returns:
            bool: True if observation stopped successfully.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await BackgroundServiceHandler.stop_observing(tab, service)

    @section_tool("backgroundservice-management")
    async def get_background_service_events(
        instance_id: str, service: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recorded background service events for a given service type.

        Call start_observing_background_service first to begin recording events.

        Args:
            instance_id (str): Browser instance ID.
            service (str): The background service type to get events for.

        Returns:
            List[Dict[str, Any]]: List of recorded background service events.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await BackgroundServiceHandler.get_events(tab, service)

    @section_tool("backgroundservice-management")
    async def clear_background_service_events(
        instance_id: str, service: str
    ) -> bool:
        """
        Clear all recorded background service events for a given service type.

        Args:
            instance_id (str): Browser instance ID.
            service (str): The background service type to clear events for.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await BackgroundServiceHandler.clear_events(tab, service)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
