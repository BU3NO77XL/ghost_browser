# Communication Flow — Ghost Browser MCP

## Simplified Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Agent (MCP Client)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ MCP Protocol (stdio)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                         server.py                                │
│  • Creates FastMCP instance                                      │
│  • Defines lifecycle (startup/shutdown)                          │
│  • Creates singletons (browser_manager, network_interceptor, etc.)│
│  • Registers tools from modules in tools/                        │
│  • Exposes functions in namespace for tests                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Dependency Injection (_deps)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      tools/ (32 modules)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ browser_management          (11 tools)                   │   │
│  │ element_interaction         (12 tools)                   │   │
│  │ network_debugging           (5 tools)                    │   │
│  │ cookies_storage             (3 tools)                    │   │
│  │ tabs                        (5 tools)                    │   │
│  │ debugging                   (7 tools)                    │   │
│  │ element_extraction          (9 tools)                    │   │
│  │ file_extraction             (8 tools)                    │   │
│  │ progressive_cloning         (10 tools)                   │   │
│  │ cdp_functions               (13 tools)                   │   │
│  │ cdp_advanced                (13 tools)                   │   │
│  │ dynamic_hooks               (10 tools)                   │   │
│  │ animation_management        (6 tools)                    │   │
│  │ audits_management           (4 tools)                    │   │
│  │ backgroundservice_management(4 tools)                    │   │
│  │ browser_cdp_management      (6 tools)                    │   │
│  │ css_management              (6 tools)                    │   │
│  │ database_management         (3 tools)                    │   │
│  │ debugger_management         (9 tools)                    │   │
│  │ dom_snapshot_management     (3 tools)                    │   │
│  │ fetch_management            (7 tools)                    │   │
│  │ heapprofiler_management     (7 tools)                    │   │
│  │ log_management              (5 tools)                    │   │
│  │ overlay_management          (8 tools)                    │   │
│  │ profiler_management         (5 tools)                    │   │
│  │ security_management         (3 tools)                    │   │
│  │ serviceworker_management    (7 tools)                    │   │
│  │ storage_cdp_management      (4 tools)                    │   │
│  │ storage_management          (15 tools)                   │   │
│  │ system_info_management      (4 tools)                    │   │
│  │ target_management           (7 tools)                    │   │
│  │ webauthn_management         (6 tools)                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Uses injected dependencies
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              Core Services (Business Logic)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ browser_manager.py             - Manages browsers        │   │
│  │ network_interceptor.py         - Intercepts network      │   │
│  │ dom_handler.py                 - Manipulates DOM         │   │
│  │ cdp_function_executor.py       - Executes CDP            │   │
│  │ element_cloner.py              - Clones elements         │   │
│  │ comprehensive_element_cloner.py- Full element clone      │   │
│  │ file_based_element_cloner.py   - File-based cloning      │   │
│  │ progressive_element_cloner.py  - Progressive cloning     │   │
│  │ cookie_manager.py              - Manages cookies         │   │
│  │ login_guard.py                 - Controls access         │   │
│  │ manual_login_handler.py        - Manual login            │   │
│  │ response_handler.py            - Manages responses       │   │
│  │ dynamic_hook_ai.py             - AI hook system          │   │
│  │ log_handler.py                 - CDP Log domain          │   │
│  │ storage_cdp_handler.py         - CDP Storage domain      │   │
│  │ system_info_handler.py         - CDP SystemInfo domain   │   │
│  │ fetch_handler.py               - CDP Fetch domain        │   │
│  │ overlay_handler.py             - CDP Overlay domain      │   │
│  │ audits_handler.py              - CDP Audits domain       │   │
│  │ target_handler.py              - CDP Target domain       │   │
│  │ browser_cdp_handler.py         - CDP Browser domain      │   │
│  │ dom_snapshot_handler.py        - CDP DOMSnapshot domain  │   │
│  │ css_handler.py                 - CDP CSS domain          │   │
│  │ database_handler.py            - CDP Database domain     │   │
│  │ serviceworker_handler.py       - CDP ServiceWorker       │   │
│  │ backgroundservice_handler.py   - CDP BackgroundService   │   │
│  │ webauthn_handler.py            - CDP WebAuthn domain     │   │
│  │ security_handler.py            - CDP Security domain     │   │
│  │ animation_handler.py           - CDP Animation domain    │   │
│  │ debugger_handler.py            - CDP Debugger domain     │   │
│  │ profiler_handler.py            - CDP Profiler domain     │   │
│  │ heapprofiler_handler.py        - CDP HeapProfiler domain │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Uses infrastructure
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              Infrastructure (Storage, Logging, Utils)            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ persistent_storage.py    - Persistent storage            │   │
│  │ process_cleanup.py       - Process cleanup               │   │
│  │ platform_utils.py        - Platform utilities            │   │
│  │ debug_logger.py          - Centralized logging           │   │
│  │ models.py                - Pydantic models               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Complete Flow Example: Spawn Browser

