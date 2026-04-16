"""Main MCP server for browser automation."""

import json
import os
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from core.animation_handler import AnimationHandler
from core.audits_handler import AuditsHandler
from core.backgroundservice_handler import BackgroundServiceHandler
from core.browser_cdp_handler import BrowserCDPHandler
from core.browser_manager import BrowserManager
from core.cdp_function_executor import CDPFunctionExecutor
from core.comprehensive_element_cloner import comprehensive_element_cloner
from core.css_handler import CSSHandler
from core.database_handler import DatabaseHandler
from core.debug_logger import debug_logger
from core.debugger_handler import DebuggerHandler
from core.dom_handler import DOMHandler
from core.dom_snapshot_handler import DOMSnapshotHandler
from core.dynamic_hook_ai_interface import dynamic_hook_ai
from core.element_cloner import element_cloner
from core.fetch_handler import FetchHandler
from core.file_based_element_cloner import file_based_element_cloner
from core.heapprofiler_handler import HeapProfilerHandler
from core.log_handler import LogHandler
from core.login_guard import check_pending_login_guard
from core.manual_login_handler import manual_login_handler
from core.network_interceptor import NetworkInterceptor
from core.overlay_handler import OverlayHandler
from core.persistent_storage import persistent_storage
from core.process_cleanup import process_cleanup
from core.profiler_handler import ProfilerHandler
from core.progressive_element_cloner import progressive_element_cloner
from core.response_handler import response_handler
from core.security_handler import SecurityHandler
from core.serviceworker_handler import ServiceWorkerHandler
from core.storage_cdp_handler import StorageCDPHandler
from core.storage_handler import StorageHandler
from core.system_info_handler import SystemInfoHandler
from core.target_handler import TargetHandler
from core.temp_file_manager import temp_file_manager
from core.webauthn_handler import WebAuthnHandler

_MINIMAL_DISABLED_SECTIONS = {
    "element-extraction",
    "file-extraction",
    "network-debugging",
    "cdp-functions",
    "progressive-cloning",
    "cookies-storage",
    "tabs",
    "debugging",
    "dynamic-hooks",
}

_DISABLE_FLAG_TO_SECTION = {
    "--disable-browser-management": "browser-management",
    "--disable-element-interaction": "element-interaction",
    "--disable-element-extraction": "element-extraction",
    "--disable-file-extraction": "file-extraction",
    "--disable-network-debugging": "network-debugging",
    "--disable-cdp-functions": "cdp-functions",
    "--disable-progressive-cloning": "progressive-cloning",
    "--disable-cookies-storage": "cookies-storage",
    "--disable-tabs": "tabs",
    "--disable-debugging": "debugging",
    "--disable-dynamic-hooks": "dynamic-hooks",
}


def _disabled_sections_from_args(argv: List[str]) -> set[str]:
    """Return tool sections disabled by startup flags.

    This intentionally ignores unknown arguments so importing server.py under
    pytest or other launchers cannot fail due to their own CLI flags.
    """
    disabled = set()
    args = set(argv[1:])

    if "--minimal" in args:
        disabled.update(_MINIMAL_DISABLED_SECTIONS)

    for flag, section in _DISABLE_FLAG_TO_SECTION.items():
        if flag in args:
            disabled.add(section)

    return disabled


DISABLED_SECTIONS = _disabled_sections_from_args(sys.argv)


def is_section_enabled(section: str) -> bool:
    """Check if a tool section is enabled."""
    return section not in DISABLED_SECTIONS


def section_tool(section: str):
    """Decorator to conditionally register tools based on section status."""

    def decorator(func):
        if is_section_enabled(section):
            return mcp.tool(func)
        else:
            return func

    return decorator


