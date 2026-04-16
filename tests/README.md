GHOST BROWSER TEST ARCHITECTURE
================================

This test suite mirrors the 5-layer architecture documented in docs/COMMUNICATION_FLOW.md

LAYER 1: MCP PROTOCOL (e2e/)
-----------------------------
Tests the complete MCP server interface - the same functions AI agents call.
These are END-TO-END tests that verify the full request/response cycle.

Files:
  - test_final_smoke.py       : Complete AI session simulation (14-step workflow)
  - test_mcp_interface.py     : MCP tool functions from server.py (spawn, navigate, etc.)

What they test:
  - AI Agent → server.py → tools → core → infrastructure (full stack)
  - Login flow with guard blocking
  - Instance lifecycle and recovery
  - WebSocket health and reconnection

LAYER 2: TOOLS LAYER (integration/)
------------------------------------
Tests tool modules that orchestrate core services.
These verify dependency injection and tool-to-core communication.

Files:
  - test_browser_tools.py     : browser_management.py tools
  - test_element_tools.py     : element_interaction.py + element_extraction.py tools
  - test_network_tools.py     : network_debugging.py + cookies_storage.py tools
  - test_navigation_flow.py   : Navigation with cookie injection and login detection
  - test_login_flow.py        : Manual login handler + watcher integration

What they test:
  - tools/ modules using injected dependencies
  - Multi-service orchestration (e.g., navigate uses browser_manager + cookie_manager + login_handler)
  - Tool-level error handling and state management

LAYER 3: CORE SERVICES (unit/)
-------------------------------
Tests business logic modules in isolation.
These verify core service behavior without browser or MCP layer.

Files:
  - test_core_modules.py      : models, platform_utils, process_cleanup, response_handler
  - test_login_guard.py       : login_guard blocking mechanism
  - test_persistence.py       : persistent_storage and instance recovery
  - test_race_conditions.py   : Concurrency and thread safety

What they test:
  - Core service logic in isolation
  - Singleton behavior
  - State management
  - Concurrency safety

LAYER 4: INFRASTRUCTURE (unit/)
--------------------------------
Tests low-level utilities and storage.
Already covered in test_core_modules.py:
  - persistent_storage
  - process_cleanup
  - platform_utils
  - debug_logger
  - models (Pydantic)

REMOVED FILES
-------------
  - test_uncovered_tools.py   : Merged into test_network_tools.py (cookie helpers)
  - demo_visual.py            : Moved to examples/ (not a test)
  - test_cdp_attributes.py    : Merged into test_element_tools.py
  - test_javascript.py        : Merged into test_browser_tools.py (execute_script)
  - test_cookies.py           : Merged into test_network_tools.py
  - test_instance_recovery.py : Merged into test_persistence.py
  - test_element_cloners.py   : Merged into test_element_tools.py

TEST EXECUTION ORDER
--------------------
1. Unit tests (fast, no browser)
2. Integration tests (browser required, isolated features)
3. E2E tests (full workflow simulation)

RUN COMMANDS
------------
All tests:           uv run python -m pytest tests/
Unit only:           uv run python -m pytest tests/unit/
Integration only:    uv run python -m pytest tests/integration/
E2E only:            uv run python -m pytest tests/e2e/
Specific test:       uv run python -m pytest tests/e2e/test_final_smoke.py -v

ARCHITECTURE ALIGNMENT
----------------------
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: AI Agent → MCP Protocol                                │
│ Tests:   tests/e2e/test_mcp_interface.py                        │
│          tests/e2e/test_final_smoke.py                           │
└─────────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────────┐
│ Layer 2: server.py (FastMCP + Dependency Injection)             │
│ Tests:   tests/e2e/* (implicitly tests server.py)               │
└─────────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────────┐
│ Layer 3: tools/ (11 modules)                                    │
│ Tests:   tests/integration/test_browser_tools.py                │
│          tests/integration/test_element_tools.py                 │
│          tests/integration/test_network_tools.py                 │
│          tests/integration/test_navigation_flow.py               │
│          tests/integration/test_login_flow.py                    │
└─────────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────────┐
│ Layer 4: Core Services (browser_manager, dom_handler, etc.)     │
│ Tests:   tests/unit/test_core_modules.py                        │
│          tests/unit/test_login_guard.py                          │
│          tests/unit/test_persistence.py                          │
│          tests/unit/test_race_conditions.py                      │
└─────────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────────┐
│ Layer 5: Infrastructure (storage, logging, utils)               │
│ Tests:   tests/unit/test_core_modules.py (covers all)           │
└─────────────────────────────────────────────────────────────────┘

PRINCIPLES
----------
1. Tests mirror architecture layers
2. Each test file has clear responsibility
3. No redundant tests - each feature tested once at appropriate layer
4. Fast unit tests run first, slow e2e tests run last
5. Integration tests verify orchestration, not individual services
6. E2E tests simulate real AI agent workflows
