"""Integration tests verifying all nine new CDP domain tool modules register correctly."""

import pytest
from unittest.mock import MagicMock

EXPECTED_TOOLS = [
    # Log
    "log_enable",
    "log_disable",
    "log_clear",
    "log_start_violations_report",
    "log_stop_violations_report",
    # StorageCDP
    "storage_clear_data_for_origin",
    "storage_get_usage_and_quota",
    "storage_track_cache_storage_for_origin",
    "storage_untrack_cache_storage_for_origin",
    # SystemInfo
    "system_info_get_info",
    "system_info_get_feature_state",
    "system_info_get_process_info",
    # Fetch
    "fetch_enable",
    "fetch_disable",
    "fetch_fail_request",
    "fetch_fulfill_request",
    "fetch_continue_request",
    "fetch_continue_with_auth",
    "fetch_get_response_body",
    # Overlay
    "overlay_enable",
    "overlay_disable",
    "overlay_highlight_node",
    "overlay_hide_highlight",
    "overlay_highlight_rect",
    "overlay_set_show_grid_overlays",
    "overlay_set_show_flex_overlays",
    "overlay_set_show_scroll_snap_overlays",
    # Audits
    "audits_enable",
    "audits_disable",
    "audits_get_encoded_response",
    "audits_check_contrast",
    # Target
    "target_get_targets",
    "target_get_target_info",
    "target_create_target",
    "target_close_target",
    "target_activate_target",
    "target_attach_to_target",
    "target_detach_from_target",
    # BrowserCDP
    "browser_get_window_for_target",
    "browser_set_window_bounds",
    "browser_get_window_bounds",
    "browser_grant_permissions",
    "browser_reset_permissions",
    "browser_set_download_behavior",
    # DOMSnapshot
    "dom_snapshot_enable",
    "dom_snapshot_disable",
    "dom_snapshot_capture",
]

NEW_MODULES = [
    "log_management",
    "storage_cdp_management",
    "system_info_management",
    "fetch_management",
    "overlay_management",
    "audits_management",
    "target_management",
    "browser_cdp_management",
    "dom_snapshot_management",
]


def _make_deps():
    bm = MagicMock()
    return {"browser_manager": bm}


def _make_section_tool():
    registered = {}

    def section_tool(section):
        def decorator(func):
            registered[func.__name__] = func
            return func

        return decorator

    return section_tool, registered


def test_all_nine_modules_importable():
    """All nine new tool modules must import without errors."""
    import importlib

    for mod_name in NEW_MODULES:
        mod = importlib.import_module(f"tools.{mod_name}")
        assert hasattr(mod, "register"), f"{mod_name} missing register()"


def test_all_expected_tools_registered():
    """All 46 new tool names must be present after registration."""
    import importlib

    mcp = MagicMock()
    deps = _make_deps()
    section_tool, registered = _make_section_tool()

    for mod_name in NEW_MODULES:
        mod = importlib.import_module(f"tools.{mod_name}")
        result = mod.register(mcp, section_tool, deps)
        if isinstance(result, dict):
            registered.update(result)

    for tool_name in EXPECTED_TOOLS:
        assert tool_name in registered, f"Tool '{tool_name}' not registered"


def test_register_returns_callable_dict():
    """Each module's register() must return a dict of callables."""
    import importlib

    mcp = MagicMock()
    deps = _make_deps()
    section_tool, _ = _make_section_tool()

    for mod_name in NEW_MODULES:
        mod = importlib.import_module(f"tools.{mod_name}")
        result = mod.register(mcp, section_tool, deps)
        assert isinstance(result, dict), f"{mod_name}.register() did not return a dict"
        for name, fn in result.items():
            assert callable(fn), f"{mod_name}: '{name}' is not callable"
