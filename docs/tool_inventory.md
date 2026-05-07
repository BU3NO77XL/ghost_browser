# MCP Tool Inventory

Total detected in `src/tools`: 225 tools across 32 sections.
All are enabled by default. Use `--minimal` to keep only the core or `--disable-<section>` to prune specific sections.

## Summary by Utility

### A — Most useful / keep first (36 tools)
- `browser-management` (11): Core. Keep. Essential for spawning, navigating, recovering, and closing browsers.
- `cookies-storage` (3): Core for sessions. Small and valuable for login, cookies, and state.
- `element-interaction` (12): Core. Keep. Essential for clicking, typing, querying DOM, capturing screenshots, and reading pages.
- `network-debugging` (5): Core for diagnostics. High value for scraping, debugging, and understanding network calls.
- `tabs` (5): Core. Keep. Very useful for real-world multi-tab workflows.

### B — Very useful on demand (90 tools)
- `browser-cdp-management` (6): Very useful on demand. Windows, permissions, and downloads; important for more complete automation.
- `cdp-advanced` (13): Very useful on demand. Performance, emulation, accessibility, PDF, and low-level input.
- `cdp-functions` (13): Powerful, use with care. Generic JS/CDP execution; flexible but increases surface area and choices.
- `css-management` (6): Very useful on demand. CSS inspection/editing; useful for frontend and visual cloning.
- `debugging` (7): Keep during development. Server diagnostics; can be removed in lean production.
- `dom-snapshot-management` (3): Very useful on demand. Full snapshots; great for analysis, heavy for everyday use.
- `element-extraction` (9): Very useful on demand. Detailed element cloning/extraction; high value, higher cost.
- `fetch-management` (7): Very useful on demand. Request interception/modification; powerful, but not every flow needs it.
- `storage-management` (15): Very useful on demand. Broad storage control; useful when persistent state is needed.
- `system-info-management` (4): Lightweight utility. Server/browser/process info; cheap and good for diagnostics.
- `target-management` (7): Very useful on demand. Powerful for targets, workers, and iframes, but duplicates parts of tabs/browser.

### C — Specialized / disable candidates (75 tools)
- `debugger-management` (9): Specialized. Full JS debugger; valuable for dev, heavy for simple automation.
- `dynamic-hooks` (10): Specialized. Dynamic network hooks; powerful, but complex and less common.
- `file-extraction` (8): Specialized. File-writing versions; useful for large artifacts, but duplicative.
- `log-management` (5): Specialized. Log domain/violations; useful in auditing, rarely used in common navigation.
- `overlay-management` (8): Specialized visual. CDP overlays; useful for visual debugging, expendable in headless automation.
- `profiler-management` (5): Specialized. CPU profiling and coverage; keep for performance/debugging.
- `progressive-cloning` (10): Specialized. Rich incremental cloning; keep if this workflow is frequent.
- `security-management` (3): Sensitive. Certificates/security state; small, but can weaken security.
- `serviceworker-management` (7): Specialized PWA. Good for PWAs; unnecessary for simple browsing.
- `storage-cdp-management` (4): Specialized. Quota and origin cleanup; good for debugging, less used day-to-day.
- `webauthn-management` (6): Specialized auth. Virtual passkeys/FIDO2; keep if testing modern authentication.

### D — Less useful for general use / strong removal candidates (24 tools)
- `animation-management` (6): Low general utility. Animation control; useful in specific visual tests.
- `audits-management` (4): Low general utility. Contrast/encoded responses; good auditing niche.
- `backgroundservice-management` (4): Low general utility. Background PWA events; niche.
- `database-management` (3): Legacy/niche. WebSQL is legacy; strong removal candidate if not used.
- `heapprofiler-management` (7): Low general utility. Heap snapshots and GC; rare outside memory investigation.

## Complete List by Section

### animation-management (6)
Classification: D — Low general utility.
Criteria: Animation control; useful in specific visual tests.

