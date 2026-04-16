"""Target domain handler for managing browser targets (pages, workers, iframes) via CDP."""

import asyncio
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.debug_logger import debug_logger


class TargetHandler:
    """Handles browser target management via CDP Target domain."""

    @staticmethod
    async def get_targets(tab: Tab) -> List[Dict[str, Any]]:
        debug_logger.log_info("TargetHandler", "get_targets", "Getting all targets")
        try:
            result = await tab.send(cdp.target.get_targets())
            targets = []
            for t in result:
                t_type = getattr(t, "type_", None) or getattr(t, "type", None)
                if t_type == "browser":
                    continue
                targets.append({
                    "target_id": str(getattr(t, "target_id", "")),
                    "type": t_type,
                    "title": getattr(t, "title", ""),
                    "url": getattr(t, "url", ""),
                    "attached": getattr(t, "attached", False),
                    "opener_id": str(getattr(t, "opener_id", "") or ""),
                })
            return targets
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("TargetHandler", "get_targets", e, {})
            raise

    @staticmethod
    async def get_target_info(tab: Tab, target_id: str) -> Dict[str, Any]:
        debug_logger.log_info(
            "TargetHandler", "get_target_info", f"Getting info for target {target_id}"
        )
        try:
            result = await tab.send(
                cdp.target.get_target_info(
                    target_id=cdp.target.TargetID(target_id)
                )
            )
            t = result
            t_type = getattr(t, "type_", None) or getattr(t, "type", None)
            return {
                "target_id": str(getattr(t, "target_id", "")),
                "type": t_type,
                "title": getattr(t, "title", ""),
                "url": getattr(t, "url", ""),
                "attached": getattr(t, "attached", False),
                "opener_id": str(getattr(t, "opener_id", "") or ""),
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
                "TargetHandler", "get_target_info", e, {"target_id": target_id}
            )
            raise

    @staticmethod
    async def create_target(
        tab: Tab,
        url: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        new_window: bool = False,
    ) -> Dict[str, str]:
        debug_logger.log_info(
            "TargetHandler", "create_target", f"Creating target with url={url}"
        )
        try:
            result = await tab.send(
                cdp.target.create_target(
                    url=url,
                    width=width,
                    height=height,
                    new_window=new_window,
                )
            )
            return {"target_id": str(result)}
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
                "TargetHandler", "create_target", e, {"url": url}
            )
            raise

    @staticmethod
    async def close_target(tab: Tab, target_id: str) -> Dict[str, bool]:
        debug_logger.log_info(
            "TargetHandler", "close_target", f"Closing target {target_id}"
        )
        try:
            result = await tab.send(
                cdp.target.close_target(
                    target_id=cdp.target.TargetID(target_id)
                )
            )
            return {"success": bool(result)}
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
                "TargetHandler", "close_target", e, {"target_id": target_id}
            )
            raise

    @staticmethod
    async def activate_target(tab: Tab, target_id: str) -> bool:
        debug_logger.log_info(
            "TargetHandler", "activate_target", f"Activating target {target_id}"
        )
        try:
            await tab.send(
                cdp.target.activate_target(
                    target_id=cdp.target.TargetID(target_id)
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
                "TargetHandler", "activate_target", e, {"target_id": target_id}
            )
            raise

    @staticmethod
    async def attach_to_target(
        tab: Tab, target_id: str, flatten: bool = True
    ) -> Dict[str, str]:
        debug_logger.log_info(
            "TargetHandler", "attach_to_target", f"Attaching to target {target_id}"
        )
        try:
            result = await tab.send(
                cdp.target.attach_to_target(
                    target_id=cdp.target.TargetID(target_id),
                    flatten=flatten,
                )
            )
            return {"session_id": str(result)}
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
                "TargetHandler", "attach_to_target", e, {"target_id": target_id}
            )
            raise

    @staticmethod
    async def detach_from_target(tab: Tab, session_id: str) -> bool:
        debug_logger.log_info(
            "TargetHandler", "detach_from_target", f"Detaching from session {session_id}"
        )
        try:
            await tab.send(
                cdp.target.detach_from_target(
                    session_id=cdp.target.SessionID(session_id)
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
                "TargetHandler", "detach_from_target", e, {"session_id": session_id}
            )
            raise
