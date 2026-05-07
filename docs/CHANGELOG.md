# Changelog

## v0.5.0 — CDP Extended Domains

### 9 New CDP Domains Implemented

**Log Domain** (`log-management`)
- `log_enable` / `log_disable` / `log_clear`
- `log_start_violations_report` / `log_stop_violations_report`

**StorageCDP Domain** (`storage-cdp-management`)
- `storage_clear_data_for_origin` / `storage_get_usage_and_quota` (includes `usage_mb` field)
- `storage_track_cache_storage_for_origin` / `storage_untrack_cache_storage_for_origin`

**SystemInfo Domain** (`system-info-management`)
- `system_info_get_info` / `system_info_get_feature_state` / `system_info_get_process_info`

**Fetch Domain** (`fetch-management`)
- `fetch_enable` / `fetch_disable` / `fetch_fail_request` / `fetch_fulfill_request`
- `fetch_continue_request` / `fetch_continue_with_auth` / `fetch_get_response_body`

**Overlay Domain** (`overlay-management`)
- `overlay_enable` / `overlay_disable` / `overlay_highlight_node` / `overlay_hide_highlight`
- `overlay_highlight_rect` / `overlay_set_show_grid_overlays`
- `overlay_set_show_flex_overlays` / `overlay_set_show_scroll_snap_overlays`

**Audits Domain** (`audits-management`)
- `audits_enable` / `audits_disable`
- `audits_get_encoded_response` (validates encoding: webp, jpeg, png)
- `audits_check_contrast`

**Target Domain** (`target-management`)
- `target_get_targets` (filters out "browser" type targets)
- `target_get_target_info` / `target_create_target` / `target_close_target`
- `target_activate_target` / `target_attach_to_target` / `target_detach_from_target`

**BrowserCDP Domain** (`browser-cdp-management`)
- `browser_get_window_for_target` / `browser_set_window_bounds` / `browser_get_window_bounds`
- `browser_grant_permissions` / `browser_reset_permissions`
- `browser_set_download_behavior` (validates download_path for behavior allow/allowAndName)

**DOMSnapshot Domain** (`dom-snapshot-management`)
- `dom_snapshot_enable` / `dom_snapshot_disable`
- `dom_snapshot_capture` (computed_styles with defaults, node_count, include_dom_rects)

### New Files
- 9 new handlers in `src/core/` (log_handler, storage_cdp_handler, system_info_handler, fetch_handler, overlay_handler, audits_handler, target_handler, browser_cdp_handler, dom_snapshot_handler)
- 9 new tool modules in `src/tools/` (log_management, storage_cdp_management, system_info_management, fetch_management, overlay_management, audits_management, target_management, browser_cdp_management, dom_snapshot_management)
- 19 new test files (9 unit + 10 integration)

### CDP Coverage
- **Before**: ~57% (22 domains, ~163 MCP tools)
- **After**: ~70% (31 domains, ~225 MCP tools)

---

## v0.4.0 — CDP Complete Implementation

### 11 New CDP Domains Implemented

**Storage Domain** (`storage-management`)
- `get_local_storage` / `set_local_storage_item` / `remove_local_storage_item` / `clear_local_storage`
- `get_session_storage` / `set_session_storage_item` / `remove_session_storage_item` / `clear_session_storage`
- `list_indexed_databases` / `get_indexed_db_schema` / `get_indexed_db_data` / `delete_indexed_database`
- `list_cache_storage` / `get_cached_response` / `delete_cache`

**CSS Domain** (`css-management`)
- `get_matched_styles` / `get_inline_styles` / `get_computed_style`
- `get_stylesheet_text` / `set_stylesheet_text` / `get_media_queries`

**Database Domain** (`database-management`)
- `list_websql_databases` / `get_websql_table_names` / `execute_websql_query`

**ServiceWorker Domain** (`serviceworker-management`)
- `list_service_workers` / `unregister_service_worker` / `force_update_service_worker`
- `deliver_push_message` / `dispatch_sync_event` / `skip_waiting_service_worker` / `set_service_worker_force_update`

**BackgroundService Domain** (`backgroundservice-management`)
- `start_observing_background_service` / `stop_observing_background_service`
- `get_background_service_events` / `clear_background_service_events`

**WebAuthn Domain** (`webauthn-management`)
- `add_virtual_authenticator` / `remove_virtual_authenticator`
- `add_webauthn_credential` / `get_webauthn_credentials` / `remove_webauthn_credential` / `set_webauthn_user_verified`

**Security Domain** (`security-management`)
- `get_security_state` / `set_ignore_certificate_errors` / `handle_certificate_error`

**Animation Domain** (`animation-management`)
- `list_animations` / `pause_animation` / `play_animation`
- `set_animation_playback_rate` / `seek_animations` / `get_animation_timing`

**Debugger Domain** (`debugger-management`)
- `enable_debugger` / `disable_debugger` / `set_breakpoint` / `remove_breakpoint`
- `resume_execution` / `step_over` / `step_into` / `get_call_stack` / `evaluate_on_call_frame`

**Profiler Domain** (`profiler-management`)
- `start_cpu_profiling` / `stop_cpu_profiling`
- `start_code_coverage` / `stop_code_coverage` / `take_code_coverage_snapshot`

**HeapProfiler Domain** (`heapprofiler-management`)
- `take_heap_snapshot` / `start_heap_sampling` / `stop_heap_sampling`
- `start_tracking_heap_objects` / `stop_tracking_heap_objects` / `collect_garbage` / `get_object_by_heap_id`

### New Files
- 11 new handlers in `src/core/` (css_handler, database_handler, serviceworker_handler, backgroundservice_handler, webauthn_handler, security_handler, animation_handler, debugger_handler, profiler_handler, heapprofiler_handler)
- 11 new tool modules in `src/tools/` (storage_management, css_management, database_management, serviceworker_management, backgroundservice_management, webauthn_management, security_management, animation_management, debugger_management, profiler_management, heapprofiler_management)

### CDP Coverage
- **Before**: ~30% (8 domains)
- **After**: ~65% (19 domains, ~163 MCP tools)

---

## v0.3.0

### Complete Refactoring
- **87% less code** in server.py (3050 → 400 lines)
- **11 organized modules** in `src/tools/` by category
- **Dependency injection** for easy testing and maintenance
- **CORE vs TOOLS separation** (brain vs gateway)

### Performance Boost
- **HTTPx async** replaces blocking requests
- **4-10x faster** on HTTP operations
- **Parallel requests** instead of serial
- **Event loop freed** — other operations continue

### Technical Improvements
- **Exception handling** improved and documented
- **get_page_state** optimized (1 JS call vs 7+ CDP calls)
- **Reduced timeout** from 30s+ to ~200ms typical
- **108 unit tests** passing

## v0.2.5

- Base version before the complete refactoring