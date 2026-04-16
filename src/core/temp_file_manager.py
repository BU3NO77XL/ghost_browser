"""
Centralized manager for temporary files generated during server operation.

Tracks every file written to disk (clones, screenshots, large responses) and
deletes them all on server shutdown. Also provides TTL-based cleanup so files
never accumulate even if the server crashes without a clean shutdown.

Files can optionally be associated with a browser instance_id.  When an
instance is closed its files are scheduled for deferred deletion:

  • Instance closed  → delete after INSTANCE_CLOSE_DELAY_MINUTES  (default 10 min)
  • Instance still open → delete after INSTANCE_IDLE_TTL_MINUTES   (default 50 min)
    (enforced by a background sweep that runs every minute)

This gives the caller enough time to read the files after the instance closes
while still preventing unbounded disk growth.
"""

import asyncio
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.debug_logger import debug_logger

# ---------------------------------------------------------------------------
# Tuneable constants
# ---------------------------------------------------------------------------

# Grace period after close_instance() before files are actually deleted (seconds)
INSTANCE_CLOSE_DELAY_SECONDS: int = 10 * 60  # 10 minutes

# Maximum age of a file that is still associated with a live instance (seconds)
INSTANCE_IDLE_TTL_SECONDS: int = 50 * 60  # 50 minutes

# How often the background sweep runs (seconds)
_SWEEP_INTERVAL_SECONDS: int = 60

# Files older than this are deleted on startup (crash recovery)
_DEFAULT_TTL_HOURS: float = 2.0

