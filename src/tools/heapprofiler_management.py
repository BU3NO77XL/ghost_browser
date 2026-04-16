"""HeapProfiler management MCP tools for memory profiling and heap analysis.

WARNING: Heap snapshots and sampling can consume significant memory and CPU.
Use with caution on production pages or pages with large heaps.
"""

from typing import Any, Dict, Optional

from core.heapprofiler_handler import HeapProfilerHandler
from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("heapprofiler-management")
    async def take_heap_snapshot(instance_id: str) -> Dict[str, Any]:
        """
        Take a heap snapshot of the current JavaScript heap.

        WARNING: Heap snapshots can be very large (tens of MB). The response
        contains a preview and metadata only. Use browser DevTools for full
        heap analysis.

        Useful for identifying memory leaks and large object allocations.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Dict[str, Any]: Snapshot metadata with preview, total_size_chars,
                            truncated flag, and analysis notes.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await HeapProfilerHandler.take_heap_snapshot(tab)

    @section_tool("heapprofiler-management")
    async def start_heap_sampling(instance_id: str, sampling_interval: int = 32768) -> bool:
        """
        Start heap sampling profiler (low-overhead memory profiling).

        Heap sampling is much less intrusive than full heap snapshots.
        It samples allocations to estimate memory usage patterns without
        pausing JavaScript execution.

        Args:
            instance_id (str): Browser instance ID.
            sampling_interval (int): Average sample interval in bytes (default 32768).
                                     Lower values = more accurate but more overhead.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await HeapProfilerHandler.start_sampling(tab, sampling_interval)

    @section_tool("heapprofiler-management")
    async def stop_heap_sampling(instance_id: str) -> Dict[str, Any]:
        """
        Stop heap sampling and return the sampling profile.

        Returns a call tree showing which functions allocated the most memory.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Dict[str, Any]: Sampling profile with head node (call tree) and samples.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await HeapProfilerHandler.stop_sampling(tab)

    @section_tool("heapprofiler-management")
    async def start_tracking_heap_objects(
        instance_id: str, track_allocations: bool = False
    ) -> bool:
        """
        Start tracking heap object allocations over time.

        Useful for detecting memory leaks by observing which objects are
        created and not garbage collected.

        Args:
            instance_id (str): Browser instance ID.
            track_allocations (bool): Whether to track individual allocations
                                      (more detailed but higher overhead).

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await HeapProfilerHandler.start_tracking_heap_objects(tab, track_allocations)

    @section_tool("heapprofiler-management")
    async def stop_tracking_heap_objects(instance_id: str) -> bool:
        """
        Stop tracking heap object allocations.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await HeapProfilerHandler.stop_tracking_heap_objects(tab)

    @section_tool("heapprofiler-management")
    async def collect_garbage(instance_id: str) -> bool:
        """
        Force a JavaScript garbage collection cycle.

        Useful before taking heap snapshots to get a cleaner view of live
        objects (removes unreachable objects that haven't been collected yet).

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await HeapProfilerHandler.collect_garbage(tab)

    @section_tool("heapprofiler-management")
    async def get_object_by_heap_id(
        instance_id: str, heap_snapshot_object_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a JavaScript object by its heap snapshot object ID.

        Allows inspecting specific objects found in a heap snapshot.

        Args:
            instance_id (str): Browser instance ID.
            heap_snapshot_object_id (str): The heap object ID from a snapshot.

        Returns:
            Optional[Dict[str, Any]]: Object info with type, value, and description.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await HeapProfilerHandler.get_object_by_heap_id(tab, heap_snapshot_object_id)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
