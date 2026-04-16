"""Profiler domain handler for CPU profiling and code coverage via CDP."""

import asyncio
import json
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.debug_logger import debug_logger

# Maximum profile data size to return (truncate large profiles)
MAX_PROFILE_NODES = 5000


class ProfilerHandler:
    """Handles CPU profiling and code coverage via CDP Profiler domain."""

    @staticmethod
    async def enable_profiler(tab: Tab) -> bool:
        """
        Enable the Profiler domain for the given tab.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        try:
            await tab.send(cdp.profiler.enable())
            return True
        except Exception as e:
            error_msg = str(e).lower()
            if "already enabled" in error_msg:
                return True
            raise

    @staticmethod
    async def start_profiling(tab: Tab) -> bool:
        """
        Start CPU profiling.

        Call stop_profiling() to end the session and retrieve the profile data.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if profiling started successfully.
        """
        debug_logger.log_info("ProfilerHandler", "start_profiling", "Starting CPU profiling")
        try:
            await ProfilerHandler.enable_profiler(tab)
            await tab.send(cdp.profiler.start())
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
            debug_logger.log_error("ProfilerHandler", "start_profiling", e, {})
            raise

    @staticmethod
    async def stop_profiling(tab: Tab) -> Dict[str, Any]:
        """
        Stop CPU profiling and return the profile data.

        Profile data can be large. Response is truncated to MAX_PROFILE_NODES
        nodes to prevent memory issues.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            Dict[str, Any]: CPU profile with nodes, start_time, end_time, and samples.
        """
        debug_logger.log_info("ProfilerHandler", "stop_profiling", "Stopping CPU profiling")
        try:
            result = await tab.send(cdp.profiler.stop())
            if not result or not result.profile:
                return {"nodes": [], "start_time": 0, "end_time": 0, "samples": []}
            profile = result.profile
            nodes = []
            if profile.nodes:
                for node in profile.nodes[:MAX_PROFILE_NODES]:
                    call_frame = {}
                    if node.call_frame:
                        call_frame = {
                            "function_name": node.call_frame.function_name,
                            "script_id": str(node.call_frame.script_id),
                            "url": node.call_frame.url,
                            "line_number": node.call_frame.line_number,
                            "column_number": node.call_frame.column_number,
                        }
                    nodes.append(
                        {
                            "id": node.id_,
                            "call_frame": call_frame,
                            "hit_count": node.hit_count,
                            "children": node.children or [],
                        }
                    )
            truncated = len(profile.nodes or []) > MAX_PROFILE_NODES
            return {
                "nodes": nodes,
                "start_time": profile.start_time,
                "end_time": profile.end_time,
                "samples": (profile.samples or [])[:10000],
                "time_deltas": (profile.time_deltas or [])[:10000],
                "truncated": truncated,
                "total_nodes": len(profile.nodes or []),
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
            debug_logger.log_error("ProfilerHandler", "stop_profiling", e, {})
            raise

    @staticmethod
    async def start_precise_coverage(
        tab: Tab, call_count: bool = False, detailed: bool = False
    ) -> bool:
        """
        Start collecting precise code coverage data.

        Args:
            tab (Tab): The browser tab object.
            call_count (bool): Whether to collect call counts (more detailed, more overhead).
            detailed (bool): Whether to collect block-level coverage (vs function-level).

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "ProfilerHandler",
            "start_precise_coverage",
            f"Starting precise coverage: call_count={call_count}, detailed={detailed}",
        )
        try:
            await ProfilerHandler.enable_profiler(tab)
            await tab.send(
                cdp.profiler.start_precise_coverage(call_count=call_count, detailed=detailed)
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
            debug_logger.log_error("ProfilerHandler", "start_precise_coverage", e, {})
            raise

    @staticmethod
    async def stop_precise_coverage(tab: Tab) -> bool:
        """
        Stop collecting precise code coverage data.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "ProfilerHandler", "stop_precise_coverage", "Stopping precise coverage"
        )
        try:
            await tab.send(cdp.profiler.stop_precise_coverage())
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
            debug_logger.log_error("ProfilerHandler", "stop_precise_coverage", e, {})
            raise

    @staticmethod
    async def take_precise_coverage(tab: Tab, url_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Take a snapshot of the current precise code coverage data.

        Args:
            tab (Tab): The browser tab object.
            url_filter (Optional[str]): Optional URL substring to filter results.

        Returns:
            Dict[str, Any]: Coverage data with script entries and covered ranges.
        """
        debug_logger.log_info(
            "ProfilerHandler",
            "take_precise_coverage",
            f"Taking precise coverage snapshot (filter: {url_filter})",
        )
        try:
            result = await tab.send(cdp.profiler.take_precise_coverage())
            scripts = []
            if result and result.result:
                for script in result.result:
                    url = script.url or ""
                    if url_filter and url_filter not in url:
                        continue
                    functions = []
                    for func in script.functions or []:
                        ranges = []
                        for r in func.ranges or []:
                            ranges.append(
                                {
                                    "start_offset": r.start_offset,
                                    "end_offset": r.end_offset,
                                    "count": r.count,
                                }
                            )
                        functions.append(
                            {
                                "function_name": func.function_name,
                                "is_block_coverage": func.is_block_coverage,
                                "ranges": ranges,
                            }
                        )
                    scripts.append(
                        {
                            "script_id": str(script.script_id),
                            "url": url,
                            "functions": functions,
                        }
                    )
            return {
                "scripts": scripts,
                "timestamp": result.timestamp if result else 0,
                "total_scripts": len(scripts),
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
            debug_logger.log_error("ProfilerHandler", "take_precise_coverage", e, {})
            raise
