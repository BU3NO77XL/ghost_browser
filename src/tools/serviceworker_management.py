"""ServiceWorker management MCP tools for PWA service worker control."""

from typing import Any, Dict, List

from core.login_guard import check_pending_login_guard
from core.serviceworker_handler import ServiceWorkerHandler


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("serviceworker-management")
    async def list_service_workers(instance_id: str) -> List[Dict[str, Any]]:
        """
        List all registered service workers for the current page.

        Service workers are scripts that run in the background, enabling PWA features
        like offline support, push notifications, and background sync.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            List[Dict[str, Any]]: List of service worker registrations with scope,
                                   script URL, and activation state.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await ServiceWorkerHandler.list_service_workers(tab)

    @section_tool("serviceworker-management")
    async def unregister_service_worker(instance_id: str, scope_url: str) -> bool:
        """
        Unregister a service worker by its scope URL.

        Unregistering removes the service worker and disables its features (offline
        support, push notifications) for the given scope.

        Args:
            instance_id (str): Browser instance ID.
            scope_url (str): The scope URL of the service worker (e.g., 'https://example.com/').

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await ServiceWorkerHandler.unregister_service_worker(tab, scope_url)

    @section_tool("serviceworker-management")
    async def force_update_service_worker(instance_id: str, scope_url: str) -> bool:
        """
        Force update a service worker (bypass the 24-hour update throttle).

        Useful for testing new service worker versions without waiting for the
        browser's automatic update check.

        Args:
            instance_id (str): Browser instance ID.
            scope_url (str): The scope URL of the service worker to update.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await ServiceWorkerHandler.force_update_service_worker(tab, scope_url)

    @section_tool("serviceworker-management")
    async def deliver_push_message(
        instance_id: str, origin: str, registration_id: str, data: str
    ) -> bool:
        """
        Deliver a simulated push message to a service worker.

        Useful for testing push notification handling without a real push server.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin of the service worker (e.g., 'https://example.com').
            registration_id (str): The service worker registration ID.
            data (str): The push message payload (JSON string or plain text).

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await ServiceWorkerHandler.deliver_push_message(tab, origin, registration_id, data)

    @section_tool("serviceworker-management")
    async def dispatch_sync_event(
        instance_id: str,
        origin: str,
        registration_id: str,
        tag: str,
        last_chance: bool = False,
    ) -> bool:
        """
        Dispatch a background sync event to a service worker.

        Background sync allows service workers to defer actions until the user
        has stable connectivity.

        Args:
            instance_id (str): Browser instance ID.
            origin (str): The origin of the service worker.
            registration_id (str): The service worker registration ID.
            tag (str): The sync event tag (identifies the sync operation).
            last_chance (bool): Whether this is the last chance to sync before giving up.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await ServiceWorkerHandler.dispatch_sync_event(
            tab, origin, registration_id, tag, last_chance
        )

    @section_tool("serviceworker-management")
    async def skip_waiting_service_worker(instance_id: str, scope_url: str) -> bool:
        """
        Skip the waiting phase and immediately activate a new service worker.

        Normally a new service worker waits until all tabs using the old version
        are closed. This forces immediate activation.

        Args:
            instance_id (str): Browser instance ID.
            scope_url (str): The scope URL of the service worker.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await ServiceWorkerHandler.skip_waiting(tab, scope_url)

    @section_tool("serviceworker-management")
    async def set_service_worker_force_update(instance_id: str, force_update: bool) -> bool:
        """
        Set whether service workers should be force-updated on every page load.

        When enabled, the browser will always fetch a fresh copy of the service
        worker script on each page load, bypassing the normal update throttle.

        Args:
            instance_id (str): Browser instance ID.
            force_update (bool): True to force update on every page load.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await ServiceWorkerHandler.set_force_update_on_page_load(tab, force_update)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
