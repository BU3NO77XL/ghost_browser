"""Tests for server startup configuration parsing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_minimal_disables_non_core_sections():
    import server

    disabled = server._disabled_sections_from_args(["server.py", "--minimal"])

    assert "element-extraction" in disabled
    assert "network-debugging" in disabled
    assert "cdp-functions" in disabled
    assert "browser-management" not in disabled
    assert "element-interaction" not in disabled


def test_explicit_disable_flags_map_to_sections():
    import server

    disabled = server._disabled_sections_from_args(
        [
            "server.py",
            "--disable-browser-management",
            "--disable-cdp-functions",
            "--transport",
            "http",
        ]
    )

    assert disabled == {"browser-management", "cdp-functions"}