- `get_animation_timing` - Get the current timing information for a specific animation.
- `list_animations` - List all active animations on the current page.
- `pause_animation` - Pause a specific animation by its ID.
- `play_animation` - Resume (play) a paused animation by its ID.
- `seek_animations` - Seek one or more animations to a specific time position.
- `set_animation_playback_rate` - Set the global playback rate for all animations on the page.

### audits-management (4)
Classification: D — Low general utility.
Criteria: Contrast/encoded responses; good auditing niche.

- `audits_check_contrast` - Trigger a contrast check on the current page.
- `audits_disable` - Disable the Audits domain for a browser instance.
- `audits_enable` - Enable the Audits domain for a browser instance.
- `audits_get_encoded_response` - Get an encoded version of a network response.

### backgroundservice-management (4)
Classification: D — Low general utility.
Criteria: Background PWA events; niche.

- `clear_background_service_events` - Clear all recorded background service events for a given service type.
- `get_background_service_events` - Retrieve recorded background service events for a given service type.
- `start_observing_background_service` - Start observing background service events for a given service type.
- `stop_observing_background_service` - Stop observing background service events for a given service type.

### browser-cdp-management (6)
Classification: B — Very useful on demand.
Criteria: Windows, permissions, and downloads; important for more complete automation.

- `browser_get_window_bounds` - Get the bounds of a browser window.
- `browser_get_window_for_target` - Get the browser window ID and bounds for the current target.
- `browser_grant_permissions` - Grant browser permissions for an origin.
- `browser_reset_permissions` - Reset all browser permissions, optionally for a specific origin.
- `browser_set_download_behavior` - Set the download behavior for the browser.
- `browser_set_window_bounds` - Set the bounds (position/size/state) of a browser window.

### browser-management (11)
Classification: A — Core. Keep.
Criteria: Essential for spawning, navigating, recovering, and closing browsers.

- `check_instance_health` - Check if browser instance is healthy and WebSocket connection is alive.
- `check_login_status` - Check if the user has completed login on an open browser instance.
- `close_instance` - Close a browser instance.
- `confirm_manual_login` - Confirm that the user completed manual login and recover the browser instance.
- `get_instance_state` - Get detailed state of a browser instance.
- `go_back` - Navigate back in history.
- `go_forward` - Navigate forward in history.
- `list_instances` - List all active browser instances.
- `navigate` - Navigate to a URL.
- `reload_page` - Reload the current page.
- `spawn_browser` - Spawn a new browser instance.

### cdp-advanced (13)
Classification: B — Very useful on demand.
Criteria: Performance, emulation, accessibility, PDF, and low-level input.

- `dispatch_mouse_event` - Dispatch low-level mouse events via CDP Input domain.
- `emulate_color_scheme` - Emulate prefers-color-scheme media feature (dark/light).
- `emulate_device` - Emulate a mobile device or custom viewport via CDP Emulation domain.
- `emulate_geolocation` - Override geolocation via CDP Emulation domain.
- `emulate_network_conditions` - Throttle network speed via CDP Network domain.
- `get_accessibility_tree` - Get the accessibility tree (AXTree) for the page or a specific element.
- `get_console_logs` - Capture browser console logs (errors, warnings, info, log) via CDP Log domain.
- `get_dom_node_info` - Get detailed CDP DOM node information for an element: nodeId, attributes,
- `get_page_vitals` - Get Core Web Vitals: LCP, FID, CLS, FCP, TTFB via PerformanceObserver.
- `get_performance_metrics` - Get runtime performance metrics via CDP Performance domain.
- `hover_element` - Hover over an element by dispatching mouseMoved CDP event to its center.
- `inject_console_capture` - Inject console capture script into the page.
- `print_to_pdf` - Export the current page as PDF via CDP Page.printToPDF.

### cdp-functions (13)
Classification: B — Powerful, use with care.
Criteria: Generic JS/CDP execution; flexible but increases surface area and choices.

