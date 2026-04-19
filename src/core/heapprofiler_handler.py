"""HeapProfiler domain handler for memory profiling and heap snapshots via CDP."""

import asyncio
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.cdp_result import remote_object_to_dict
from core.debug_logger import debug_logger

# Maximum snapshot size to return (heap snapshots can be very large)
MAX_SNAPSHOT_CHARS = 500_000


class HeapProfilerHandler:
    """Handles heap profiling and memory analysis via CDP HeapProfiler domain."""

    @staticmethod
    async def enable_heap_profiler(tab: Tab) -> bool:
        """
        Enable the HeapProfiler domain for the given tab.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        try:
            await tab.send(cdp.heap_profiler.enable())
            return True
        except Exception as e:
            error_msg = str(e).lower()
            if "already enabled" in error_msg:
                return True
            raise

    @staticmethod
    async def take_heap_snapshot(tab: Tab, report_progress: bool = False) -> Dict[str, Any]:
        """
        Take a heap snapshot of the current JavaScript heap.

        WARNING: Heap snapshots can be very large (tens of MB). The response
        is truncated to MAX_SNAPSHOT_CHARS characters to prevent memory issues.
        Use this for identifying memory leaks and large object allocations.

        Args:
            tab (Tab): The browser tab object.
            report_progress (bool): Whether to report snapshot progress.

        Returns:
            Dict[str, Any]: Snapshot metadata with truncated flag and size info.
        """
        debug_logger.log_info("HeapProfilerHandler", "take_heap_snapshot", "Taking heap snapshot")
        try:
            await HeapProfilerHandler.enable_heap_profiler(tab)
            # Collect snapshot chunks via CDP events
            snapshot_chunks: List[str] = []

            async def collect_chunk(event):
                if hasattr(event, "chunk"):
                    snapshot_chunks.append(event.chunk)

            # Take snapshot - chunks are delivered via addHeapSnapshotChunk events
            await tab.send(cdp.heap_profiler.take_heap_snapshot(report_progress=report_progress))
            # Give a moment for chunks to arrive
            await asyncio.sleep(0.5)

            full_snapshot = "".join(snapshot_chunks)
            total_size = len(full_snapshot)
            truncated = total_size > MAX_SNAPSHOT_CHARS
            if truncated:
                full_snapshot = full_snapshot[:MAX_SNAPSHOT_CHARS]

            return {
                "snapshot_preview": full_snapshot[:2000] if full_snapshot else "",
                "total_size_chars": total_size,
                "truncated": truncated,
                "chunks_received": len(snapshot_chunks),
                "note": (
                    (
                        "Heap snapshot data is very large. Use browser DevTools for "
                        "full analysis. This response contains a preview only."
                    )
                    if truncated
                    else "Heap snapshot captured."
                ),
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
            debug_logger.log_error("HeapProfilerHandler", "take_heap_snapshot", e, {})
            raise

    @staticmethod
    async def start_sampling(tab: Tab, sampling_interval: int = 32768) -> bool:
        """
        Start heap sampling profiler.

        Heap sampling is a low-overhead alternative to full heap snapshots.
        It samples allocations to estimate memory usage patterns.

        Args:
            tab (Tab): The browser tab object.
            sampling_interval (int): Average sample interval in bytes (default 32768).

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "HeapProfilerHandler",
            "start_sampling",
            f"Starting heap sampling with interval: {sampling_interval}",
        )
        try:
            await HeapProfilerHandler.enable_heap_profiler(tab)
            await tab.send(cdp.heap_profiler.start_sampling(sampling_interval=sampling_interval))
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
            debug_logger.log_error("HeapProfilerHandler", "start_sampling", e, {})
            raise

    @staticmethod
    async def stop_sampling(tab: Tab) -> Dict[str, Any]:
        """
        Stop heap sampling and return the sampling profile.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            Dict[str, Any]: Sampling profile with head node and total size.
        """
        debug_logger.log_info("HeapProfilerHandler", "stop_sampling", "Stopping heap sampling")
        try:
            result = await tab.send(cdp.heap_profiler.stop_sampling())
            profile = getattr(result, "profile", result)
            if not profile:
                return {"head": None, "samples": []}

            def serialize_node(node, depth=0):
                if depth > 10:
                    return {"name": "...", "self_size": 0, "children": []}
                children = []
                if node.children:
                    for child in node.children[:20]:  # limit children
                        children.append(serialize_node(child, depth + 1))
                return {
                    "name": node.call_frame.function_name if node.call_frame else "",
                    "url": node.call_frame.url if node.call_frame else "",
                    "self_size": node.self_size,
                    "children": children,
                }

            head = serialize_node(profile.head) if profile.head else None
            return {
                "head": head,
                "samples": [
                    {"node_id": s.node_id, "ordinal": s.ordinal, "size": s.size}
                    for s in (profile.samples or [])[:1000]
                ],
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
            debug_logger.log_error("HeapProfilerHandler", "stop_sampling", e, {})
            raise

    @staticmethod
    async def start_tracking_heap_objects(tab: Tab, track_allocations: bool = False) -> bool:
        """
        Start tracking heap object allocations over time.

        Args:
            tab (Tab): The browser tab object.
            track_allocations (bool): Whether to track individual allocations.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "HeapProfilerHandler",
            "start_tracking_heap_objects",
            f"Starting heap object tracking (track_allocations={track_allocations})",
        )
        try:
            await HeapProfilerHandler.enable_heap_profiler(tab)
            await tab.send(
                cdp.heap_profiler.start_tracking_heap_objects(track_allocations=track_allocations)
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
            debug_logger.log_error("HeapProfilerHandler", "start_tracking_heap_objects", e, {})
            raise

    @staticmethod
    async def stop_tracking_heap_objects(tab: Tab) -> bool:
        """
        Stop tracking heap object allocations.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "HeapProfilerHandler",
            "stop_tracking_heap_objects",
            "Stopping heap object tracking",
        )
        try:
            await tab.send(cdp.heap_profiler.stop_tracking_heap_objects(report_progress=False))
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
            debug_logger.log_error("HeapProfilerHandler", "stop_tracking_heap_objects", e, {})
            raise

    @staticmethod
    async def collect_garbage(tab: Tab) -> bool:
        """
        Force a garbage collection cycle.

        Useful before taking heap snapshots to get a cleaner view of live objects.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "HeapProfilerHandler", "collect_garbage", "Forcing garbage collection"
        )
        try:
            await HeapProfilerHandler.enable_heap_profiler(tab)
            await tab.send(cdp.heap_profiler.collect_garbage())
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
            debug_logger.log_error("HeapProfilerHandler", "collect_garbage", e, {})
            raise

    @staticmethod
    async def get_object_by_heap_id(
        tab: Tab, heap_snapshot_object_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a JavaScript object by its heap snapshot object ID.

        Args:
            tab (Tab): The browser tab object.
            heap_snapshot_object_id (str): The heap object ID from a snapshot.

        Returns:
            Optional[Dict[str, Any]]: Object info with type, value, and description.
        """
        debug_logger.log_info(
            "HeapProfilerHandler",
            "get_object_by_heap_id",
            f"Getting object by heap ID: {heap_snapshot_object_id}",
        )
        try:
            result = await tab.send(
                cdp.heap_profiler.get_object_by_heap_object_id(
                    object_id=cdp.heap_profiler.HeapSnapshotObjectId(heap_snapshot_object_id)
                )
            )
            obj = getattr(result, "result", result)
            if not obj:
                return None
            return remote_object_to_dict(obj)
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
                "HeapProfilerHandler",
                "get_object_by_heap_id",
                e,
                {"heap_snapshot_object_id": heap_snapshot_object_id},
            )
            raise