@asynccontextmanager
async def app_lifespan(server):
    """Manage application lifecycle with proper cleanup."""
    debug_logger.log_info("server", "startup", "Starting Browser Automation MCP Server...")
    try:
        persistent_storage.clear_all()
        debug_logger.log_info(
            "server", "startup", "Cleared stale instances from persistent storage"
        )
    except Exception as e:
        debug_logger.log_error("server", "startup", f"Failed to clear storage on startup: {e}")

    # Clean up orphaned temp files from previous crashed sessions
    try:
        temp_file_manager.cleanup_on_startup(ttl_hours=2)
    except Exception as e:
        debug_logger.log_error("server", "startup", f"Temp file startup cleanup failed: {e}")

    # Start background sweep for deferred instance file cleanup
    try:
        temp_file_manager.start_sweep()
    except Exception as e:
        debug_logger.log_error("server", "startup", f"Temp file sweep start failed: {e}")

    try:
        yield
    finally:
        debug_logger.log_info(
            "server", "shutdown", "Shutting down Browser Automation MCP Server..."
        )
        try:
            await browser_manager.close_all()
            debug_logger.log_info("server", "cleanup", "All browser instances closed")
        except Exception as e:
            debug_logger.log_error("server", "cleanup", e)

        try:
            process_cleanup._cleanup_all_tracked()
            debug_logger.log_info("server", "cleanup", "Process cleanup complete")
        except Exception as e:
            debug_logger.log_error("server", "cleanup", f"Process cleanup failed: {e}")

        # Delete all temp files generated during this session
        try:
            temp_file_manager.cleanup_on_shutdown()
        except Exception as e:
            debug_logger.log_error("server", "cleanup", f"Temp file shutdown cleanup failed: {e}")

        try:
            persistent_instances = persistent_storage.list_instances()
            if persistent_instances.get("instances"):
                debug_logger.log_info(
                    "server",
                    "storage_cleanup",
                    f"Preserving persisted storage with {len(persistent_instances['instances'])} instances",
                )
        except Exception as e:
            debug_logger.log_error("server", "storage_cleanup", e)
        debug_logger.log_info(
            "server", "shutdown", "Browser Automation MCP Server shutdown complete"
        )


mcp = FastMCP(
    name="Browser Automation MCP",
    instructions="""
    This MCP server provides undetectable browser automation using nodriver (CDP-based).

    Key features:
    - Spawn and manage multiple browser instances
    - Navigate, interact, and extract data from web pages
    - Execute CDP commands directly
    - Network interception and monitoring
    - Dynamic hook system for AI-driven automation

    All browser instances are undetectable by anti-bot systems.

    ============================================================
    CRITICAL — WEBSOCKET CONNECTION HANDLING
    ============================================================

    Browser automation uses WebSocket (Chrome DevTools Protocol) for communication.
    WebSocket connections can die if:
    - Browser crashes or becomes unresponsive
    - Network issues occur
    - Browser process is killed

    SYMPTOMS of dead WebSocket:
    - Errors mentioning "WebSocket", "HTTP 500", "connection"
    - Timeouts on simple operations
    - Tools failing with connection errors

    PROTOCOL when WebSocket dies:
    1. Use 'check_instance_health' to verify connection status
    2. If healthy=false and can_recover=false:
       - Call 'close_instance' to clean up
       - Call 'spawn_browser' to create fresh instance
       - Continue automation with new instance
    3. DO NOT keep trying to use a dead instance
    4. DO NOT ask user to fix it - just recreate automatically

    BEST PRACTICE:
    - If you get WebSocket errors, immediately check health and recreate
    - Don't waste time retrying operations on dead connections
    - Inform user briefly: "Browser connection lost, recreating instance..."

    ============================================================
    CRITICAL MANDATORY PROTOCOL — LOGIN HANDLING
    ============================================================

    When the 'navigate' tool returns login_required=true, you MUST follow this EXACT protocol:

    STEP 1: STOP all automation immediately. Do NOT try to interact with the login page.
    STEP 2: Send a message to the user saying:
            "The browser is open and showing a login page. Please go to the browser
             window and log in manually. When you are done, tell me and I will continue."
    STEP 3: WAIT. Do absolutely nothing until the user replies confirming login is done.
    STEP 4: After user confirms, call 'confirm_manual_login' with the SAME instance_id.
    STEP 5: Only after confirm_manual_login returns success=true, resume normal automation.

    IMPORTANT — AUTO-DETECTION:
    The system monitors the browser in background. When the user logs in and navigates
    away from the login page, the watcher detects it automatically.
    When the user tells you they logged in, call confirm_manual_login ONCE. Do NOT loop.
    If it returns success=true, proceed immediately.
    If it returns success=false, tell the user and ask them to try again — do NOT retry automatically.

    PROHIBITED ACTIONS when login_required=true:
    - DO NOT spawn a new browser instance
    - DO NOT close the current browser instance
    - DO NOT try to fill in login forms automatically
    - DO NOT try alternative URLs or workarounds
    - DO NOT conclude that the task is impossible
    - DO NOT call confirm_manual_login more than once without user instruction

    The browser window is OPEN and VISIBLE to the user. The user WILL log in manually.
    Your ONLY job is to WAIT and then call confirm_manual_login ONCE after user confirmation.
    ============================================================
    """,
    lifespan=app_lifespan,
)

