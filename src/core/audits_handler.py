"""Audits domain handler for encoded response inspection and contrast checking via CDP."""

import asyncio
from typing import Any, Dict, Optional

from nodriver import Tab, cdp

from core.debug_logger import debug_logger

VALID_ENCODINGS = {"webp", "jpeg", "png"}


class AuditsHandler:
    """Handles audit operations via CDP Audits domain."""

    @staticmethod
    async def enable_audits(tab: Tab) -> bool:
        debug_logger.log_info("AuditsHandler", "enable_audits", "Enabling Audits domain")
        try:
            await tab.send(cdp.audits.enable())
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
            debug_logger.log_error("AuditsHandler", "enable_audits", e, {})
            raise

    @staticmethod
    async def disable_audits(tab: Tab) -> bool:
        debug_logger.log_info("AuditsHandler", "disable_audits", "Disabling Audits domain")
        try:
            await tab.send(cdp.audits.disable())
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
            debug_logger.log_error("AuditsHandler", "disable_audits", e, {})
            raise

    @staticmethod
    async def get_encoded_response(
        tab: Tab,
        request_id: str,
        encoding: str,
        quality: Optional[int] = None,
    ) -> Dict[str, Any]:
        debug_logger.log_info(
            "AuditsHandler",
            "get_encoded_response",
            f"Getting encoded response for request {request_id} as {encoding}",
        )
        if encoding not in VALID_ENCODINGS:
            raise ValueError(
                f"Invalid encoding '{encoding}'. Must be one of: {', '.join(sorted(VALID_ENCODINGS))}"
            )
        try:
            result = await tab.send(
                cdp.audits.get_encoded_response(
                    request_id=cdp.network.RequestId(request_id),
                    encoding=encoding,  # Pass string directly instead of enum
                    quality=quality,
                )
            )
            return {
                "body": result.body if result.body is not None else "",
                "original_size": result.original_size,
                "encoded_size": result.encoded_size,
            }
        except ValueError:
            raise
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
                "AuditsHandler",
                "get_encoded_response",
                e,
                {"request_id": request_id, "encoding": encoding},
            )
            raise

    @staticmethod
    async def check_contrast(tab: Tab, report_aaa: bool = False) -> bool:
        debug_logger.log_info(
            "AuditsHandler",
            "check_contrast",
            f"Checking contrast (report_aaa={report_aaa})",
        )
        try:
            await tab.send(cdp.audits.check_contrast(report_aaa=report_aaa))
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
            debug_logger.log_error("AuditsHandler", "check_contrast", e, {})
            raise
