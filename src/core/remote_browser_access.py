"""Remote browser access — stub for local development mode."""

from typing import Any, Dict, Optional


def build_remote_login_access(instance_id: str) -> Optional[Dict[str, Any]]:
    """Returns None — remote viewer is not available in local development mode."""
    return None