- `call_javascript_function` - Call a JavaScript function with arguments.
- `create_persistent_function` - Create a persistent JavaScript function that survives page reloads.
- `create_python_binding` - Create a binding that allows JavaScript to call Python functions.
- `discover_global_functions` - Discover all global JavaScript functions available in the page.
- `discover_object_methods` - Discover methods of a specific JavaScript object.
- `execute_cdp_command` - Execute Runtime commands or raw fully-qualified CDP methods.
- `execute_function_sequence` - Execute a sequence of JavaScript function calls.
- `execute_python_in_browser` - Execute Python code by translating it to JavaScript.
- `get_execution_contexts` - Get all available JavaScript execution contexts.
- `get_function_executor_info` - Get information about the CDP function executor state.
- `inject_and_execute_script` - Inject and execute custom JavaScript code.
- `inspect_function_signature` - Inspect a JavaScript function's signature and details.
- `list_cdp_commands` - List all available CDP Runtime commands for function execution.

### cookies-storage (3)
Classification: A — Core for sessions.
Criteria: Small and valuable for login, cookies, and state.

- `clear_cookies` - Clear cookies.
- `get_cookies` - Get cookies for current page or specific URLs.
- `set_cookie` - Set a cookie.

### css-management (6)
Classification: B — Very useful on demand.
Criteria: CSS inspection/editing; useful for frontend and visual cloning.

- `get_computed_style` - Get computed CSS styles for an element (all resolved values).
- `get_inline_styles` - Get inline CSS styles for an element.
- `get_matched_styles` - Get all matched CSS styles for an element.
- `get_media_queries` - Get all media queries from the page's stylesheets.
- `get_stylesheet_text` - Get the full text content of a stylesheet by its ID.
- `set_stylesheet_text` - Replace the full text content of a stylesheet.

### database-management (3)
Classification: D — Legacy/niche.
Criteria: WebSQL is legacy; strong removal candidate if not used.

- `execute_websql_query` - Execute a SQL query against a WebSQL database.
- `get_websql_table_names` - Get all table names in a WebSQL database.
- `list_websql_databases` - List all WebSQL databases on the current page.

### debugger-management (9)
Classification: C — Specialized.
Criteria: Full JS debugger; valuable for dev, heavy for simple automation.

- `disable_debugger` - Disable the JavaScript debugger for a browser instance.
- `enable_debugger` - Enable the JavaScript debugger for a browser instance.
- `evaluate_on_call_frame` - Evaluate a JavaScript expression on a specific call frame when paused.
- `get_call_stack` - Get the current JavaScript call stack.
- `remove_breakpoint` - Remove a JavaScript breakpoint by its ID.
- `resume_execution` - Resume JavaScript execution after a breakpoint pause.
- `set_breakpoint` - Set a JavaScript breakpoint at a specific URL and line number.
- `step_into` - Step into the current function call.
- `step_over` - Step over the current statement (execute current line, stop at next).

### debugging (7)
Classification: B — Keep during development.
Criteria: Server diagnostics; can be removed in lean production.

- `clear_debug_view` - Clear all debug logs and statistics with timeout protection.
- `export_debug_logs` - Export debug logs to a file using the fastest available method with timeout protection.
- `get_debug_lock_status` - Get current debug logger lock status for debugging hanging exports.
- `get_debug_view` - Get comprehensive debug view with all logged errors and statistics.
- `hot_reload` - Hot reload all modules without restarting the server.
- `reload_status` - Check the status of loaded modules.
- `validate_browser_environment_tool` - Validate browser environment and diagnose potential issues.

### dom-snapshot-management (3)
Classification: B — Very useful on demand.
Criteria: Full snapshots; great for analysis, heavy for everyday use.

- `dom_snapshot_capture` - Capture a full DOM snapshot of the current page including computed styles.
- `dom_snapshot_disable` - Disable the DOMSnapshot domain for a browser instance.
- `dom_snapshot_enable` - Enable the DOMSnapshot domain for a browser instance.

### dynamic-hooks (10)
Classification: C — Specialized.
Criteria: Dynamic network hooks; powerful, but complex and less common.

