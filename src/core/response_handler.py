"""
Response handler.

Large responses are NOT silently saved to a server-side directory anymore —
that would expose client data on the server and accumulate disk garbage.

Instead, when a response exceeds max_tokens the caller receives a structured
error that tells it to use save_page_html or a file-extraction tool with an
explicit output_path pointing to the client workspace.
"""

import json
from typing import Any, Dict, Optional


class ResponseHandler:
    """Handle responses, rejecting oversized payloads with a clear action hint."""

    def __init__(self, max_tokens: int = 20000):
        self.max_tokens = max_tokens
        # clone_dir kept as a no-op attribute so existing code that references
        # response_handler.clone_dir doesn't crash (e.g. take_screenshot).
        # Screenshots still need a temp location — they use a system temp dir.
        self.clone_dir = None

    def estimate_tokens(self, data: Any) -> int:
        """Rough token estimate (~4 chars per token)."""
        if isinstance(data, (dict, list)):
            return len(json.dumps(data, ensure_ascii=False)) // 4
        elif isinstance(data, str):
            return len(data) // 4
        return len(str(data)) // 4

    def handle_response(
        self,
        data: Any,
        fallback_filename_prefix: str = "large_response",
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Return *data* if it fits within max_tokens.

        If it is too large, return a structured error dict that instructs the
        agent to use save_page_html (for HTML) or a file-extraction tool with
        an explicit output_path so the content goes directly to the workspace.

        Args:
            data: The response data.
            fallback_filename_prefix: Hint used in the error message.
            metadata: Optional metadata (instance_id etc.) for the error hint.

        Returns:
            The original data, or an error dict with remediation instructions.
        """
        estimated_tokens = self.estimate_tokens(data)

        if estimated_tokens <= self.max_tokens:
            return data

        instance_id: Optional[str] = (metadata or {}).get("instance_id", "<instance_id>")

        return {
            "error": "response_too_large",
            "estimated_tokens": estimated_tokens,
            "max_tokens": self.max_tokens,
            "message": (
                f"The response is too large (~{estimated_tokens} tokens) to return inline. "
                "Use one of the following tools to save the content directly to your workspace:"
            ),
            "remediation": {
                "for_html": {
                    "tool": "save_page_html",
                    "args": {
                        "instance_id": instance_id,
                        "output_path": "<absolute_path_in_your_workspace>/page.html",
                    },
                },
                "for_structured_data": {
                    "tool": f"extract_{fallback_filename_prefix}_to_file"
                    if not fallback_filename_prefix.startswith("page")
                    else "clone_element_to_file",
                    "args": {
                        "instance_id": instance_id,
                        "output_path": f"<absolute_path_in_your_workspace>/{fallback_filename_prefix}.json",
                    },
                },
            },
        }


# Global instance
response_handler = ResponseHandler()