# Shared service instances
browser_manager = BrowserManager()
network_interceptor = NetworkInterceptor()
dom_handler = DOMHandler()
cdp_function_executor = CDPFunctionExecutor()
storage_handler = StorageHandler()
css_handler = CSSHandler()
database_handler = DatabaseHandler()
serviceworker_handler = ServiceWorkerHandler()
backgroundservice_handler = BackgroundServiceHandler()
webauthn_handler = WebAuthnHandler()
security_handler = SecurityHandler()
animation_handler = AnimationHandler()
debugger_handler = DebuggerHandler()
profiler_handler = ProfilerHandler()
heapprofiler_handler = HeapProfilerHandler()

# Dependency container passed to tool modules
_deps = {
    "browser_manager": browser_manager,
    "network_interceptor": network_interceptor,
    "dom_handler": dom_handler,
    "cdp_function_executor": cdp_function_executor,
    "element_cloner": element_cloner,
    "comprehensive_element_cloner": comprehensive_element_cloner,
    "file_based_element_cloner": file_based_element_cloner,
    "progressive_element_cloner": progressive_element_cloner,
    "response_handler": response_handler,
    "persistent_storage": persistent_storage,
    "manual_login_handler": manual_login_handler,
    "dynamic_hook_ai": dynamic_hook_ai,
    "debug_logger": debug_logger,
    "storage_handler": storage_handler,
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

# Register all tool sections and expose functions in module namespace
from tools import (
    animation_management,
    audits_management,
    backgroundservice_management,
    browser_cdp_management,
    browser_management,
    cdp_advanced,
    cdp_functions,
    cookies_storage,
    css_management,
    database_management,
    debugger_management,
    debugging,
    dom_snapshot_management,
    dynamic_hooks,
    element_extraction,
    element_interaction,
    fetch_management,
    file_extraction,
    heapprofiler_management,
    log_management,
    network_debugging,
    overlay_management,
    profiler_management,
    progressive_cloning,
    security_management,
    serviceworker_management,
    storage_cdp_management,
    storage_management,
    system_info_management,
    tabs,
    target_management,
    webauthn_management,
)

_tool_modules = [
    browser_management,
    element_interaction,
    network_debugging,
    cookies_storage,
    tabs,
    element_extraction,
    file_extraction,
    progressive_cloning,
    cdp_functions,
    cdp_advanced,
    debugging,
    dynamic_hooks,
    storage_management,
    css_management,
    database_management,
    serviceworker_management,
    backgroundservice_management,
    webauthn_management,
    security_management,
    animation_management,
    debugger_management,
    profiler_management,
    heapprofiler_management,
    log_management,
    storage_cdp_management,
    system_info_management,
    fetch_management,
    overlay_management,
    audits_management,
    target_management,
    browser_cdp_management,
    dom_snapshot_management,
]

for _mod in _tool_modules:
    _registered = _mod.register(mcp, section_tool, _deps)
    if isinstance(_registered, dict):
        globals().update(_registered)


# MCP Resources
@mcp.resource("browser://{instance_id}/state")
async def get_browser_state_resource(instance_id: str) -> str:
    """Get current state of a browser instance."""
    guard = await check_pending_login_guard(instance_id)
    if guard:
        return guard
    state = await browser_manager.get_page_state(instance_id)
    if state:
        return json.dumps(state.model_dump(mode="json"), indent=2)
    return json.dumps({"error": "Instance not found"})


@mcp.resource("browser://{instance_id}/cookies")
async def get_cookies_resource(instance_id: str) -> str:
    """Get cookies for a browser instance."""
    guard = await check_pending_login_guard(instance_id)
    if guard:
        return guard
    tab = await browser_manager.get_tab(instance_id)
    if tab:
        cookies = await network_interceptor.get_cookies(tab)
        return json.dumps(cookies, indent=2)
    return json.dumps({"error": "Instance not found"})


@mcp.resource("browser://{instance_id}/network")
async def get_network_resource(instance_id: str) -> str:
    """Get network requests for a browser instance."""
    guard = await check_pending_login_guard(instance_id)
    if guard:
        return guard
    requests = await network_interceptor.list_requests(instance_id)
    return json.dumps([req.model_dump(mode="json") for req in requests], indent=2)


@mcp.resource("browser://{instance_id}/console")
async def get_console_resource(instance_id: str) -> str:
    """Get console logs for a browser instance."""
    guard = await check_pending_login_guard(instance_id)
    if guard:
        return guard
    state = await browser_manager.get_page_state(instance_id)
    if state:
        return json.dumps(state.console_logs, indent=2)
    return json.dumps({"error": "Instance not found"})


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stealth Browser MCP Server with 92 tools")
    parser.add_argument(
        "--transport", choices=["stdio", "http"], default="stdio", help="Transport protocol to use"
    )
    parser.add_argument(
        "--port", type=int, default=int(os.getenv("PORT", 8000)), help="Port for HTTP transport"
    )
    parser.add_argument(
        "--host",
        # MCP HTTP transport must bind all interfaces in container deployments.
        default="0.0.0.0",  # nosec B104
        help="Host for HTTP transport",
    )
    parser.add_argument(
        "--disable-browser-management",
        action="store_true",
        help="Disable browser management tools (spawn, navigate, close, etc.)",
    )
    parser.add_argument(
        "--disable-element-interaction",
        action="store_true",
        help="Disable element interaction tools (click, type, scroll, etc.)",
    )
    parser.add_argument(
        "--disable-element-extraction",
        action="store_true",
        help="Disable element extraction tools (styles, structure, events, etc.)",
    )
    parser.add_argument(
        "--disable-file-extraction", action="store_true", help="Disable file-based extraction tools"
    )
    parser.add_argument(
        "--disable-network-debugging",
        action="store_true",
        help="Disable network debugging and interception tools",
    )
    parser.add_argument(
        "--disable-cdp-functions", action="store_true", help="Disable CDP function execution tools"
    )
    parser.add_argument(
        "--disable-progressive-cloning",
        action="store_true",
        help="Disable progressive element cloning tools",
    )
    parser.add_argument(
        "--disable-cookies-storage",
        action="store_true",
        help="Disable cookie and storage management tools",
    )
    parser.add_argument("--disable-tabs", action="store_true", help="Disable tab management tools")
    parser.add_argument(
        "--disable-debugging", action="store_true", help="Disable debug and system tools"
    )
    parser.add_argument(
        "--disable-dynamic-hooks", action="store_true", help="Disable dynamic network hook system"
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Enable only core browser management and element interaction (disable everything else)",
    )
    parser.add_argument(
        "--list-sections", action="store_true", help="List all available tool sections and exit"
    )

    args = parser.parse_args()

    if args.list_sections:
        print("Available tool sections:")
        print("  browser-management: Core browser operations (10 tools)")
        print("  element-interaction: Page interaction and element manipulation (11 tools)")
        print("  element-extraction: Element cloning and extraction (9 tools)")
        print("  file-extraction: File-based extraction tools (9 tools)")
        print("  network-debugging: Network monitoring and interception (5 tools)")
        print("  cdp-functions: Chrome DevTools Protocol function execution (13 tools)")
        print("  progressive-cloning: Advanced element cloning system (10 tools)")
        print("  cookies-storage: Cookie and storage management (3 tools)")
        print("  tabs: Tab management (5 tools)")
        print("  debugging: Debug and system tools (7 tools)")
        print("  dynamic-hooks: AI-powered network hook system (10 tools)")
        print("\nUse --disable-<section-name> to disable specific sections")
        print("Use --minimal to enable only core functionality")
        sys.exit(0)

    if args.minimal:
        DISABLED_SECTIONS.update(
            [
                "element-extraction",
                "file-extraction",
                "network-debugging",
                "cdp-functions",
                "progressive-cloning",
                "cookies-storage",
                "tabs",
                "debugging",
                "dynamic-hooks",
            ]
        )

    if args.disable_browser_management:
        DISABLED_SECTIONS.add("browser-management")
    if args.disable_element_interaction:
        DISABLED_SECTIONS.add("element-interaction")
    if args.disable_element_extraction:
        DISABLED_SECTIONS.add("element-extraction")
    if args.disable_file_extraction:
        DISABLED_SECTIONS.add("file-extraction")
    if args.disable_network_debugging:
        DISABLED_SECTIONS.add("network-debugging")
    if args.disable_cdp_functions:
        DISABLED_SECTIONS.add("cdp-functions")
    if args.disable_progressive_cloning:
        DISABLED_SECTIONS.add("progressive-cloning")
    if args.disable_cookies_storage:
        DISABLED_SECTIONS.add("cookies-storage")
    if args.disable_tabs:
        DISABLED_SECTIONS.add("tabs")
    if args.disable_debugging:
        DISABLED_SECTIONS.add("debugging")
    if args.disable_dynamic_hooks:
        DISABLED_SECTIONS.add("dynamic-hooks")

    if DISABLED_SECTIONS:
        print(f"Disabled tool sections: {', '.join(sorted(DISABLED_SECTIONS))}", file=sys.stderr)

    if args.transport == "http":
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")