- `create_dynamic_hook` - Create a new dynamic hook with AI-generated Python function.
- `create_simple_dynamic_hook` - Create a simple dynamic hook using predefined templates (easier for AI).
- `get_dynamic_hook_details` - Get detailed information about a specific dynamic hook.
- `get_hook_common_patterns` - Get common hook patterns and use cases.
- `get_hook_documentation` - Get comprehensive documentation for creating hook functions (AI learning).
- `get_hook_examples` - Get example hook functions for AI learning.
- `get_hook_requirements_documentation` - Get documentation on hook requirements and matching criteria.
- `list_dynamic_hooks` - List all dynamic hooks.
- `remove_dynamic_hook` - Remove a dynamic hook.
- `validate_hook_function` - Validate hook function code for common issues before creating.

### element-extraction (9)
Classification: B — Very useful on demand.
Criteria: Detailed element cloning/extraction; high value, higher cost.

- `clone_element_complete` - Master function that extracts ALL element data using specialized functions.
- `extract_complete_element_cdp` - Extract complete element using native CDP methods for 100% accuracy.
- `extract_element_animations` - Extract CSS animations, transitions, and transforms.
- `extract_element_assets` - Extract all assets related to an element (images, fonts, etc.).
- `extract_element_events` - Extract complete event listener and JavaScript handler information.
- `extract_element_structure` - Extract complete HTML structure and DOM information.
- `extract_element_styles` - Extract complete styling information from an element.
- `extract_element_styles_cdp` - Extract element styles using direct CDP calls (no JavaScript evaluation).
- `extract_related_files` - Discover and analyze related CSS/JS files for context.

### element-interaction (12)
Classification: A — Core. Keep.
Criteria: Essential for clicking, typing, querying DOM, capturing screenshots, and reading pages.

- `click_element` - Click an element.
- `execute_script` - Execute JavaScript in page context.
- `get_element_state` - Get complete state of an element.
- `get_page_content` - Get page HTML and text content.
- `paste_text` - Paste text instantly into an input field.
- `query_elements` - Query DOM elements.
- `save_page_html` - Serialize the current page DOM and save it directly to disk.
- `scroll_page` - Scroll the page.
- `select_option` - Select an option from a dropdown.
- `take_screenshot` - Take a screenshot of the page.
- `type_text` - Type text into an input field.
- `wait_for_element` - Wait for an element to appear.

### fetch-management (7)
Classification: B — Very useful on demand.
Criteria: Request interception/modification; powerful, but not every flow needs it.

- `fetch_continue_request` - Continue an intercepted request, optionally modifying it.
- `fetch_continue_with_auth` - Continue an intercepted request that requires authentication.
- `fetch_disable` - Disable the Fetch domain, stopping request interception for a browser instance.
- `fetch_enable` - Enable the Fetch domain to intercept network requests for a browser instance.
- `fetch_fail_request` - Cause an intercepted request to fail with the given network error reason.
- `fetch_fulfill_request` - Fulfill an intercepted request with the given response.
- `fetch_get_response_body` - Get the response body for an intercepted request.

### file-extraction (8)
Classification: C — Specialized.
Criteria: File-writing versions; useful for large artifacts, but duplicative.

- `clone_element_to_file` - Clone element completely and save directly to output_path in the workspace.
- `download_element_assets_to_folder` - Download images, backgrounds, icons, fonts, and media related to an element.
- `extract_complete_element_to_file` - Extract complete element via comprehensive cloner and save to output_path.
- `extract_element_animations_to_file` - Extract element animations and save to output_path.
- `extract_element_assets_to_file` - Extract element assets and save to output_path.
- `extract_element_events_to_file` - Extract element events and save to output_path.
- `extract_element_structure_to_file` - Extract element structure and save to output_path.
- `extract_element_styles_to_file` - Extract element styles and save to output_path.

### heapprofiler-management (7)
Classification: D — Low general utility.
Criteria: Heap snapshots and GC; rare outside memory investigation.

