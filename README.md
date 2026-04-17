<div align="center">
<img src="docs/media/UndetectedStealthBrowser.png" alt="Ghost Browser MCP" width="200"/>

# Ghost Browser MCP

**Undetectable browser automation for MCP-compatible AI agents.**

**Improved fork of [Stealth Browser MCP](https://github.com/vibheksoni/stealth-browser-mcp) adapted as Ghost Browser MCP.**

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
- [Features](#features)
- [Quickstart](#quickstart)
- [Docker Runtime](#docker-runtime)
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

## Features

- **Antibot bypass** — Works on Cloudflare, Queue-It, and other protection systems that block traditional automation
- **225 tools across 32 sections** — From basic navigation to advanced CDP function execution
- **Modular loading** — Run the full tool suite or a minimal 23-tool core; disable what you don't need
- **Pixel-accurate element cloning** — Extract complete elements with all CSS, DOM structure, events, and assets via CDP
- **Network interception** — Inspect every request, response, header, and payload through your AI agent
- **Dynamic hook system** — AI-generated Python functions that intercept and modify network traffic in real-time
- **Instant text input** — Paste large content via CDP or type with human-like keystrokes and newline support
- **Cross-platform** — Windows, macOS, Linux, Docker, and CI/CD pipelines with automatic environment detection
- **Browser support** — Chrome, Chromium, and Microsoft Edge (automatic detection)
- **Clean MCP integration** — No custom brokers or wrappers; works with Claude Code, Claude Desktop, Cursor, and any MCP client

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
git clone <your-fork-url> ghost_browser
cd ghost_browser
uv sync
```

This creates a local `.venv` with the dependencies declared in `pyproject.toml`.

### 3. Add to your MCP client

**Claude Code CLI (recommended):**

Windows:
```bash
claude mcp add-json ghost_browser "{\"type\":\"stdio\",\"command\":\"C:\\path\\to\\ghost_browser\\.venv\\Scripts\\python.exe\",\"args\":[\"C:\\path\\to\\ghost_browser\\src\\server.py\"],\"env\":{\"PYTHONPATH\":\"C:\\path\\to\\ghost_browser\\src\"}}"
```

Mac/Linux:
```bash
claude mcp add-json ghost_browser '{
  "type": "stdio",
  "command": "/path/to/ghost_browser/.venv/bin/python",
  "args": ["/path/to/ghost_browser/src/server.py"],
  "env": {"PYTHONPATH": "/path/to/ghost_browser/src"}
}'
```

> Replace `/path/to/ghost_browser/` with your actual project path.

<details>
<summary><strong>Manual JSON configuration (Claude Desktop, Cursor, Kiro, etc.)</strong></summary>

Windows (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "ghost_browser": {
      "type": "stdio",
      "command": "C:\\path\\to\\ghost_browser\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\ghost_browser\\src\\server.py"],
      "env": {
        "PYTHONPATH": "C:\\path\\to\\ghost_browser\\src"
      }
    }
  }
}
```

Mac/Linux (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "ghost_browser": {
      "type": "stdio",
      "command": "/path/to/ghost_browser/.venv/bin/python",
      "args": ["/path/to/ghost_browser/src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/ghost_browser/src"
      }
    }
  }
}
```

> Replace `/path/to/ghost_browser/` with your actual project path.

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

> "Use ghost_browser to navigate to https://example.com and take a screenshot."

---

## Docker Runtime

Run Ghost Browser with MCP HTTP transport and a remote Chromium viewer:

```bash
docker compose up -d --build
```

Default endpoints:

| Service | URL |
|---------|-----|
| MCP HTTP | `http://localhost:8000/mcp` |
| noVNC browser viewer | `http://localhost:6080/vnc.html` |

For a VPS or reverse proxy, set the public noVNC URL so manual-login responses can be
forwarded to users:

```bash
GHOST_REMOTE_VIEWER_PUBLIC_URL=https://browser.example.com docker compose up -d
```

Relevant environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `GHOST_ENABLE_NOVNC` | `true` | Starts Xvfb, x11vnc, and noVNC inside the container |
| `GHOST_REMOTE_VIEWER_ENABLED` | `true` in compose | Adds remote login metadata to pending-login responses |
| `GHOST_REMOTE_VIEWER_PUBLIC_URL` | `http://localhost:6080` | Public URL agents should send to the user |
| `GHOST_REMOTE_VIEWER_TOKEN_SECRET` | `change-me-local-only` | Signs manual-login URLs for downstream gateways |
| `GHOST_REMOTE_VIEWER_TOKEN_TTL_SECONDS` | `900` | Expiration window for generated login URLs |

The compose file binds noVNC to `127.0.0.1:6080` by default. On a VPS, expose it through
HTTPS with a reverse proxy and authentication; do not publish the raw VNC port.

---

## Modular Architecture

Choose exactly what functionality you need. Run the full tool suite or strip it down to 23 core tools.

| Mode | Tools | Use Case |
|------|-------|----------|
| **Full** (default) | 225 | Complete browser automation and debugging |
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
| `cdp-functions` | 13 | Chrome DevTools Protocol execution |
| `progressive-cloning` | 10 | Advanced element cloning |
| `cookies-storage` | 3 | Cookie and storage management |
| `tabs` | 5 | Tab management |
| `debugging` | 7 | Debug and system tools |
| `dynamic-hooks` | 10 | AI-powered network hooks |
| `log-management` | 5 | CDP Log domain — console logs and violations |
| `storage-cdp-management` | 4 | Origin data clearing and quota |
| `system-info-management` | 4 | GPU, process, and feature flag info |
| `fetch-management` | 7 | Granular request interception |
| `overlay-management` | 8 | Element highlighting and visual overlays |
| `audits-management` | 4 | Lighthouse-style audits and contrast checks |
| `target-management` | 7 | Advanced tab, worker, and iframe management |
| `browser-cdp-management` | 6 | Window management, permissions, downloads |
| `dom-snapshot-management` | 3 | Full DOM snapshot with computed styles |

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
| `hot_reload()` | Reload modules without restart |
| `reload_status()` | Check module reload status |

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

</details>

<details>
<summary><strong>Element Extraction (CDP-accurate)</strong></summary>

| Tool | Description |
|------|-------------|
| `extract_complete_element_cdp()` | Complete CDP-based element clone |
| `clone_element_complete()` | Complete element cloning |
| `extract_complete_element_to_file()` | Save complete extraction to file |
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
| `clone_element_to_file()` | Save complete clone to file |
| `list_clone_files()` | List saved clone files |
| `cleanup_clone_files()` | Clean up old clone files |

</details>

<details>
<summary><strong>Network Debugging and Interception</strong></summary>

| Tool | Description |
|------|-------------|
| `list_network_requests()` | List captured network requests |
| `get_request_details()` | Inspect headers and payload for a request |
| `get_response_content()` | Get response data from a request |
| `modify_headers()` | Add custom headers to requests |
| `spawn_browser(block_resources=[...])` | Block tracking scripts, ads, etc. |
| `create_dynamic_hook()` | Create Python functions to intercept/modify requests |
| `create_simple_dynamic_hook()` | Quick hook creation with presets |
| `list_dynamic_hooks()` | List active hooks with statistics |
| `get_dynamic_hook_details()` | Inspect hook source code |
| `remove_dynamic_hook()` | Remove a hook |
| `get_hook_documentation()` | Request object structure and HookAction types |
| `get_hook_examples()` | 10 detailed examples: blockers, redirects, proxies |
| `get_hook_requirements_documentation()` | Pattern matching and best practices |
| `get_hook_common_patterns()` | Ad blocking, API proxying, auth injection |
| `validate_hook_function()` | Validate hook code before deployment |

</details>

<details>
<summary><strong>CDP Function Execution</strong></summary>

| Tool | Description |
|------|-------------|
| `execute_cdp_command()` | Direct CDP commands (use snake_case) |
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
| `get_instance_state()` | localStorage and sessionStorage snapshot |
| `execute_script()` | Read/modify storage via JS |

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
<summary><strong>Page Analysis and Debugging</strong></summary>

| Tool | Description |
|------|-------------|
| `take_screenshot()` | Capture screenshots |
| `get_page_content()` | HTML and metadata |
| `get_debug_view()` | Debug info with pagination |
| `clear_debug_view()` | Clear debug logs |
| `export_debug_logs()` | Export logs (JSON/pickle/gzip) |
| `get_debug_lock_status()` | Debug lock status |
| `validate_browser_environment_tool()` | Diagnose platform issues and browser compatibility |

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
| Total tools | 225 (customizable) | ~20 |

Tested on: LinkedIn, Instagram, Twitter/X, Amazon, banking portals, government sites, Cloudflare-protected APIs, Nike SNKRS, Ticketmaster, Supreme.

---

## Troubleshooting

**No compatible browser found**
Install Chrome, Chromium, or Microsoft Edge. The server auto-detects the first available browser. Run `validate_browser_environment_tool()` to diagnose.

**Tools hang or return malformed JSON**
This fork includes the upstream fix for stdout corruption from [#8](https://github.com/vibheksoni/stealth-browser-mcp/issues/8). Re-sync the environment if you are updating an older checkout.

**Browser crashes on Linux / Docker / CI**
Run with `--sandbox=false` or ensure your environment supports sandboxing. The server auto-detects root and container environments and adjusts accordingly.

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

Prompt templates: [docs/examples/claude_prompts.md](docs/examples/claude_prompts.md)
Cookie template: [docs/examples/cookies_example.txt](docs/examples/cookies_example.txt)

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