```
1. AI Agent sends MCP command:
   spawn_browser(headless=False, viewport_width=1920)
   
2. server.py receives and routes to:
   tools/browser_management.py → spawn_browser()
   
3. spawn_browser() uses injected dependencies:
   ├─→ browser_manager.spawn_browser(options)
   │   ├─→ platform_utils.validate_browser_environment()
   │   ├─→ process_cleanup.track_process(pid)
   │   └─→ persistent_storage.store_instance(instance_id, data)
   │
   └─→ network_interceptor.setup_interception(tab, instance_id)
       └─→ dynamic_hook_system.apply_hooks(instance_id)
   
4. Returns to AI Agent:
   {"instance_id": "abc123", "state": "ready", ...}
```

## Complete Flow Example: Navigate + Login Detection

```
1. AI Agent sends MCP command:
   navigate(instance_id="abc123", url="https://example.com")
   
2. server.py receives and routes to:
   tools/browser_management.py → navigate()
   
3. navigate() orchestrates multiple dependencies:
   ├─→ browser_manager.get_tab(instance_id)
   │   └─→ Returns browser tab
   │
   ├─→ cookie_manager.inject_cookies_from_file(tab, url)
   │   ├─→ Reads cookies.txt (Netscape format)
   │   ├─→ Filters cookies by domain
   │   └─→ Injects via network_interceptor.set_cookie()
   │
   ├─→ tab.get(url)  # Navigates
   │
   ├─→ manual_login_handler.detect_login_page(tab)
   │   ├─→ Checks if login page
   │   └─→ If YES: registers pending login
   │
   └─→ If login detected:
       ├─→ login_watcher.start_watching(instance_id, tab)
       └─→ Returns {"login_required": true, ...}
   
4. If login_required=true:
   AI Agent STOPS and asks user to log in manually
   
5. User logs in and confirms
   
6. AI Agent sends:
   confirm_manual_login(instance_id="abc123")
   
7. confirm_manual_login() verifies:
   ├─→ login_watcher.consume_detected(instance_id)
   │   └─→ Checks if watcher detected login
   │
   └─→ manual_login_handler.confirm_login(instance_id, tab)
       ├─→ Checks if still on login page
       └─→ If OK: removes pending login
   
8. Returns to AI Agent:
   {"success": true, "current_url": "https://example.com/dashboard"}
```

## Complete Flow Example: Click Element

```
1. AI Agent sends MCP command:
   click_element(instance_id="abc123", selector="button.login")
   
2. server.py receives and routes to:
   tools/element_interaction.py → click_element()
   
3. click_element() checks guard and executes:
   ├─→ login_guard.check_pending_login_guard(instance_id)
   │   └─→ If pending login: returns error blocking execution
   │
   ├─→ browser_manager.get_tab(instance_id)
   │   └─→ Returns browser tab
   │
   └─→ dom_handler.click_element(tab, selector)
       ├─→ tab.select(selector)  # Finds element via CDP
       ├─→ element.scroll_into_view()  # Ensures visibility
       ├─→ element.click()  # Clicks via CDP
       └─→ debug_logger.log_info("Clicked element")
   
4. Returns to AI Agent:
   true
```

## Complete Flow Example: Extract Element Styles