- `collect_garbage` - Force a JavaScript garbage collection cycle.
- `get_object_by_heap_id` - Get a JavaScript object by its heap snapshot object ID.
- `start_heap_sampling` - Start heap sampling profiler (low-overhead memory profiling).
- `start_tracking_heap_objects` - Start tracking heap object allocations over time.
- `stop_heap_sampling` - Stop heap sampling and return the sampling profile.
- `stop_tracking_heap_objects` - Stop tracking heap object allocations.
- `take_heap_snapshot` - Take a heap snapshot of the current JavaScript heap.

### log-management (5)
Classification: C — Specialized.
Criteria: Log domain/violations; useful in auditing, rarely used in common navigation.

- `log_clear` - Clear the browser log for a browser instance.
- `log_disable` - Disable the Log domain for a browser instance.
- `log_enable` - Enable the Log domain for a browser instance.
- `log_start_violations_report` - Start violation reporting for a browser instance.
- `log_stop_violations_report` - Stop violation reporting for a browser instance.

### network-debugging (5)
Classification: A — Core for diagnostics.
Criteria: High value for scraping, debugging, and understanding network calls.

- `get_request_details` - Get detailed information about a network request.
- `get_response_content` - Get response body content.
- `get_response_details` - Get response details for a network request.
- `list_network_requests` - List captured network requests.
- `modify_headers` - Modify request headers for future requests.

### overlay-management (8)
Classification: C — Specialized visual.
Criteria: CDP overlays; useful for visual debugging, expendable in headless automation.

- `overlay_disable` - Disable the Overlay domain for a browser instance.
- `overlay_enable` - Enable the Overlay domain for a browser instance.
- `overlay_hide_highlight` - Hide any active highlight on a browser instance.
- `overlay_highlight_node` - Highlight a DOM node with the given highlight configuration.
- `overlay_highlight_rect` - Highlight a rectangular area on the page.
- `overlay_set_show_flex_overlays` - Show CSS flexbox overlays for the specified nodes.
- `overlay_set_show_grid_overlays` - Show CSS grid overlays for the specified nodes.
- `overlay_set_show_scroll_snap_overlays` - Show scroll snap overlays for the specified nodes.

### profiler-management (5)
Classification: C — Specialized.
Criteria: CPU profiling and coverage; keep for performance/debugging.

- `start_code_coverage` - Start collecting JavaScript code coverage data.
- `start_cpu_profiling` - Start CPU profiling for a browser instance.
- `stop_code_coverage` - Stop collecting JavaScript code coverage data.
- `stop_cpu_profiling` - Stop CPU profiling and return the profile data.
- `take_code_coverage_snapshot` - Take a snapshot of the current code coverage data.

### progressive-cloning (10)
Classification: C — Specialized.
Criteria: Rich incremental cloning; keep if this workflow is frequent.

- `clear_all_elements` - Clear all stored elements.
- `clear_stored_element` - Clear a specific stored element.
- `clone_element_progressive` - Clone element progressively - returns lightweight base structure with element_id.
- `expand_animations` - Expand animations and fonts data for a stored element.
- `expand_children` - Expand children data for a stored element.
- `expand_css_rules` - Expand CSS rules data for a stored element.
- `expand_events` - Expand event listeners data for a stored element.
- `expand_pseudo_elements` - Expand pseudo-elements data for a stored element.
- `expand_styles` - Expand styles data for a stored element.
- `list_stored_elements` - List all stored elements with their basic info.

### security-management (3)
Classification: C — Sensitive.
Criteria: Certificates/security state; small, but can weaken security.

- `get_security_state` - Get the current security state of the page.
- `handle_certificate_error` - Handle a certificate error event by continuing or cancelling the request.
- `set_ignore_certificate_errors` - Set whether SSL/TLS certificate errors should be ignored.

### serviceworker-management (7)
Classification: C — Specialized PWA.
Criteria: Good for PWAs; unnecessary for simple browsing.

- `deliver_push_message` - Deliver a simulated push message to a service worker.
- `dispatch_sync_event` - Dispatch a background sync event to a service worker.
- `force_update_service_worker` - Force update a service worker (bypass the 24-hour update throttle).
- `list_service_workers` - List all registered service workers for the current page.
- `set_service_worker_force_update` - Set whether service workers should be force-updated on every page load.
- `skip_waiting_service_worker` - Skip the waiting phase and immediately activate a new service worker.
- `unregister_service_worker` - Unregister a service worker by its scope URL.

