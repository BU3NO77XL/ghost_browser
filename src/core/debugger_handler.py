"""Debugger domain handler for JavaScript debugging via CDP."""

import asyncio
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.cdp_result import exception_details_to_dict, remote_object_to_dict, runtime_parts, runtime_value
from core.debug_logger import debug_logger


class DebuggerHandler:
    """Handles JavaScript debugging operations via CDP Debugger domain."""

    # Breakpoint state per handler instance (class-level for simplicity)
    _breakpoints: Dict[str, str] = {}  # breakpoint_id -> location description

    @staticmethod
    async def enable_debugger(tab: Tab) -> str:
        """
        Enable the Debugger domain for the given tab.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            str: The debugger ID (unique identifier for this debugger session).
        """
        try:
            result = await tab.send(cdp.debugger.enable())
            return str(getattr(result, "debugger_id", result)) if result else ""
        except Exception as e:
            error_msg = str(e).lower()
            if "already enabled" in error_msg:
                return ""
            raise

    @staticmethod
    async def disable_debugger(tab: Tab) -> bool:
        """
        Disable the Debugger domain for the given tab.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        try:
            await tab.send(cdp.debugger.disable())
            return True
        except Exception as e:
            error_msg = str(e).lower()
            if "not enabled" in error_msg:
                return True
            raise

    @staticmethod
    async def set_breakpoint(
        tab: Tab,
        url: str,
        line_number: int,
        column_number: int = 0,
        condition: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Set a breakpoint at a specific URL and line number.

        Args:
            tab (Tab): The browser tab object.
            url (str): The URL or URL pattern of the script (supports regex).
            line_number (int): The line number (0-indexed).
            column_number (int): The column number (0-indexed, default 0).
            condition (Optional[str]): Optional JavaScript condition expression.

        Returns:
            Dict[str, Any]: Breakpoint info with breakpoint_id and resolved locations.
        """
        debug_logger.log_info(
            "DebuggerHandler",
            "set_breakpoint",
            f"Setting breakpoint at {url}:{line_number}:{column_number}",
        )
        try:
            await DebuggerHandler.enable_debugger(tab)
            result = await tab.send(
                cdp.debugger.set_breakpoint_by_url(
                    line_number=line_number,
                    url=url,
                    column_number=column_number,
                    condition=condition,
                )
            )
            if isinstance(result, (tuple, list)):
                raw_breakpoint_id = result[0] if len(result) > 0 else ""
                raw_locations = result[1] if len(result) > 1 else []
            else:
                raw_breakpoint_id = getattr(result, "breakpoint_id", "")
                raw_locations = getattr(result, "locations", [])
            breakpoint_id = str(raw_breakpoint_id)
            locations = []
            if raw_locations:
                for loc in raw_locations:
                    locations.append(
                        {
                            "script_id": str(loc.script_id),
                            "line_number": loc.line_number,
                            "column_number": loc.column_number,
                        }
                    )
            DebuggerHandler._breakpoints[breakpoint_id] = f"{url}:{line_number}"
            return {
                "breakpoint_id": breakpoint_id,
                "locations": locations,
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
                "DebuggerHandler",
                "set_breakpoint",
                e,
                {"url": url, "line_number": line_number},
            )
            raise

    @staticmethod
    async def remove_breakpoint(tab: Tab, breakpoint_id: str) -> bool:
        """
        Remove a breakpoint by its ID.

        Args:
            tab (Tab): The browser tab object.
            breakpoint_id (str): The breakpoint ID to remove.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "DebuggerHandler",
            "remove_breakpoint",
            f"Removing breakpoint: {breakpoint_id}",
        )
        try:
            await tab.send(
                cdp.debugger.remove_breakpoint(
                    breakpoint_id=cdp.debugger.BreakpointId(breakpoint_id)
                )
            )
            DebuggerHandler._breakpoints.pop(breakpoint_id, None)
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
                "DebuggerHandler",
                "remove_breakpoint",
                e,
                {"breakpoint_id": breakpoint_id},
            )
            raise

    @staticmethod
    async def resume_execution(tab: Tab) -> bool:
        """
        Resume JavaScript execution after a breakpoint pause.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info("DebuggerHandler", "resume_execution", "Resuming execution")
        try:
            await tab.send(cdp.debugger.resume())
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
            debug_logger.log_error("DebuggerHandler", "resume_execution", e, {})
            raise

    @staticmethod
    async def step_over(tab: Tab) -> bool:
        """
        Step over the current statement (execute current line, stop at next).

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info("DebuggerHandler", "step_over", "Stepping over")
        try:
            await tab.send(cdp.debugger.step_over())
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
            debug_logger.log_error("DebuggerHandler", "step_over", e, {})
            raise

    @staticmethod
    async def step_into(tab: Tab) -> bool:
        """
        Step into the current function call.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info("DebuggerHandler", "step_into", "Stepping into")
        try:
            await tab.send(cdp.debugger.step_into())
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
            debug_logger.log_error("DebuggerHandler", "step_into", e, {})
            raise

    @staticmethod
    async def get_call_stack(tab: Tab) -> List[Dict[str, Any]]:
        """
        Get the current JavaScript call stack (only available when paused).

        Args:
            tab (Tab): The browser tab object.

        Returns:
            List[Dict[str, Any]]: List of call frames with function name, URL, and line.
        """
        debug_logger.log_info("DebuggerHandler", "get_call_stack", "Getting call stack")
        try:
            # Use Runtime.evaluate to get stack trace info
            result = await tab.send(
                cdp.runtime.evaluate(
                    expression="new Error().stack",
                    return_by_value=True,
                )
            )
            stack_str = ""
            value = runtime_value(result)
            if value:
                stack_str = value
            frames = []
            for line in stack_str.split("\n")[1:]:  # skip first "Error" line
                line = line.strip()
                if line.startswith("at "):
                    frames.append({"frame": line[3:]})
            return frames
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("DebuggerHandler", "get_call_stack", e, {})
            raise

    @staticmethod
    async def evaluate_on_call_frame(
        tab: Tab, call_frame_id: str, expression: str
    ) -> Dict[str, Any]:
        """
        Evaluate a JavaScript expression on a specific call frame (when paused).

        Args:
            tab (Tab): The browser tab object.
            call_frame_id (str): The call frame ID (from CDP Debugger.paused event).
            expression (str): The JavaScript expression to evaluate.

        Returns:
            Dict[str, Any]: Evaluation result with type, value, and any exception info.
        """
        debug_logger.log_info(
            "DebuggerHandler",
            "evaluate_on_call_frame",
            f"Evaluating on call frame {call_frame_id}: {expression[:80]}",
        )
        try:
            result = await tab.send(
                cdp.debugger.evaluate_on_call_frame(
                    call_frame_id=cdp.debugger.CallFrameId(call_frame_id),
                    expression=expression,
                    return_by_value=True,
                )
            )
            remote_object, exception = runtime_parts(result)
            value = remote_object_to_dict(remote_object) if remote_object else None
            exception_details = exception_details_to_dict(exception) if exception else None
            return {"result": value, "exception_details": exception_details}
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
                "DebuggerHandler",
                "evaluate_on_call_frame",
                e,
                {"call_frame_id": call_frame_id},
            )
            raise
