"""ServiceWorker domain handler for PWA service worker management via CDP."""

import asyncio
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.cdp_result import runtime_value
from core.debug_logger import debug_logger


class ServiceWorkerHandler:
    """Handles Service Worker operations via CDP ServiceWorker domain."""

    @staticmethod
    async def enable_serviceworker_domain(tab: Tab) -> None:
        """
        Enable the ServiceWorker domain for the given tab.

        Args:
            tab (Tab): The browser tab object.
        """
        try:
            await tab.send(cdp.service_worker.enable())
        except Exception as e:
            error_msg = str(e).lower()
            if "already enabled" in error_msg:
                return
            raise

    @staticmethod
    async def list_service_workers(tab: Tab) -> List[Dict[str, Any]]:
        """
        List all registered service workers for the current page.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            List[Dict[str, Any]]: List of service worker registrations with scope,
                                   script URL, and status.
        """
        debug_logger.log_info(
            "ServiceWorkerHandler", "list_service_workers", "Listing service workers"
        )
        try:
            await ServiceWorkerHandler.enable_serviceworker_domain(tab)
            # Use JS to enumerate service workers since CDP doesn't have a direct list command
            result = await tab.send(
                cdp.runtime.evaluate(
                    expression="""
                    (async () => {
                        if (!navigator.serviceWorker) return [];
                        const reg = await navigator.serviceWorker.getRegistrations();
                        return reg.map(r => ({
                            scope: r.scope,
                            script_url: r.active ? r.active.scriptURL : (r.installing ? r.installing.scriptURL : ''),
                            state: r.active ? 'activated' : (r.installing ? 'installing' : (r.waiting ? 'waiting' : 'unknown'))
                        }));
                    })()
                    """,
                    await_promise=True,
                    return_by_value=True,
                )
            )
            value = runtime_value(result)
            if value:
                return value
            return []
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("ServiceWorkerHandler", "list_service_workers", e, {})
            raise

    @staticmethod
    async def unregister_service_worker(tab: Tab, scope_url: str) -> bool:
        """
        Unregister a service worker by its scope URL.

        Args:
            tab (Tab): The browser tab object.
            scope_url (str): The scope URL of the service worker to unregister.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "ServiceWorkerHandler",
            "unregister_service_worker",
            f"Unregistering service worker: {scope_url}",
        )
        try:
            await ServiceWorkerHandler.enable_serviceworker_domain(tab)
            await tab.send(cdp.service_worker.unregister(scope_url=scope_url))
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
                "ServiceWorkerHandler",
                "unregister_service_worker",
                e,
                {"scope_url": scope_url},
            )
            raise

    @staticmethod
    async def force_update_service_worker(tab: Tab, scope_url: str) -> bool:
        """
        Force update a service worker by triggering a new install.

        Args:
            tab (Tab): The browser tab object.
            scope_url (str): The scope URL of the service worker to update.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "ServiceWorkerHandler",
            "force_update_service_worker",
            f"Force updating service worker: {scope_url}",
        )
        try:
            await ServiceWorkerHandler.enable_serviceworker_domain(tab)
            await tab.send(cdp.service_worker.update_registration(scope_url=scope_url))
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
                "ServiceWorkerHandler",
                "force_update_service_worker",
                e,
                {"scope_url": scope_url},
            )
            raise

    @staticmethod
    async def deliver_push_message(tab: Tab, origin: str, registration_id: str, data: str) -> bool:
        """
        Deliver a push message to a service worker.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin of the service worker.
            registration_id (str): The service worker registration ID.
            data (str): The push message data (JSON string or plain text).

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "ServiceWorkerHandler",
            "deliver_push_message",
            f"Delivering push message to registration: {registration_id}",
        )
        try:
            await ServiceWorkerHandler.enable_serviceworker_domain(tab)
            await tab.send(
                cdp.service_worker.deliver_push_message(
                    origin=origin,
                    registration_id=registration_id,
                    data=data,
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
                "ServiceWorkerHandler",
                "deliver_push_message",
                e,
                {"origin": origin, "registration_id": registration_id},
            )
            raise

    @staticmethod
    async def dispatch_sync_event(
        tab: Tab, origin: str, registration_id: str, tag: str, last_chance: bool = False
    ) -> bool:
        """
        Dispatch a background sync event to a service worker.

        Args:
            tab (Tab): The browser tab object.
            origin (str): The origin of the service worker.
            registration_id (str): The service worker registration ID.
            tag (str): The sync event tag.
            last_chance (bool): Whether this is the last chance to sync.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "ServiceWorkerHandler",
            "dispatch_sync_event",
            f"Dispatching sync event '{tag}' to registration: {registration_id}",
        )
        try:
            await ServiceWorkerHandler.enable_serviceworker_domain(tab)
            await tab.send(
                cdp.service_worker.dispatch_sync_event(
                    origin=origin,
                    registration_id=registration_id,
                    tag=tag,
                    last_chance=last_chance,
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
                "ServiceWorkerHandler",
                "dispatch_sync_event",
                e,
                {"origin": origin, "registration_id": registration_id, "tag": tag},
            )
            raise

    @staticmethod
    async def skip_waiting(tab: Tab, scope_url: str) -> bool:
        """
        Skip the waiting phase for a service worker (activate immediately).

        Args:
            tab (Tab): The browser tab object.
            scope_url (str): The scope URL of the service worker.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "ServiceWorkerHandler",
            "skip_waiting",
            f"Skipping waiting for service worker: {scope_url}",
        )
        try:
            await ServiceWorkerHandler.enable_serviceworker_domain(tab)
            await tab.send(cdp.service_worker.skip_waiting(scope_url=scope_url))
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
                "ServiceWorkerHandler", "skip_waiting", e, {"scope_url": scope_url}
            )
            raise

    @staticmethod
    async def set_force_update_on_page_load(tab: Tab, force_update: bool) -> bool:
        """
        Set whether service workers should be force-updated on every page load.

        Args:
            tab (Tab): The browser tab object.
            force_update (bool): True to force update on every page load.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "ServiceWorkerHandler",
            "set_force_update_on_page_load",
            f"Setting force update on page load: {force_update}",
        )
        try:
            await ServiceWorkerHandler.enable_serviceworker_domain(tab)
            await tab.send(
                cdp.service_worker.set_force_update_on_page_load(
                    force_update_on_page_load=force_update
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
                "ServiceWorkerHandler",
                "set_force_update_on_page_load",
                e,
                {"force_update": force_update},
            )
            raise