# Root of the project (two levels up from this file: src/core/ -> src/ -> project/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TempFileManager:
    def __init__(self):
        self._tracked: List[Path] = []
        # Directories to scan for orphaned files on startup
        self._managed_dirs: List[Path] = []
        # Per-instance file tracking: instance_id -> list of (Path, created_at_epoch)
        self._instance_files: Dict[str, List[Tuple[Path, float]]] = {}
        # Pending deferred deletions: instance_id -> scheduled_delete_at_epoch
        # Set when close_instance() is called; files are deleted once the epoch passes.
        self._pending_close: Dict[str, float] = {}
        # Background sweep task handle
        self._sweep_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # Directory registration
    # ------------------------------------------------------------------

    def register_dir(self, directory: Path):
        """Register a directory whose contents should be cleaned up on shutdown."""
        directory = Path(directory)
        if directory not in self._managed_dirs:
            self._managed_dirs.append(directory)
        # Ensure the directory exists immediately upon registration
        directory.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # File tracking
    # ------------------------------------------------------------------

    def track(self, path: Path, instance_id: Optional[str] = None):
        """
        Track a single file for deletion.

        If instance_id is provided the file is associated with that instance
        and will be deleted according to the deferred schedule.  It is also
        added to the global list so it gets cleaned up on shutdown regardless.
        """
        path = Path(path)
        self._tracked.append(path)
        if instance_id:
            self._instance_files.setdefault(instance_id, []).append((path, time.monotonic()))

    # ------------------------------------------------------------------
    # Instance lifecycle hooks
    # ------------------------------------------------------------------

    def schedule_instance_cleanup(self, instance_id: str):
        """
        Schedule deferred deletion of all files for *instance_id*.

        Called when the browser instance is closed.  Files will be deleted
        after INSTANCE_CLOSE_DELAY_SECONDS (default 10 min).
        """
        if instance_id not in self._instance_files:
            # Nothing tracked for this instance — nothing to do.
            return
        delete_at = time.monotonic() + INSTANCE_CLOSE_DELAY_SECONDS
        self._pending_close[instance_id] = delete_at
        debug_logger.log_info(
            "temp_file_manager",
            "schedule_instance_cleanup",
            f"Instance {instance_id} closed — files scheduled for deletion in "
            f"{INSTANCE_CLOSE_DELAY_SECONDS // 60} min",
        )

    # ------------------------------------------------------------------
    # Background sweep
    # ------------------------------------------------------------------

    def start_sweep(self):
        """
        Start the background asyncio task that enforces deferred deletions.
        Must be called from within a running event loop (e.g. at server startup).
        """
        if self._sweep_task is None or self._sweep_task.done():
            self._sweep_task = asyncio.create_task(self._sweep_loop())
            debug_logger.log_info(
                "temp_file_manager", "start_sweep", "Background sweep task started"
            )

    def stop_sweep(self):
        """Cancel the background sweep task (called at shutdown)."""
        if self._sweep_task and not self._sweep_task.done():
            self._sweep_task.cancel()
            self._sweep_task = None

    async def _sweep_loop(self):
        """Runs every _SWEEP_INTERVAL_SECONDS and enforces all TTL rules."""
        while True:
            try:
                await asyncio.sleep(_SWEEP_INTERVAL_SECONDS)
                self._sweep_once()
            except asyncio.CancelledError:
                break
            except Exception as e:
                debug_logger.log_error("temp_file_manager", "_sweep_loop", e)

    def _sweep_once(self):
        """
        Single sweep pass — called by the background task and also exposed
        for testing / manual invocation.
        """
        now = time.monotonic()
        deleted_total = 0

        # 1. Deferred close deletions: instances that were closed and whose
        #    grace period has now expired.
        expired_instances = [
            iid for iid, delete_at in self._pending_close.items() if now >= delete_at
        ]
        for iid in expired_instances:
            deleted_total += self._delete_instance_files(iid)
            del self._pending_close[iid]

        # 2. Idle TTL: files still associated with a live (not-yet-closed)
        #    instance but older than INSTANCE_IDLE_TTL_SECONDS.
        idle_expired = []
        for iid, file_list in self._instance_files.items():
            if iid in self._pending_close:
                # Already scheduled for close-based deletion — skip.
                continue
            still_alive = []
            for path, created_at in file_list:
                age = now - created_at
                if age >= INSTANCE_IDLE_TTL_SECONDS:
                    try:
                        if path.exists():
                            path.unlink()
                            deleted_total += 1
                    except Exception:
                        pass
                    try:
                        self._tracked.remove(path)
                    except ValueError:
                        pass
                else:
                    still_alive.append((path, created_at))
            self._instance_files[iid] = still_alive
            if not still_alive:
                idle_expired.append(iid)

        for iid in idle_expired:
            del self._instance_files[iid]

        if deleted_total:
            debug_logger.log_info(
                "temp_file_manager",
                "_sweep_once",
                f"Sweep deleted {deleted_total} temp files",
            )

    def _delete_instance_files(self, instance_id: str) -> int:
        """Delete all tracked files for *instance_id* and return count deleted."""
        file_list = self._instance_files.pop(instance_id, [])
        deleted = 0
        for path, _ in file_list:
            try:
                if path.exists():
                    path.unlink()
                    deleted += 1
            except Exception:
                pass
            try:
                self._tracked.remove(path)
            except ValueError:
                pass
        if deleted:
            debug_logger.log_info(
                "temp_file_manager",
                "_delete_instance_files",
                f"Deleted {deleted} temp files for instance {instance_id}",
            )
        return deleted

    # ------------------------------------------------------------------
    # Startup / shutdown
    # ------------------------------------------------------------------

    def cleanup_on_startup(self, ttl_hours: float = _DEFAULT_TTL_HOURS):
        """
        Delete files older than ttl_hours from all managed directories.
        Called at server startup to recover from previous crashes.
        """
        cutoff = time.time() - ttl_hours * 3600
        deleted = 0
        for directory in self._managed_dirs:
            if not directory.exists():
                continue
            for f in directory.iterdir():
                if not f.is_file():
                    continue
                try:
                    if f.stat().st_mtime < cutoff:
                        f.unlink()
                        deleted += 1
                except Exception:
                    pass
        if deleted:
            debug_logger.log_info(
                "temp_file_manager",
                "startup_cleanup",
                f"Deleted {deleted} orphaned temp files (older than {ttl_hours}h)",
            )

    def cleanup_on_shutdown(self):
        """Delete all tracked files, managed directories content, and __pycache__ trees."""
        self.stop_sweep()

        deleted_files = 0
        deleted_cache = 0

        # Delete individually tracked files
        for f in self._tracked:
            try:
                if f.exists():
                    f.unlink()
                    deleted_files += 1
            except Exception:
                pass
        self._tracked.clear()
        self._instance_files.clear()
        self._pending_close.clear()

        # Delete everything in managed directories
        for directory in self._managed_dirs:
            if not directory.exists():
                continue
            for f in directory.iterdir():
                if not f.is_file():
                    continue
                try:
                    f.unlink()
                    deleted_files += 1
                except Exception:
                    pass

        # Remove all __pycache__ directories under the project src/
        src_dir = _PROJECT_ROOT / "src"
        for cache_dir in src_dir.rglob("__pycache__"):
            try:
                shutil.rmtree(cache_dir, ignore_errors=True)
                deleted_cache += 1
            except Exception:
                pass

        parts = []
        if deleted_files:
            parts.append(f"{deleted_files} temp files")
        if deleted_cache:
            parts.append(f"{deleted_cache} __pycache__ dirs")
        if parts:
            debug_logger.log_info(
                "temp_file_manager",
                "shutdown_cleanup",
                f"Deleted {', '.join(parts)}",
            )


temp_file_manager = TempFileManager()
