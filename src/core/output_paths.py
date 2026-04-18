"""Output path handling for local and Docker transports."""

import os
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Dict, Iterable, Optional
from urllib.parse import unquote, urlparse

from core.platform_utils import is_running_in_container

_DEFAULT_CONTAINER_WORKSPACE = "/workspace"
_DEFAULT_HOST_ROOT_MOUNT = "/host_root"


def file_uri_to_path(uri: str) -> str:
    """Best-effort conversion for MCP file:// root URIs."""
    parsed = urlparse(str(uri))
    if parsed.scheme != "file":
        return str(uri)
    path = unquote(parsed.path)
    if parsed.netloc:
        return f"//{parsed.netloc}{path}"
    if len(path) >= 3 and path[0] == "/" and path[2] == ":":
        return path[1:]
    return path


def _is_windows_abs(path: str) -> bool:
    return PureWindowsPath(path).is_absolute()


def _is_posix_abs(path: str) -> bool:
    return PurePosixPath(path).is_absolute()


def _is_abs(path: str) -> bool:
    return _is_windows_abs(path) or _is_posix_abs(path)


def _norm_host(path: str) -> str:
    return str(path).replace("\\", "/").rstrip("/")


def _join_host(root: str, relative: Path) -> str:
    if _is_windows_abs(root):
        return str(PureWindowsPath(root) / PureWindowsPath(relative.as_posix()))
    return str(PurePosixPath(root) / PurePosixPath(relative.as_posix()))


def get_host_root() -> Optional[str]:
    """Return the host root mounted into the container, if configured."""
    host_root = os.environ.get("GHOST_HOST_ROOT")
    if host_root:
        return _norm_host(host_root)
    return None


def get_host_root_mount() -> Path:
    return Path(os.environ.get("GHOST_HOST_ROOT_MOUNT", _DEFAULT_HOST_ROOT_MOUNT))


def get_client_workspace() -> Path:
    """Return the filesystem root where client-visible artifacts should be written."""
    if is_running_in_container():
        return Path(os.environ.get("GHOST_CLIENT_WORKSPACE", _DEFAULT_CONTAINER_WORKSPACE))
    return Path.cwd()


def _map_host_path_to_container(host_path: str) -> Optional[Path]:
    host_root = get_host_root()
    if not host_root:
        return None

    normalized_root = _norm_host(host_root)
    normalized_path = _norm_host(host_path)

    # For Windows paths, ensure we handle drive letters correctly
    # Extract drive letter if present
    root_drive = None
    path_drive = None

    if _is_windows_abs(normalized_root):
        root_parts = normalized_root.split("/", 1)
        if len(root_parts) > 0 and len(root_parts[0]) >= 2 and root_parts[0][1] == ":":
            root_drive = root_parts[0].lower()

    if _is_windows_abs(normalized_path):
        path_parts = normalized_path.split("/", 1)
        if len(path_parts) > 0 and len(path_parts[0]) >= 2 and path_parts[0][1] == ":":
            path_drive = path_parts[0].lower()

    # If both have drives and they don't match, this path is not under host_root
    if root_drive and path_drive and root_drive != path_drive:
        return None

    root_cmp = normalized_root.lower() if _is_windows_abs(normalized_root) else normalized_root
    path_cmp = normalized_path.lower() if _is_windows_abs(normalized_path) else normalized_path

    if path_cmp == root_cmp:
        return get_host_root_mount()
    if path_cmp.startswith(f"{root_cmp}/"):
        relative = normalized_path[len(normalized_root) :].lstrip("/")
        return get_host_root_mount() / PurePosixPath(relative)
    return None


def _first_client_root(client_roots: Optional[Iterable[str]]) -> Optional[str]:
    if not client_roots:
        return None
    for root in client_roots:
        if root:
            return file_uri_to_path(str(root))
    return None


def _map_relative_to_client_root(relative_path: str, client_root: Optional[str]) -> Optional[Path]:
    if not client_root:
        return None
    relative = str(relative_path).replace("\\", "/").lstrip("/")
    mapped = _map_host_path_to_container(f"{client_root.rstrip('/')}/{relative}")
    return mapped