```
1. AI Agent sends MCP command:
   extract_element_styles(instance_id="abc123", selector=".hero")
   
2. server.py receives and routes to:
   tools/element_extraction.py → extract_element_styles()
   
3. extract_element_styles() uses element_cloner:
   ├─→ browser_manager.get_tab(instance_id)
   │
   └─→ element_cloner.extract_element_styles(tab, selector)
       ├─→ Loads JavaScript from src/js/extract_styles.js
       ├─→ tab.evaluate(js_code)  # Executes in browser
       ├─→ Extracts computed styles via getComputedStyle()
       ├─→ Extracts CSS rules via getMatchedCSSRules()
       ├─→ Extracts pseudo-elements (::before, ::after)
       └─→ Returns object with all styles
   
4. If response is too large:
   response_handler.handle_response(result)
   ├─→ Estimates tokens (len(json) / 4)
   ├─→ If > 20000 tokens: saves to file
   └─→ Returns {"file_path": "...", "estimated_tokens": ...}
   
5. Returns to AI Agent:
   {
     "computed_styles": {...},
     "css_rules": [...],
     "pseudo_elements": {...}
   }
```

## Dependency Injection

The `server.py` creates a `_deps` container with all dependencies:

```python
# server.py
_deps = {
    "browser_manager": browser_manager,
    "network_interceptor": network_interceptor,
    "dom_handler": dom_handler,
    "cdp_function_executor": cdp_function_executor,
    "element_cloner": element_cloner,
    "comprehensive_element_cloner": comprehensive_element_cloner,
    "file_based_element_cloner": file_based_element_cloner,
    "progressive_element_cloner": progressive_element_cloner,
    "cookie_manager": cookie_manager,
    "login_guard": login_guard,
    "manual_login_handler": manual_login_handler,
    "response_handler": response_handler,
    "persistent_storage": persistent_storage,
    "dynamic_hook_ai": dynamic_hook_ai,
    "debug_logger": debug_logger,
    # CDP domain handlers
    "log_handler": log_handler,
    "storage_cdp_handler": storage_cdp_handler,
    "system_info_handler": system_info_handler,
    "fetch_handler": fetch_handler,
    "overlay_handler": overlay_handler,
    "audits_handler": audits_handler,
    "target_handler": target_handler,
    "browser_cdp_handler": browser_cdp_handler,
    "dom_snapshot_handler": dom_snapshot_handler,
    "css_handler": css_handler,
    "database_handler": database_handler,
    "serviceworker_handler": serviceworker_handler,
    "backgroundservice_handler": backgroundservice_handler,
    "webauthn_handler": webauthn_handler,
    "security_handler": security_handler,
    "animation_handler": animation_handler,
    "debugger_handler": debugger_handler,
    "profiler_handler": profiler_handler,
    "heapprofiler_handler": heapprofiler_handler,
}
```

Each tool module receives `_deps` and extracts what it needs:

```python
# tools/browser_management.py
def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]
    network_interceptor = deps["network_interceptor"]
    manual_login_handler = deps["manual_login_handler"]
    persistent_storage = deps["persistent_storage"]
    
    @section_tool("browser-management")
    async def spawn_browser(...):
        instance = await browser_manager.spawn_browser(...)
        await network_interceptor.setup_interception(...)
        return {...}
```

## Advantages of This Architecture

1. **Separation of Concerns**
   - MCP tools (interface) separated from business logic
   - Core services don't know about MCP
   - Infrastructure is isolated

2. **Testability**
   - Dependencies are easy to mock
   - Tests can import functions from `server.py`
   - Core services are independently testable

3. **Maintainability**
   - Each tool module is ~100-300 lines
   - Easy to find and modify functionality
   - Changes in core services don't affect tools

4. **Reusability**
   - Managers/handlers used by multiple tools
   - Centralized business logic
   - No code duplication

5. **Scalability**
   - Easy to add new tools
   - Easy to add new core services
   - Dependency injection facilitates extension

## What NOT to Do

❌ **Tools importing from other tools**
```python
# ❌ WRONG
from tools.browser_management import spawn_browser
```

❌ **Core services importing from tools**
```python
# ❌ WRONG
from tools.element_interaction import click_element
```

❌ **Tools accessing singletons directly**
```python
# ❌ WRONG
from browser_manager import browser_manager
browser_manager.spawn_browser(...)
```

✅ **Always use dependency injection**
```python
# ✅ CORRECT
def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]
    # Uses injected browser_manager
```
