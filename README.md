<div align="center">
<img src="docs/media/UndetectedStealthBrowser.png" alt="Ghost Browser MCP" width="200"/>

# Ghost Browser MCP

Undetectable browser automation for MCP-compatible AI agents.

Improved fork of Stealth Browser MCP adapted as Ghost Browser MCP.

Ghost Browser MCP turns a real browser into a full MCP-native research, extraction, and page-reconstruction toolkit. It combines 225 browser tools across 32 sections, Chrome DevTools Protocol access, network inspection, asset downloading, and pixel-accurate page cloning in one agent-ready server.

Bypass Cloudflare, antibot systems, and social media blocks with real browser instances powered by [nodriver](https://github.com/ultrafunkamsterdam/nodriver) + Chrome DevTools Protocol + [FastMCP](https://github.com/jlowin/fastmcp).

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-6A0DAD?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/nodriver-0.48-1a1a1a?style=for-the-badge&logo=googlechrome&logoColor=white" alt="nodriver"/>
  <img src="https://img.shields.io/badge/HTTPx-Async-FF6B6B?style=for-the-badge&logo=fastapi&logoColor=white" alt="HTTPx Async"/>
  <img src="https://img.shields.io/badge/License-MIT-8B0000?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="License MIT"/>
  <img src="https://img.shields.io/badge/author-BU3NO77XL-6A0DAD?style=for-the-badge&logo=github&logoColor=white" alt="Author"/>
</p>


</div>

---

## Table of Contents

- [Demo](#demo)
- [What Ghost Adds](#what-ghost-adds)
- [Features](#features)
- [How It Fits Together](#how-it-fits-together)
- [Quickstart](#quickstart)
- [Modular Architecture](#modular-architecture)
- [Toolbox](#toolbox)
- [Ghost vs Playwright MCP](#ghost-vs-playwright-mcp)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)
- [Showcase](#showcase)
- [Roadmap](#roadmap)
- [Support](#support)
- [License](#license)

---

## Demo

<div align="center">
<img src="docs/media/showcase-demo-full.gif" alt="Ghost Browser MCP Demo" width="800" style="border-radius: 8px;">
<br><br>
<a href="docs/media/Showcase%20Stealth%20Browser%20Mcp.mp4" download>
  <img src="https://img.shields.io/badge/Watch%20HD%20Video-red?style=for-the-badge&logo=video&logoColor=white" alt="Watch HD Video">
</a>
</div>

*Ghost Browser MCP bypassing Cloudflare, cloning UI elements, and intercepting network traffic — all through AI chat commands.*

---

## What Ghost Adds

Ghost Browser MCP is more than a browser controller. It is a practical reverse-engineering and reconstruction toolkit for authorized web analysis:

- **225 MCP tools across 32 sections** — Navigation, screenshots, DOM extraction, CDP commands, network tracing, downloads, sessions, hooks, and page-state inspection.
- **Pixel-accurate cloning** — Extract page structure, styles, computed layout, screenshots, and loaded assets to recreate pages in minutes.
- **Asset-aware extraction** — Download the images, icons, fonts, CSS, and media actually loaded by the current page instead of collecting unrelated noise.
- **Deep page intelligence** — Inspect HTML, accessibility data, console logs, network requests, storage, cookies, event listeners, and element relationships.
- **Manual-login handoff** — Let a human complete authentication in a real browser, then return control to the AI agent with the same session.

---

## Features

- **Antibot bypass** — Works on Cloudflare, Queue-It, and other protection systems that block traditional automation
- **225 tools across 32 sections** — From basic navigation to advanced CDP domain management
- **Modular loading** — Run the full tool suite or a minimal 23-tool core; disable what you don't need
- **Pixel-accurate element cloning** — Extract complete elements with all CSS, DOM structure, events, and assets via CDP
- **Network interception** — Inspect every request, response, header, and payload through your AI agent
- **Dynamic hook system** — AI-generated Python functions that intercept and modify network traffic in real-time
- **Instant text input** — Paste large content via CDP or type with human-like keystrokes and newline support
- **Cross-platform** — Windows, macOS, Linux, and CI/CD pipelines with automatic environment detection
- **Browser support** — Chrome, Chromium, and Microsoft Edge (automatic detection)
- **Clean MCP integration** — No custom brokers or wrappers; works with Claude Code, Claude Desktop, Cursor, and any MCP client

---

## How It Fits Together

```text
Your AI agent
  -> talks to Ghost Browser through MCP (stdio)
  -> Ghost Browser controls Chrome/Chromium
  -> Chrome opens websites, clicks, extracts data, screenshots, assets, and network info
```

---

## Quickstart

### 1. Install uv

Windows (PowerShell):
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS / Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or see the official installation docs: https://docs.astral.sh/uv/getting-started/installation/

### 2. Clone and sync

```bash
git clone https://github.com/BU3NO77XL/Ghost_Browser_MCP.git Ghost_Browser_MCP
cd Ghost_Browser_MCP
uv sync
```

### 3. Add to your MCP client

**Claude Code CLI (recommended):**

Windows:
```bash
claude mcp add-json ghost_browser_mcp "{\"type\":\"stdio\",\"command\":\"C:\\path\\to\\Ghost_Browser_MCP\\.venv\\Scripts\\python.exe\",\"args\":[\"C:\\path\\to\\Ghost_Browser_MCP\\src\\server.py\"],\"env\":{\"PYTHONPATH\":\"C:\\path\\to\\Ghost_Browser_MCP\\src\"}}"
```

Mac/Linux:
```bash
claude mcp add-json ghost_browser_mcp '{
  "type": "stdio",
  "command": "/path/to/Ghost_Browser_MCP/.venv/bin/python",
  "args": ["/path/to/Ghost_Browser_MCP/src/server.py"],
  "env": {"PYTHONPATH": "/path/to/Ghost_Browser_MCP/src"}
}'
```

> Replace `/path/to/Ghost_Browser_MCP/` with your actual project path.

<details>
<summary><strong>Manual JSON configuration (Claude Desktop, Cursor, Kiro, etc.)</strong></summary>

Windows (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "ghost_browser_mcp": {
      "type": "stdio",
      "command": "C:\\path\\to\\Ghost_Browser_MCP\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\Ghost_Browser_MCP\\src\\server.py"],
      "env": {
        "PYTHONPATH": "C:\\path\\to\\Ghost_Browser_MCP\\src"
      }
    }
  }
}
```

Mac/Linux (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "ghost_browser_mcp": {
      "type": "stdio",
      "command": "/path/to/Ghost_Browser_MCP/.venv/bin/python",
      "args": ["/path/to/Ghost_Browser_MCP/src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/Ghost_Browser_MCP/src"
      }
    }
  }
}
```

> Replace `/path/to/Ghost_Browser_MCP/` with your actual project path.

</details>

<details>
<summary><strong>FastMCP CLI (untested)</strong></summary>

```bash
uv tool install fastmcp
fastmcp install claude-desktop src/server.py
# OR
fastmcp install claude-code src/server.py
# OR
fastmcp install cursor src/server.py
```

</details>

### 4. Test it

Restart your MCP client and ask your agent:

> "Use ghost_browser_mcp to navigate to https://example.com and take a screenshot."

---

## Modular Architecture

Choose exactly what functionality you need. Run the full tool suite or strip it down to 23 core tools.

| Mode | Tools | Use Case |
|------|-------|----------|
| **Full** (default) | 225 | Complete browser automation and debugging across 32 sections |
| **Minimal** (`--minimal`) | 23 | Core browser automation only |
| **Custom** (`--disable-*`) | Your choice | Disable specific sections |

```bash
python src/server.py --minimal
python src/server.py --disable-cdp-functions --disable-dynamic-hooks
python src/server.py --list-sections
```

**Available sections:**

| Section | Tools | Description |
|---------|-------|-------------|
| `browser-management` | 11 | Core browser operations |
| `element-interaction` | 12 | Page interaction and manipulation |
| `element-extraction` | 9 | Element cloning and extraction |
| `file-extraction` | 8 | File-based extraction tools |
| `network-debugging` | 5 | Network monitoring and interception |
| `cdp-advanced` | 13 | Performance, emulation, accessibility, PDF |
| `cdp-functions` | 13 | Chrome DevTools Protocol execution |
| `progressive-cloning` | 10 | Advanced element cloning |
| `cookies-storage` | 3 | Cookie and storage management |
| `tabs` | 5 | Tab management |
| `debugging` | 7 | Debug and system tools |
| `dynamic-hooks` | 10 | AI-powered network hooks |
| `animation-management` | 6 | CSS animation control and inspection |
| `audits-management` | 4 | Contrast checks and encoded responses |
| `backgroundservice-management` | 4 | Background PWA event observation |
| `browser-cdp-management` | 6 | Window management, permissions, downloads |
| `css-management` | 6 | CSS style inspection and editing |
| `database-management` | 3 | WebSQL database queries |
| `debugger-management` | 9 | Full JavaScript debugger (breakpoints, stepping) |
| `dom-snapshot-management` | 3 | Full DOM snapshot with computed styles |
| `fetch-management` | 7 | Granular request interception |
| `heapprofiler-management` | 7 | Heap snapshots, sampling, and GC |
| `log-management` | 5 | CDP Log domain — console logs and violations |
| `overlay-management` | 8 | Element highlighting and visual overlays |
| `profiler-management` | 5 | CPU profiling and code coverage |
| `security-management` | 3 | Certificate and security state |
| `serviceworker-management` | 7 | Service worker lifecycle and push events |
| `storage-cdp-management` | 4 | Origin data clearing and quota |
| `storage-management` | 15 | LocalStorage, SessionStorage, IndexedDB, Cache Storage |
| `system-info-management` | 4 | GPU, process, and feature flag info |
| `target-management` | 7 | Advanced tab, worker, and iframe management |
| `webauthn-management` | 6 | Virtual authenticators and passkey testing |

---

## Toolbox

<details>
<summary><strong>Browser Management</strong></summary>

| Tool | Description |
|------|-------------|
| `spawn_browser()` | Create undetectable browser instance |
| `navigate()` | Navigate to URLs |
| `close_instance()` | Clean shutdown of browser |
| `list_instances()` | Manage multiple sessions |
| `get_instance_state()` | Full browser state information |
| `go_back()` | Navigate back in history |
| `go_forward()` | Navigate forward in history |
| `reload_page()` | Reload current page |
| `check_instance_health()` | Check WebSocket connection health |
| `check_login_status()` | Check if manual login completed |
| `confirm_manual_login()` | Confirm manual login and recover session |

</details>

<details>
<summary><strong>Element Interaction</strong></summary>

| Tool | Description |
|------|-------------|
| `query_elements()` | Find elements by CSS/XPath |
| `click_element()` | Natural clicking |
| `type_text()` | Human-like typing with newline support |
| `paste_text()` | Instant text pasting via CDP |
| `scroll_page()` | Natural scrolling |
| `wait_for_element()` | Smart waiting |
| `execute_script()` | Run JavaScript |
| `select_option()` | Dropdown selection |
| `get_element_state()` | Element properties |
| `get_page_content()` | HTML and text content |
| `take_screenshot()` | Capture page screenshot |
| `save_page_html()` | Serialize DOM directly to disk |

</details>

<details>
<summary><strong>Element Extraction (CDP-accurate)</strong></summary>

| Tool | Description |
|------|-------------|
| `extract_complete_element_cdp()` | Complete CDP-based element clone |
| `clone_element_complete()` | Master extraction function |
| `extract_element_styles()` | 300+ CSS properties via CDP |
| `extract_element_styles_cdp()` | Pure CDP styles extraction |
| `extract_element_structure()` | Full DOM tree |
| `extract_element_events()` | React/Vue/framework listeners |
| `extract_element_animations()` | CSS animations/transitions |
| `extract_element_assets()` | Images, fonts, videos |
| `extract_related_files()` | Related CSS/JS files |

</details>

<details>
<summary><strong>File-Based Extraction</strong></summary>

| Tool | Description |
|------|-------------|
| `extract_element_styles_to_file()` | Save styles to file |
| `extract_element_structure_to_file()` | Save structure to file |
| `extract_element_events_to_file()` | Save events to file |
| `extract_element_animations_to_file()` | Save animations to file |
| `extract_element_assets_to_file()` | Save assets to file |
| `extract_complete_element_to_file()` | Save complete extraction to file |
| `clone_element_to_file()` | Save complete clone to file |
| `download_element_assets_to_folder()` | Download images, fonts, CSS to folder |

</details>

<details>
<summary><strong>Network Debugging</strong></summary>

| Tool | Description |
|------|-------------|
| `list_network_requests()` | List captured network requests |
| `get_request_details()` | Inspect headers and payload for a request |
| `get_response_details()` | Get response metadata |
| `get_response_content()` | Get response body from a request |
| `modify_headers()` | Add custom headers to requests |

</details>

<details>
<summary><strong>CDP Function Execution</strong></summary>

| Tool | Description |
|------|-------------|
| `execute_cdp_command()` | Direct Runtime commands, or raw `Domain.method` CDP commands |
| `discover_global_functions()` | Find JavaScript functions |
| `discover_object_methods()` | Discover object methods (93+ methods) |
| `call_javascript_function()` | Execute any function |
| `inject_and_execute_script()` | Run custom JS code |
| `inspect_function_signature()` | Inspect function details |
| `create_persistent_function()` | Functions that survive reloads |
| `execute_function_sequence()` | Execute function sequences |
| `create_python_binding()` | Create Python-JS bindings |
| `execute_python_in_browser()` | Execute Python code via py2js |
| `get_execution_contexts()` | Get JS execution contexts |
| `list_cdp_commands()` | List available CDP commands |
| `get_function_executor_info()` | Get executor state info |

</details>

<details>
<summary><strong>Progressive Element Cloning</strong></summary>

| Tool | Description |
|------|-------------|
| `clone_element_progressive()` | Initial lightweight structure |
| `expand_styles()` | On-demand styles expansion |
| `expand_events()` | On-demand events expansion |
| `expand_children()` | Progressive children expansion |
| `expand_css_rules()` | Expand CSS rules data |
| `expand_pseudo_elements()` | Expand pseudo-elements |
| `expand_animations()` | Expand animations data |
| `list_stored_elements()` | List stored elements |
| `clear_stored_element()` | Clear specific element |
| `clear_all_elements()` | Clear all stored elements |

</details>

<details>
<summary><strong>Cookie and Storage</strong></summary>

| Tool | Description |
|------|-------------|
| `get_cookies()` | Read cookies |
| `set_cookie()` | Set cookies |
| `clear_cookies()` | Clear cookies |

</details>

<details>
<summary><strong>Tabs</strong></summary>

| Tool | Description |
|------|-------------|
| `list_tabs()` | List open tabs |
| `new_tab()` | Create new tab |
| `switch_tab()` | Change active tab |
| `close_tab()` | Close tab |
| `get_active_tab()` | Get current tab |

</details>

<details>
<summary><strong>Debugging and Diagnostics</strong></summary>

| Tool | Description |
|------|-------------|
| `get_debug_view()` | Debug info with pagination |
| `clear_debug_view()` | Clear debug logs |
| `export_debug_logs()` | Export logs (JSON/pickle/gzip) |
| `get_debug_lock_status()` | Debug lock status |
| `hot_reload()` | Hot reload modules without restart |
| `reload_status()` | Check module reload status |
| `validate_browser_environment_tool()` | Diagnose platform issues and browser compatibility |

</details>

<details>
<summary><strong>CDP Advanced — Performance, Emulation, Accessibility</strong></summary>

| Tool | Description |
|------|-------------|
| `get_performance_metrics()` | JS heap, DOM nodes, layout count |
| `get_page_vitals()` | LCP, FID, CLS, FCP, TTFB |
| `emulate_device()` | Mobile device presets (iPhone 14, Pixel 7, etc.) |
| `emulate_geolocation()` | Override geolocation coordinates |
| `emulate_color_scheme()` | Dark/light mode emulation |
| `emulate_network_conditions()` | Throttle network (2G, 3G, 4G, offline) |
| `get_accessibility_tree()` | AXTree for screen reader testing |
| `get_console_logs()` | Browser console log capture |
| `inject_console_capture()` | Inject console capture before navigation |
| `get_dom_node_info()` | CDP DOM node details and bounding box |
| `print_to_pdf()` | Export page as PDF via CDP |
| `dispatch_mouse_event()` | Low-level mouse events via CDP Input |
| `hover_element()` | Hover over element via mouseMoved event |

</details>

<details>
<summary><strong>Animation Management</strong></summary>

| Tool | Description |
|------|-------------|
| `list_animations()` | List all active CSS/Web Animations |
| `pause_animation()` | Pause animation by ID |
| `play_animation()` | Resume paused animation |
| `set_animation_playback_rate()` | Global playback rate control |
| `seek_animations()` | Seek to specific time position |
| `get_animation_timing()` | Current timing information |

</details>

<details>
<summary><strong>Audits Management</strong></summary>

| Tool | Description |
|------|-------------|
| `audits_enable()` | Enable Audits domain |
| `audits_disable()` | Disable Audits domain |
| `audits_get_encoded_response()` | Encode response (webp/jpeg/png) |
| `audits_check_contrast()` | Trigger contrast check |

</details>

<details>
<summary><strong>BackgroundService Management</strong></summary>

| Tool | Description |
|------|-------------|
| `start_observing_background_service()` | Observe sync/fetch/push events |
| `stop_observing_background_service()` | Stop observation |
| `get_background_service_events()` | Retrieve recorded events |
| `clear_background_service_events()` | Clear recorded events |

</details>

<details>
<summary><strong>Browser CDP Management</strong></summary>

| Tool | Description |
|------|-------------|
| `browser_get_window_for_target()` | Get window ID and bounds |
| `browser_set_window_bounds()` | Set position/size/state |
| `browser_get_window_bounds()` | Get window bounds |
| `browser_grant_permissions()` | Grant permissions for origin |
| `browser_reset_permissions()` | Reset all permissions |
| `browser_set_download_behavior()` | Allow/deny downloads |

</details>

<details>
<summary><strong>CSS Management</strong></summary>

| Tool | Description |
|------|-------------|
| `get_matched_styles()` | All matched CSS styles for element |
| `get_inline_styles()` | Inline styles only |
| `get_computed_style()` | All resolved computed values |
| `get_stylesheet_text()` | Full stylesheet content by ID |
| `set_stylesheet_text()` | Replace stylesheet content |
| `get_media_queries()` | All media queries from page |

</details>

<details>
<summary><strong>Database Management (WebSQL)</strong></summary>

| Tool | Description |
|------|-------------|
| `list_websql_databases()` | List all WebSQL databases |
| `get_websql_table_names()` | Get table names from database |
| `execute_websql_query()` | Run SQL query (with parameters) |

</details>

<details>
<summary><strong>Debugger Management</strong></summary>

| Tool | Description |
|------|-------------|
| `enable_debugger()` | Enable JavaScript debugger |
| `disable_debugger()` | Disable JavaScript debugger |
| `set_breakpoint()` | Set breakpoint at URL + line |
| `remove_breakpoint()` | Remove breakpoint by ID |
| `resume_execution()` | Resume after breakpoint pause |
| `step_over()` | Step over current statement |
| `step_into()` | Step into function call |
| `get_call_stack()` | Get current call stack |
| `evaluate_on_call_frame()` | Evaluate expression in call frame |

</details>

<details>
<summary><strong>DOM Snapshot Management</strong></summary>

| Tool | Description |
|------|-------------|
| `dom_snapshot_enable()` | Enable DOMSnapshot domain |
| `dom_snapshot_disable()` | Disable DOMSnapshot domain |
| `dom_snapshot_capture()` | Full DOM snapshot with computed styles |

</details>

<details>
<summary><strong>Fetch Management (Request Interception)</strong></summary>

| Tool | Description |
|------|-------------|
| `fetch_enable()` | Enable Fetch domain for interception |
| `fetch_disable()` | Disable Fetch domain |
| `fetch_fail_request()` | Fail request with error reason |
| `fetch_fulfill_request()` | Fulfill with custom response |
| `fetch_continue_request()` | Continue with optional modifications |
| `fetch_continue_with_auth()` | Continue with auth credentials |
| `fetch_get_response_body()` | Get response body of intercepted request |

</details>

<details>
<summary><strong>HeapProfiler Management</strong></summary>

| Tool | Description |
|------|-------------|
| `take_heap_snapshot()` | Full heap snapshot (metadata preview) |
| `start_heap_sampling()` | Low-overhead sampling profiler |
| `stop_heap_sampling()` | Stop and return sampling profile |
| `start_tracking_heap_objects()` | Track allocations over time |
| `stop_tracking_heap_objects()` | Stop tracking |
| `collect_garbage()` | Force garbage collection |
| `get_object_by_heap_id()` | Inspect specific heap object |

</details>

<details>
<summary><strong>Profiler Management</strong></summary>

| Tool | Description |
|------|-------------|
| `start_cpu_profiling()` | Start CPU profiling |
| `stop_cpu_profiling()` | Stop and return profile data |
| `start_code_coverage()` | Track script execution coverage |
| `stop_code_coverage()` | Stop coverage collection |
| `take_code_coverage_snapshot()` | Snapshot of current coverage |

</details>

<details>
<summary><strong>Security Management</strong></summary>

| Tool | Description |
|------|-------------|
| `get_security_state()` | HTTPS and connection security info |
| `set_ignore_certificate_errors()` | Enable/disable SSL bypass |
| `handle_certificate_error()` | Respond to certificate error event |

</details>

<details>
<summary><strong>ServiceWorker Management</strong></summary>

| Tool | Description |
|------|-------------|
| `list_service_workers()` | List registered service workers |
| `unregister_service_worker()` | Remove service worker |
| `force_update_service_worker()` | Bypass 24-hour update throttle |
| `skip_waiting_service_worker()` | Activate new worker immediately |
| `set_service_worker_force_update()` | Force update on every load |
| `deliver_push_message()` | Simulate push notification |
| `dispatch_sync_event()` | Trigger background sync |

</details>

<details>
<summary><strong>Storage CDP Management</strong></summary>

| Tool | Description |
|------|-------------|
| `storage_clear_data_for_origin()` | Clear cookies, localStorage, etc. |
| `storage_get_usage_and_quota()` | Storage usage in bytes |
| `storage_track_cache_storage_for_origin()` | Start cache storage tracking |
| `storage_untrack_cache_storage_for_origin()` | Stop cache storage tracking |

</details>

<details>
<summary><strong>Storage Management (Full)</strong></summary>

| Tool | Description |
|------|-------------|
| `get_local_storage()` | Read all LocalStorage for origin |
| `set_local_storage_item()` | Set LocalStorage key/value |
| `remove_local_storage_item()` | Remove LocalStorage key |
| `clear_local_storage()` | Clear all LocalStorage |
| `get_session_storage()` | Read all SessionStorage |
| `set_session_storage_item()` | Set SessionStorage key/value |
| `remove_session_storage_item()` | Remove SessionStorage key |
| `clear_session_storage()` | Clear all SessionStorage |
| `list_indexed_databases()` | List IndexedDB databases |
| `get_indexed_db_schema()` | Object stores and indexes |
| `get_indexed_db_data()` | Query records with pagination |
| `delete_indexed_database()` | Delete entire IndexedDB database |
| `list_cache_storage()` | List Cache Storage caches |
| `get_cached_response()` | Retrieve cached response |
| `delete_cache()` | Delete cache by name |

</details>

<details>
<summary><strong>System Info Management</strong></summary>

| Tool | Description |
|------|-------------|
| `get_server_info()` | Server cwd, platform, Python version |
| `system_info_get_info()` | GPU, model name, browser launch command |
| `system_info_get_feature_state()` | Browser feature flag status |
| `system_info_get_process_info()` | Running browser processes |

</details>

<details>
<summary><strong>Target Management</strong></summary>

| Tool | Description |
|------|-------------|
| `target_get_targets()` | List all targets (pages, workers, iframes) |
| `target_get_target_info()` | Get specific target info |
| `target_create_target()` | Open new tab/window |
| `target_close_target()` | Close target |
| `target_activate_target()` | Focus target |
| `target_attach_to_target()` | Create debugging session |
| `target_detach_from_target()` | Detach from session |

</details>

<details>
<summary><strong>WebAuthn Management</strong></summary>

| Tool | Description |
|------|-------------|
| `add_virtual_authenticator()` | Add CTAP2/U2F authenticator |
| `remove_virtual_authenticator()` | Remove authenticator |
| `add_webauthn_credential()` | Add credential to authenticator |
| `get_webauthn_credentials()` | List stored credentials |
| `remove_webauthn_credential()` | Remove credential |
| `set_webauthn_user_verified()` | Set user verified state |

</details>

---

## Ghost vs Playwright MCP

| Feature | Ghost Browser MCP | Playwright MCP |
|---------|---------------------|----------------|
| Cloudflare / Queue-It | Consistently bypasses | Commonly blocked |
| Banking / Gov portals | Works | Frequently blocked |
| Social media automation | Full automation | Captchas and bans |
| UI element cloning | CDP-accurate extraction | Limited |
| Network debugging | Full request/response inspection via AI | Basic |
| API reverse engineering | Payload inspection through chat | Manual tools only |
| Dynamic hook system | AI-generated Python functions for real-time interception | Not available |
| Modular architecture | 32 sections, 23–225 tools | Fixed ~20 tools |
| Total tools | 225 across 32 sections (customizable) | ~20 |

Tested on: LinkedIn, Instagram, Twitter/X, Amazon, banking portals, government sites, Cloudflare-protected APIs, Nike SNKRS, Ticketmaster, Supreme.

---

## Troubleshooting

**No compatible browser found**
Install Chrome, Chromium, or Microsoft Edge. The server auto-detects the first available browser. Run `validate_browser_environment_tool()` to diagnose.

**Tools hang or return malformed JSON**
This fork includes the upstream fix for stdout corruption from [#8](https://github.com/vibheksoni/stealth-browser-mcp/issues/8). Re-sync the environment if you are updating an older checkout.

**Browser crashes on Linux / CI**
Run with `--sandbox=false` or ensure your environment supports sandboxing. The server auto-detects root and CI environments and adjusts accordingly.

**Too many tools cluttering the AI chat**
Use `--minimal` for 23 core tools, or selectively disable sections:
```bash
python src/server.py --disable-cdp-functions --disable-dynamic-hooks --disable-progressive-cloning
```

**Module not found errors**
Make sure you synchronized the project environment from the repository root:
```bash
uv sync
```

---

## Examples

- **Market research** — Extract pricing and features from competitors, output a comparison table
- **UI cloning** — Recreate a pricing section with exact fonts, styles, and interactions
- **Inventory monitoring** — Watch a product page and alert when stock changes
- **API reverse engineering** — Intercept requests, map endpoints, and inspect data flow

All driven from a single AI agent conversation.

---

## Showcase

<div align="center">
<img src="docs/media/AugmentHeroClone.PNG" alt="Augment Code Hero Recreation" width="700" style="border-radius: 8px;">
</div>

**Augment Code hero clone** — A user asked Claude to clone the hero section from [augmentcode.com](https://www.augmentcode.com/). The agent spawned a ghost browser, navigated to the site, extracted the complete element via CDP (styles, structure, assets), and generated a pixel-accurate HTML recreation with responsive design and animations. The entire process took under two minutes of conversation.

---

## Roadmap

Roadmap items are tracked in this fork and, when relevant, in the upstream repository.

---

## Support

Issues, feature requests, and contributions are welcome through this repository.

---

## License

MIT — see [LICENSE](LICENSE).
