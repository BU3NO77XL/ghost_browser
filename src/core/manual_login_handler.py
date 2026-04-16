"""Handler for manual login scenarios.

Flow:
  1. navigate() detects login page → register_pending_login() + watcher starts
  2. Watcher polls every 1.5s — detects when user leaves login page, sets flag
  3. User tells AI they logged in → AI calls confirm_manual_login
  4. confirm_manual_login clears pending state, returns success + current URL
  5. AI continues automation normally. Cookies are handled separately via CDP tools.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

from nodriver import Tab

from core.debug_logger import debug_logger

LOGIN_URL_INDICATORS = (
    "login",
    "signin",
    "sign-in",
    "log-in",
    "logon",
    "log_in",
    "auth",
    "authenticate",
    "sso",
    "oauth",
    "accounts.google.com",
    "login.microsoftonline.com",
    "login.live.com",
    "appleid.apple.com",
)


class ManualLoginHandler:
    def __init__(self):
        self._pending: Dict[str, dict] = {}  # instance_id → {url, registered_at}
        self._lock = asyncio.Lock()  # Protect concurrent access

    # ------------------------------------------------------------------
    # Pending state
    # ------------------------------------------------------------------

    async def register_pending_login(self, instance_id: str, tab: Tab, url: str) -> None:
        async with self._lock:
            self._pending[instance_id] = {
                "url": url,
                "registered_at": datetime.now().isoformat(),
            }
        debug_logger.log_info(
            "manual_login_handler",
            "register_pending_login",
            f"Pending login for {instance_id}. URL: {url}",
        )
        from core.login_watcher import login_watcher

        await login_watcher.start_watching(instance_id, tab)

    async def is_pending_login(self, instance_id: str) -> bool:
        async with self._lock:
            return instance_id in self._pending

    async def get_pending_info(self, instance_id: str) -> Optional[dict]:
        async with self._lock:
            info = self._pending.get(instance_id)
            if not info:
                return None
            return {"instance_id": instance_id, **info, "status": "waiting_for_user"}

    async def _clear_pending(self, instance_id: str) -> None:
        async with self._lock:
            self._pending.pop(instance_id, None)

    # ------------------------------------------------------------------
    # Confirm login — just clears state and returns current URL
    # ------------------------------------------------------------------

    async def confirm_login(
        self, instance_id: str, tab: Tab, skip_login_check: bool = False
    ) -> Dict[str, Any]:
        """
        Confirm login: clears pending state and returns the current URL.
        Does NOT save cookies — use CDP tools for that separately.

        skip_login_check=False → verify user is no longer on login page first.
        skip_login_check=True  → skip check (watcher already confirmed URL changed).
        """
        try:
            if not skip_login_check:
                still_on_login = await self.detect_login_page(tab)
                if still_on_login:
                    try:
                        current_url = await asyncio.wait_for(
                            tab.evaluate("window.location.href"), timeout=3.0
                        )
                    except Exception:
                        current_url = "unknown"
                    debug_logger.log_warning(
                        "manual_login_handler",
                        "confirm_login",
                        f"{instance_id} still on login page: {current_url}",
                    )
                    return {
                        "success": False,
                        "message": "Ainda na página de login. Conclua o login e tente novamente.",
                        "current_url": current_url,
                        "is_login_page": True,
                        "instance_id": instance_id,
                    }

            try:
                current_url = await asyncio.wait_for(
                    tab.evaluate("window.location.href"), timeout=3.0
                )
            except Exception:
                current_url = "unknown"

            await self._clear_pending(instance_id)

            debug_logger.log_info(
                "manual_login_handler",
                "confirm_login",
                f"Login confirmed for {instance_id}. URL: {current_url}",
            )
            return {
                "success": True,
                "message": "Login confirmado. Instância pronta para uso.",
                "current_url": current_url,
                "instance_id": instance_id,
            }

        except asyncio.TimeoutError:
            debug_logger.log_error(
                "manual_login_handler", "confirm_login", f"Timeout for {instance_id}"
            )
            return {
                "success": False,
                "message": "Timeout ao confirmar login.",
                "instance_id": instance_id,
                "error": "timeout",
            }
        except Exception as e:
            debug_logger.log_error("manual_login_handler", "confirm_login", e)
            return {
                "success": False,
                "message": f"Erro: {e}",
                "instance_id": instance_id,
                "error": type(e).__name__,
            }

    # ------------------------------------------------------------------
    # Login page detection — used by navigate() and confirm_login()
    # ------------------------------------------------------------------

    async def detect_login_page(self, tab: Tab) -> bool:
        """Returns True if current page looks like a login page."""
        try:
            url = await asyncio.wait_for(tab.evaluate("window.location.href"), timeout=3.0)

            if any(ind in url.lower() for ind in LOGIN_URL_INDICATORS):
                debug_logger.log_info(
                    "manual_login_handler", "detect_login_page", f"Login page by URL: {url}"
                )
                return True

            has_form = await asyncio.wait_for(
                tab.evaluate("""
                (() => {
                    if (document.querySelector('input[type="password"]')) return true;
                    for (const btn of document.querySelectorAll('button, input[type="submit"]')) {
                        const t = (btn.textContent || btn.value || '').toLowerCase();
                        if (t.includes('login') || t.includes('entrar') || t.includes('signin')) return true;
                    }
                    for (const f of document.querySelectorAll('form')) {
                        const id = (f.id || '').toLowerCase();
                        const cls = (f.className || '').toLowerCase();
                        if (id.includes('login') || cls.includes('login')) return true;
                    }
                    return false;
                })()
            """),
                timeout=3.0,
            )

            if bool(has_form):
                debug_logger.log_info(
                    "manual_login_handler", "detect_login_page", "Login page by DOM"
                )
                return True

            return False

        except asyncio.TimeoutError:
            debug_logger.log_error(
                "manual_login_handler", "detect_login_page", "Timeout — assuming not login page"
            )
            return False
        except Exception as e:
            debug_logger.log_error(
                "manual_login_handler", "detect_login_page", f"{type(e).__name__}: {e}"
            )
            return False


manual_login_handler = ManualLoginHandler()
