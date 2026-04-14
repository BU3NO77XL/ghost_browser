import json
import os
import tempfile
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

class InMemoryStorage:
    """Thread-safe storage for browser instance data with disk persistence."""

    def __init__(self, storage_file: Optional[str] = None):
        """
        Initialize storage and load persisted state from disk.

        self: InMemoryStorage - The storage instance.
        """
        self._lock = threading.RLock()
        self._data: Dict[str, Any] = {"instances": {}}
        if storage_file:
            self._storage_file = Path(storage_file).expanduser()
        else:
            env_path = os.environ.get("STEALTH_BROWSER_STORAGE_FILE", "").strip()
            self._storage_file = (
                Path(env_path).expanduser()
                if env_path
                else Path(__file__).resolve().parent / ".storage" / "instances.json"
            )
        self._load_from_disk()

    def _load_from_disk(self):
        """Load persisted data from disk, discarding stale instances from previous runs."""
        with self._lock:
            try:
                if not self._storage_file.exists():
                    return
                loaded = json.loads(self._storage_file.read_text(encoding="utf-8"))
                if not isinstance(loaded, dict):
                    return
                instances = loaded.get("instances")
                if not isinstance(instances, dict):
                    loaded["instances"] = {}
                # Discard all stored instances — they belong to a previous server run
                # and their browser processes no longer exist. Starting fresh prevents
                # ghost instances from polluting list_instances().
                loaded["instances"] = {}
                self._data = loaded
                self._persist_to_disk()
            except Exception:
                self._data = {"instances": {}}

    def _persist_to_disk(self):
        """Persist current state to disk atomically."""
        with self._lock:
            try:
                self._storage_file.parent.mkdir(parents=True, exist_ok=True)
                serialized = json.dumps(self._data, ensure_ascii=False, indent=2)
                with tempfile.NamedTemporaryFile(
                    "w",
                    encoding="utf-8",
                    delete=False,
                    dir=str(self._storage_file.parent),
                    prefix=".tmp_stealth_storage_",
                    suffix=".json",
                ) as tmp:
                    tmp.write(serialized)
                    tmp_path = Path(tmp.name)
                tmp_path.replace(self._storage_file)
            except Exception:
                # Keep in-memory behavior even if disk persistence fails.
                return

    def store_instance(self, instance_id: str, data: Dict[str, Any]):
        """
        Store browser instance data.

        instance_id: str - The unique identifier for the browser instance.
        data: Dict[str, Any] - The data associated with the browser instance.
        """
        with self._lock:
            if 'instances' not in self._data:
                self._data['instances'] = {}
            serializable_data = {
                'instance_id': instance_id,
                'state': data.get('state', 'unknown'),
                'created_at': data.get('created_at', ''),
                'current_url': data.get('current_url', ''),
                'title': data.get('title', ''),
                'tabs': []
            }
            self._data['instances'][instance_id] = serializable_data
            self._persist_to_disk()

    def remove_instance(self, instance_id: str):
        """
        Remove browser instance from storage.

        instance_id: str - The unique identifier for the browser instance to remove.
        """
        with self._lock:
            if 'instances' in self._data and instance_id in self._data['instances']:
                del self._data['instances'][instance_id]
                self._persist_to_disk()

    def get_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get browser instance data.

        instance_id: str - The unique identifier for the browser instance.
        Returns: Optional[Dict[str, Any]] - The data for the browser instance, or None if not found.
        """
        with self._lock:
            instance = self._data.get('instances', {}).get(instance_id)
            return deepcopy(instance) if instance is not None else None

    def list_instances(self) -> Dict[str, Any]:
        """
        List all stored instances.

        Returns: Dict[str, Any] - A copy of all stored instances.
        """
        with self._lock:
            return deepcopy(self._data)

    def clear_all(self):
        """
        Clear all stored data.

        self: InMemoryStorage - The storage instance.
        """
        with self._lock:
            self._data = {"instances": {}}
            self._persist_to_disk()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get data by key.

        key: str - The key to retrieve from storage.
        default: Any - The default value to return if key is not found.
        Returns: Any - The value associated with the key, or default if not found.
        """
        with self._lock:
            value = self._data.get(key, default)
            return deepcopy(value)

    def set(self, key: str, value: Any):
        """
        Set data by key.

        key: str - The key to set in storage.
        value: Any - The value to associate with the key.
        """
        with self._lock:
            self._data[key] = value
            self._persist_to_disk()

persistent_storage = InMemoryStorage()
