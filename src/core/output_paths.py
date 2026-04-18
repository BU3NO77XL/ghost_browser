"""Output path handling for local and Docker transports."""

import os
from pathlib import Path
from typing import Dict

from core.platform_utils import is_running_in_container

_DEFAULT_CONTAINER_WORKSPACE = "/workspace"


def get_client_workspace() -> Path:
    """Return the filesystem root where client-visible artifacts should be written."""
    if is_running_in_container():
        return Path(os.environ.get("GHOST_CLIENT_WORKSPACE", _DEFAULT_CONTAINER_WORKSPACE))
    return Path.cwd()


def resolve_output_path(output_path: str) -> Path:
    """Resolve an output path without leaking Docker artifacts into /app."""
    if not output_path:
        raise ValueError("output_path is required")

    raw_path = Path(str(output_path)).expanduser()
    if not is_running_in_container():
        return raw_path

    workspace = get_client_workspace()
    raw = str(output_path).replace("\\", "/")

    if raw.startswith(f"{workspace.as_posix()}/") or raw == workspace.as_posix():
        return Path(raw)

    if raw.startswith("/app/"):
        return workspace / raw.removeprefix("/app/")

    if raw.startswith("/data/output/"):
        return workspace / raw.removeprefix("/data/output/")

    if raw.startswith("/"):
        return workspace / raw.lstrip("/")

    return workspace / raw


def output_path_metadata(path: Path) -> Dict[str, str]:
    """Return client-facing path hints for a written artifact."""
    metadata = {"file_path": str(path.absolute())}
    if is_running_in_container():
        workspace = get_client_workspace()
        try:
            relative = path.absolute().relative_to(workspace.absolute())
        except ValueError:
            relative = Path(path.name)
        host_root = os.environ.get("GHOST_CLIENT_WORKSPACE_HOST", "ghost_browser_mcp_output")
        metadata["client_path_hint"] = str(Path(host_root) / relative)
        metadata["workspace_mount"] = str(workspace)
    return metadata