def resolve_output_path(output_path: str, client_roots: Optional[Iterable[str]] = None) -> Path:
    """Resolve an output path without leaking Docker artifacts into /app."""
    if not output_path:
        raise ValueError("output_path is required")

    raw_path = Path(str(output_path)).expanduser()
    if not is_running_in_container():
        return raw_path

    workspace = get_client_workspace()
    raw = str(output_path).replace("\\", "/")
    client_root = _first_client_root(client_roots)

    # Debug logging for path resolution
    import logging

    logger = logging.getLogger(__name__)
    logger.debug(f"Resolving output_path: {output_path}")
    logger.debug(f"  raw normalized: {raw}")
    logger.debug(f"  workspace: {workspace}")
    logger.debug(f"  client_root: {client_root}")
    logger.debug(f"  GHOST_HOST_ROOT: {get_host_root()}")
    logger.debug(f"  GHOST_HOST_ROOT_MOUNT: {get_host_root_mount()}")

    mapped_absolute = _map_host_path_to_container(raw)
    if mapped_absolute is not None:
        logger.debug(f"  -> mapped to host_root: {mapped_absolute}")
        return mapped_absolute

    if raw.startswith(f"{workspace.as_posix()}/") or raw == workspace.as_posix():
        relative = raw.removeprefix(workspace.as_posix()).lstrip("/")
        mapped_workspace = _map_relative_to_client_root(relative, client_root)
        if mapped_workspace is not None:
            logger.debug(f"  -> mapped via client_root: {mapped_workspace}")
            return mapped_workspace
        logger.debug(f"  -> using workspace path: {raw}")
        return Path(raw)

    if raw.startswith("/app/"):
        mapped_app = _map_relative_to_client_root(raw.removeprefix("/app/"), client_root)
        if mapped_app is not None:
            logger.debug(f"  -> mapped /app/ via client_root: {mapped_app}")
            return mapped_app
        result = workspace / raw.removeprefix("/app/")
        logger.debug(f"  -> /app/ to workspace: {result}")
        return result

    if raw.startswith("/data/output/"):
        mapped_data = _map_relative_to_client_root(raw.removeprefix("/data/output/"), client_root)
        if mapped_data is not None:
            logger.debug(f"  -> mapped /data/output/ via client_root: {mapped_data}")
            return mapped_data
        result = workspace / raw.removeprefix("/data/output/")
        logger.debug(f"  -> /data/output/ to workspace: {result}")
        return result

    if raw.startswith("/"):
        result = workspace / raw.lstrip("/")
        logger.debug(f"  -> absolute path to workspace: {result}")
        return result

    mapped_relative = _map_relative_to_client_root(raw, client_root)
    if mapped_relative is not None:
        logger.debug(f"  -> mapped relative via client_root: {mapped_relative}")
        return mapped_relative

    result = workspace / raw
    logger.debug(f"  -> fallback to workspace: {result}")
    return result


def output_path_metadata(path: Path) -> Dict[str, str]:
    """Return client-facing path hints for a written artifact."""
    metadata = {"file_path": str(path.absolute())}
    if is_running_in_container():
        workspace = get_client_workspace()
        absolute_path = path.absolute()
        host_root = os.environ.get("GHOST_CLIENT_WORKSPACE_HOST")

        try:
            relative = absolute_path.relative_to(workspace.absolute())
            workspace_hint_root = host_root or "ghost_browser_mcp_output"
            metadata["client_path_hint"] = str(Path(workspace_hint_root) / relative)
            metadata["workspace_mount"] = str(workspace)
            return metadata
        except ValueError:
            pass

        host_mount = get_host_root_mount()
        mounted_host_root = get_host_root()
        try:
            relative = absolute_path.relative_to(host_mount.absolute())
            if mounted_host_root:
                metadata["client_path_hint"] = _join_host(mounted_host_root, relative)
                metadata["host_root_mount"] = str(host_mount)
                return metadata
        except ValueError:
            pass

        metadata["client_path_hint"] = str(
            Path(host_root or "ghost_browser_mcp_output") / path.name
        )
        metadata["workspace_mount"] = str(workspace)
    return metadata
