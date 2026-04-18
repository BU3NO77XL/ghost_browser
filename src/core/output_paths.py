"""Output path handling for local development mode."""

import os
from pathlib import Path, PureWindowsPath
from typing import Dict, Iterable, Optional
from urllib.parse import unquote, urlparse


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


def resolve_output_path(output_path: str, client_roots: Optional[Iterable[str]] = None) -> Path:
    """Resolve an output path for local development mode."""
    if not output_path:
        raise ValueError("output_path is required")
    return Path(str(output_path)).expanduser()


def output_path_metadata(path: Path) -> Dict[str, str]:
    """Return client-facing path hints for a written artifact."""
    return {"file_path": str(path.absolute())}