### storage-cdp-management (4)
Classification: C — Specialized.
Criteria: Quota and origin cleanup; good for debugging, less used day-to-day.

- `storage_clear_data_for_origin` - Clear storage data for a given origin.
- `storage_get_usage_and_quota` - Get storage usage and quota for a given origin.
- `storage_track_cache_storage_for_origin` - Start tracking cache storage for a given origin.
- `storage_untrack_cache_storage_for_origin` - Stop tracking cache storage for a given origin.

### storage-management (15)
Classification: B — Very useful on demand.
Criteria: Broad storage control; useful when persistent state is needed.

- `clear_local_storage` - Clear all LocalStorage items for a given origin.
- `clear_session_storage` - Clear all SessionStorage items for a given origin.
- `delete_cache` - Delete a Cache Storage cache by name.
- `delete_indexed_database` - Delete an IndexedDB database.
- `get_cached_response` - Retrieve a cached response from Cache Storage.
- `get_indexed_db_data` - Query data from an IndexedDB object store.
- `get_indexed_db_schema` - Get the schema of an IndexedDB database (object stores and indexes).
- `get_local_storage` - Get all LocalStorage items for a given origin.
- `get_session_storage` - Get all SessionStorage items for a given origin.
- `list_cache_storage` - List all Cache Storage cache names for a given origin.
- `list_indexed_databases` - List all IndexedDB database names for a given origin.
- `remove_local_storage_item` - Remove a LocalStorage item for a given origin.
- `remove_session_storage_item` - Remove a SessionStorage item for a given origin.
- `set_local_storage_item` - Set a LocalStorage item for a given origin.
- `set_session_storage_item` - Set a SessionStorage item for a given origin.

### system-info-management (4)
Classification: B — Lightweight utility.
Criteria: Server/browser/process info; cheap and good for diagnostics.

- `get_server_info` - Return information about the MCP server process itself.
- `system_info_get_feature_state` - Return the state of a browser feature flag for a browser instance.
- `system_info_get_info` - Return information about the system for a browser instance.
- `system_info_get_process_info` - Return information about all running browser processes for a browser instance.

### tabs (5)
Classification: A — Core. Keep.
Criteria: Very useful for real-world multi-tab workflows.

- `close_tab` - Close a specific tab.
- `get_active_tab` - Get information about the currently active tab.
- `list_tabs` - List all tabs for a browser instance.
- `new_tab` - Open a new tab in the browser instance.
- `switch_tab` - Switch to a specific tab by bringing it to front.

### target-management (7)
Classification: B — Very useful on demand.
Criteria: Powerful for targets, workers, and iframes, but duplicates parts of tabs/browser.

- `target_activate_target` - Activate (focus) a browser target.
- `target_attach_to_target` - Attach to a browser target to create a debugging session.
- `target_close_target` - Close a browser target.
- `target_create_target` - Create a new browser target (tab/window).
- `target_detach_from_target` - Detach from a browser target session.
- `target_get_target_info` - Get info for a specific browser target.
- `target_get_targets` - Get all browser targets (pages, workers, iframes), excluding browser-type targets.

### webauthn-management (6)
Classification: C — Specialized auth.
Criteria: Virtual passkeys/FIDO2; keep if testing modern authentication.

- `add_virtual_authenticator` - Add a virtual WebAuthn authenticator for testing passkeys and FIDO2.
- `add_webauthn_credential` - Add a credential to a virtual WebAuthn authenticator.
- `get_webauthn_credentials` - Get all credentials stored in a virtual WebAuthn authenticator.
- `remove_virtual_authenticator` - Remove a virtual WebAuthn authenticator.
- `remove_webauthn_credential` - Remove a credential from a virtual WebAuthn authenticator.
- `set_webauthn_user_verified` - Set the user verified state for a virtual WebAuthn authenticator.