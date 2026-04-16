"""
Login watcher — background poller that detects when the user leaves the login page.

Responsibility: DETECT ONLY. Does NOT save cookies, does NOT confirm login.

Flow:
  1. register_pending_login() → start_watching()
  2. Watcher polls every 1.5s checking URL + DOM
  3. User logs in and navigates away from login page
  4. Watcher sets _detected flag and stops
  5. AI calls confirm_manual_login → sees detected=True → clears pending state → done

After watcher timeout (10 min), the detected flag is set anyway so that
confirm_manual_login can still succeed via skip_login_check path.
"""

import asyncio
from typing import Dict, Set

from core.debug_logger import debug_logger


class LoginWatcher:
    POLL_INTERVAL = 1.5  # seconds between checks
    MAX_WAIT = 600.0  # give up after 10 minutes

    def __init__(self):
        self._tasks: Dict[str, asyncio.Task] = {}
        self._detected: Set[str] = set()
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def start_watching(self, instance_id: str, tab) -> None:
        """Start background polling for this instance."""
        async with self._lock:
            # Cancel existing task if any
            existing = self._tasks.get(instance_id)
            if existing and not existing.done():
                return  # already watching
            task = asyncio.create_task(
                self._watch_loop(instance_id, tab),
                name=f"login_watcher_{instance_id[:8]}",
            )
            self._tasks[instance_id] = task
        debug_logger.log_info(
            "login_watcher", "start_watching", f"Watcher started for {instance_id}"
        )

    async def stop_watching(self, instance_id: str) -> None:
        """Cancel watcher task and clean up detected flag."""
        async with self._lock:
            task = self._tasks.pop(instance_id, None)
            if task and not task.done():
                task.cancel()
            self._detected.discard(instance_id)

    async def is_login_detected(self, instance_id: str) -> bool:
        """True if watcher detected the user left the login page."""
        async with self._lock:
            # Also clean up done tasks opportunistically
            self._cleanup_done_tasks_unsafe()
            return instance_id in self._detected

    async def consume_detected(self, instance_id: str) -> bool:
        """Read and clear the detected flag atomically. Returns True if was detected."""
        async with self._lock:
            if instance_id in self._detected:
                self._detected.discard(instance_id)
                return True
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cleanup_done_tasks_unsafe(self) -> None:
        """Remove completed tasks from _tasks dict. Must be called with lock held."""
        done = [iid for iid, t in self._tasks.items() if t.done()]
        for iid in done:
            del self._tasks[iid]

    # ------------------------------------------------------------------
    # Background loop
    # ------------------------------------------------------------------

    async def _watch_loop(self, instance_id: str, tab) -> None:
        from core.manual_login_handler import LOGIN_URL_INDICATORS

        loop = asyncio.get_event_loop()
        deadline = loop.time() + self.MAX_WAIT

        try:
            while loop.time() < deadline:
                await asyncio.sleep(self.POLL_INTERVAL)

                # Stop if already handled externally
                async with self._lock:
                    if instance_id in self._detected:
                        return

                try:
                    left = await self._left_login_page(tab, LOGIN_URL_INDICATORS)
                except Exception as e:
                    debug_logger.log_warning(
                        "login_watcher", "_watch_loop", f"{instance_id}: {type(e).__name__}: {e}"
                    )
                    continue

                if not left:
                    continue

                # User left the login page — signal detection
                async with self._lock:
                    self._detected.add(instance_id)
                debug_logger.log_info(
                    "login_watcher", "_watch_loop", f"Login detected for {instance_id}"
                )
                return

            # Timeout reached — set detected anyway so confirm_manual_login
            # can still succeed via skip_login_check=True path.
            async with self._lock:
                if instance_id not in self._detected:
                    self._detected.add(instance_id)
            debug_logger.log_warning(
                "login_watcher",
                "_watch_loop",
                f"Watcher timed out for {instance_id} — setting detected flag as fallback",
            )
        except asyncio.CancelledError:
            debug_logger.log_info(
                "login_watcher", "_watch_loop", f"Watcher cancelled for {instance_id}"
            )
        finally:
            # Clean up task reference
            async with self._lock:
                self._tasks.pop(instance_id, None)

    @staticmethod
    async def _left_login_page(tab, login_url_indicators) -> bool:
        """Returns True when the browser is no longer on a login page."""
        try:
            url = await asyncio.wait_for(tab.evaluate("window.location.href"), timeout=2.0)
        except Exception:
            return False

        if any(ind in url.lower() for ind in login_url_indicators):
            return False

        try:
            has_pw = await asyncio.wait_for(
                tab.evaluate("!!document.querySelector('input[type=\"password\"]')"), timeout=2.0
            )
            if bool(has_pw):
                return False
        except Exception as e:
            debug_logger.log_warning("login_watcher", "_left_login_page", f"Password field check failed: {e}")

        return True


login_watcher = LoginWatcher()
