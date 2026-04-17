<div align="center">
<img src="docs/media/UndetectedStealthBrowser.png" alt="Ghost Browser MCP" width="200"/>

# Ghost Browser MCP

**Undetectable browser automation for MCP-compatible AI agents.**

**Improved fork of [Stealth Browser MCP](https://github.com/vibheksoni/stealth-browser-mcp) adapted as Ghost Browser MCP.**

Ghost Browser MCP turns a real browser into a full MCP-native research, extraction, and page-reconstruction toolkit. It combines 225 browser tools, Chrome DevTools Protocol access, network inspection, asset downloading, and pixel-accurate page cloning in one agent-ready server.

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
- [Development vs Quick Reproduction](#development-vs-quick-reproduction)
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

## What Ghost Adds

Ghost Browser MCP is more than a browser controller. It is a practical reverse-engineering and reconstruction toolkit for authorized web analysis:

- **225 MCP tools** — Navigation, screenshots, DOM extraction, CDP commands, network tracing, downloads, sessions, hooks, and page-state inspection.
- **Pixel-accurate cloning** — Extract page structure, styles, computed layout, screenshots, and loaded assets to recreate pages in minutes.
- **Asset-aware extraction** — Download the images, icons, fonts, CSS, and media actually loaded by the current page instead of collecting unrelated noise.
- **Deep page intelligence** — Inspect HTML, accessibility data, console logs, network requests, storage, cookies, event listeners, and element relationships.
- **Manual-login handoff** — Let a human complete authentication in a real browser, then return control to the AI agent with the same session.
- **Docker-ready runtime** — Run from source for development or from a published image for fast reproduction on Windows, macOS, Linux, or a VPS.

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

## How It Fits Together

Think of Ghost Browser as three simple pieces:

```text
Your AI agent
  -> talks to Ghost Browser through MCP
  -> Ghost Browser controls Chrome/Chromium
  -> Chrome opens websites, clicks, extracts data, screenshots, assets, and network info
```

The only decision you need to make first is **how Ghost Browser should run**.

If you only remember one thing:

```text
I want to change Ghost Browser code -> use local source mode.
I only want to run Ghost Browser     -> use Docker image mode.
```

| You want to... | Use this mode | MCP connection |
|----------------|---------------|----------------|
| edit the code, add tools, debug internals | Local source mode | `stdio` with local Python paths |
| run it quickly without touching source code | Docker image mode | `http` to `http://localhost:8000/mcp` |
| host it on a VPS for remote agents | Docker image mode + reverse proxy | `http` to `https://mcp.example.com/mcp` |

The words used in this README mean:

- **MCP server**: the tool server that exposes Ghost Browser tools to an AI agent.
- **MCP client**: the app/agent that calls those tools, such as Claude, Cursor, Kiro, OpenClaw, or another MCP-compatible agent.
- **`stdio` mode**: the MCP client starts Ghost Browser by running a local command, usually Python + `src/server.py`.
- **`http` mode**: Ghost Browser is already running somewhere, and the MCP client connects to its URL.
- **Docker**: a packaged runtime that includes Python dependencies, Chrome, Xvfb, and noVNC.
- **noVNC**: a browser-based remote screen so you can see/control Chrome inside Docker.
- **manual login handoff**: when an agent pauses and sends you a noVNC link so you can log in manually.

Docker files in this repository:

| File | Purpose |
|------|---------|
| `Dockerfile` | Image recipe: installs system packages, Chrome, Python dependencies, and the app |
| `docker/entrypoint.sh` | Container startup: starts Xvfb, fluxbox, x11vnc, noVNC, then the MCP server |
| `docker-compose.yml` | Local source build: builds the image from this repository and runs the container |
| `docker-compose.image.yml` | Quick reproduction: runs a published image without needing the source code |

The relationship is:

```text
Dockerfile                = image recipe
docker/entrypoint.sh      = container startup
docker-compose.yml        = local build from source code
docker-compose.image.yml  = quick reproduction with published image
```

So the flow is:

```text
1. Choose local source mode or Docker mode.
2. Start Ghost Browser.
3. Add the matching MCP template to your client.
4. Ask the agent to use ghost_browser_mcp.
5. If login is needed, open the browser/noVNC link, log in, and let the agent continue.
```

---

## Quickstart

This quickstart is for **local source mode**. Use it when you have the repository on your
machine and want the MCP client to start Ghost Browser with `stdio`.

If you want the fastest Docker-only path, skip to [Quick Reproduction Mode](#quick-reproduction-mode).

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

Download the source code and install the Python dependencies:

```bash
git clone https://github.com/BU3NO77XL/Ghost_Browser_MCP.git Ghost_Browser_MCP
cd Ghost_Browser_MCP
uv sync
```

This creates a local `.venv` with the dependencies declared in `pyproject.toml`.

### 3. Add to your MCP client

In local source mode, the MCP client must know where Python and `src/server.py` are located.

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

## Development vs Quick Reproduction

There are two recommended ways to run Ghost Browser. Pick one before copying commands.

```text
Do you want to change the code?
  yes -> Development Mode
  no  -> Quick Reproduction Mode
```

### Development Mode

Use this when you want to edit the source code, run tests, change tools, debug internals, or
contribute patches.

In this mode:

```text
You keep the source code locally.
You install Python dependencies with uv.
Your MCP client usually connects through stdio.
You edit files, run tests, commit changes, and push.
```

```bash
git clone https://github.com/BU3NO77XL/Ghost_Browser_MCP.git Ghost_Browser_MCP
cd Ghost_Browser_MCP
uv sync
uv run black --check src/ tests/ --line-length 100
uv run pytest
```

Run the MCP server from source:

```bash
uv run python src/server.py --transport stdio
```

Or run HTTP transport while developing:

```bash
uv run python src/server.py --transport http --host 0.0.0.0 --port 8000
```

Use development mode when:

- you are changing Python code or JavaScript extractors
- you need fast edit/test cycles
- you want to inspect logs directly from the source tree
- you are adding or removing MCP tools
- you are debugging CI failures

### Quick Reproduction Mode

Use this when you only want to run the latest packaged browser server quickly on a local
machine or VPS, without cloning the source code or installing Python dependencies.

In this mode:

```text
You install Docker Compose.
Docker Compose reads the runtime file from GitHub, or you download that one small file.
Docker pulls the ready-made Ghost Browser image.
Your MCP client connects through HTTP.
You do not need local Python paths.
```

Fastest path, streaming the compose file from GitHub without saving it:

```bash
curl -fsSL https://raw.githubusercontent.com/BU3NO77XL/Ghost_Browser_MCP/main/docker-compose.image.yml | docker compose -f - up -d
```

Windows PowerShell:

```powershell
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/BU3NO77XL/Ghost_Browser_MCP/main/docker-compose.image.yml -UseBasicParsing).Content | docker compose -f - up -d
```

To stop it, stream the same compose file again:

```bash
curl -fsSL https://raw.githubusercontent.com/BU3NO77XL/Ghost_Browser_MCP/main/docker-compose.image.yml | docker compose -f - down
```

Windows PowerShell:

```powershell
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/BU3NO77XL/Ghost_Browser_MCP/main/docker-compose.image.yml -UseBasicParsing).Content | docker compose -f - down
```

Some Docker Compose versions do not handle `-f https://...` URLs consistently across
operating systems. Streaming with `-f -` avoids that path issue. If you prefer to keep the
runtime file locally, use the universal fallback:

```bash
mkdir ghost_browser_mcp_runtime
cd ghost_browser_mcp_runtime
curl -O https://raw.githubusercontent.com/BU3NO77XL/Ghost_Browser_MCP/main/docker-compose.image.yml
docker compose -f docker-compose.image.yml pull
docker compose -f docker-compose.image.yml up -d
```

On Windows PowerShell, the fallback is:

```powershell
mkdir ghost_browser_mcp_runtime
cd ghost_browser_mcp_runtime
Invoke-WebRequest -Uri https://raw.githubusercontent.com/BU3NO77XL/Ghost_Browser_MCP/main/docker-compose.image.yml -OutFile docker-compose.image.yml
docker compose -f docker-compose.image.yml pull
docker compose -f docker-compose.image.yml up -d
```

If you prefer a minimal compose file, use the published image directly:

```yaml
services:
  ghost-browser-mcp:
    image: ghcr.io/bu3no77xl/ghost_browser_mcp:latest
    shm_size: "1gb"
    environment:
      PORT: "8000"
      GHOST_ENABLE_NOVNC: "true"
      GHOST_REMOTE_VIEWER_ENABLED: "true"
      GHOST_REMOTE_VIEWER_PUBLIC_URL: "http://localhost:6080"
      GHOST_REMOTE_VIEWER_TOKEN_SECRET: "change-me-local-only"
    ports:
      - "8000:8000"
      - "127.0.0.1:6080:6080"
    volumes:
      - ghost_browser_mcp_data:/data
    restart: unless-stopped

volumes:
  ghost_browser_mcp_data:
```

Then run:

```bash
docker compose up -d
```

Connect an MCP client to the running Docker service with HTTP transport:

```json
{
  "mcpServers": {
    "ghost_browser_mcp": {
      "type": "http",
      "url": "http://localhost:8000/mcp",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

For a VPS, use the public MCP endpoint exposed by your reverse proxy:

```json
{
  "mcpServers": {
    "ghost_browser_mcp": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

In Docker mode, the MCP client connects to a server that is already running. Do not point the
client at `python`, `.venv`, or `src/server.py`; those paths are only for local source mode.

Use quick reproduction mode when:

- you want the fastest way to test or host Ghost Browser
- you are deploying to a VPS
- you do not want source code on the target machine
- you want reproducible runtime behavior across machines
- you want updates to be as simple as `docker compose pull && docker compose up -d`

### Docker Image Publishing

The CI workflow builds and smoke-tests the Docker image after the existing lint, security,
unit, integration, and E2E jobs pass. On pushes to `main`, it publishes:

```text
ghcr.io/bu3no77xl/ghost_browser_mcp:latest
ghcr.io/bu3no77xl/ghost_browser_mcp:<commit-sha>
```

The Docker job checks:

```text
docker compose config
docker compose -f docker-compose.image.yml config
Docker image build
noVNC HTTP availability
MCP HTTP initialize
tools/list exposes 225 tools
```

For local development before pushing, use local build mode:

```bash
docker compose up -d --build
```

---

## Docker Runtime

Docker is the recommended runtime when you want to run Ghost Browser without managing
Python, Chrome, system libraries, Xvfb, or noVNC directly on the host. The container starts:

- MCP HTTP server on port `8000`
- Chromium/Chrome inside a virtual display (`Xvfb`)
- noVNC browser viewer on port `6080`
- persistent runtime data under the Docker volume `ghost_browser_mcp_data`

This is especially useful for VPS deployments and mobile handoff flows. If an AI agent reaches
a manual login page, Ghost Browser can return a remote noVNC URL; the user opens that URL,
logs in inside the same server-side browser session, and the agent continues with the same
cookies, localStorage, and browser context.

### Install Docker Compose

Docker Compose v2 is included with Docker Desktop on Windows and macOS. On Linux/VPS
servers, install Docker Engine with the Compose plugin.

Windows:

1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Enable the WSL 2 backend when prompted.
3. Open PowerShell and verify:

```powershell
docker --version
docker compose version
```

macOS:

1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Open Terminal and verify:

```bash
docker --version
docker compose version
```

Linux / VPS:

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker "$USER"
newgrp docker
docker --version
docker compose version
```

### Run Locally From Source

Build and start the container:

```bash
docker compose up -d --build
```

To run from a published image instead of building locally, use `docker-compose.image.yml`:

```bash
docker compose -f docker-compose.image.yml pull
docker compose -f docker-compose.image.yml up -d
```

Check status and logs:

```bash
docker compose ps
docker compose logs -f ghost-browser-mcp
```

Default endpoints:

| Service | URL |
|---------|-----|
| MCP HTTP | `http://localhost:8000/mcp` |
| noVNC browser viewer | `http://localhost:6080/vnc.html` |

Open the noVNC URL in your browser to see and control the remote Chromium display.

Stop the runtime:

```bash
docker compose down
```

Reset persistent runtime data:

```bash
docker compose down -v
```

### VPS / Remote Access

On a VPS, set the public noVNC URL so manual-login responses can be forwarded to users:

```bash
GHOST_REMOTE_VIEWER_PUBLIC_URL=https://browser.example.com docker compose up -d --build
```

Use a reverse proxy such as Caddy, Nginx, or Traefik to expose noVNC over HTTPS. Keep the
raw VNC port private; the compose file only exposes noVNC on `127.0.0.1:6080` by default.

Recommended VPS shape:

```text
Internet
  -> HTTPS reverse proxy
  -> 127.0.0.1:6080 noVNC
  -> Chromium inside Docker
```

Do not expose port `5900`. It is the internal VNC port and should stay reachable only inside
the container.

### Manual Login Handoff

When remote viewer metadata is enabled and a login page is detected, tool responses may include:

```json
{
  "login_required": true,
  "manual_login_url": "https://browser.example.com/vnc.html?instance_id=...",
  "remote_browser_access": {
    "type": "novnc",
    "expires_in_seconds": 900
  }
}
```

An agent can send `manual_login_url` to the user over Telegram, chat, email, or any other
channel. The user logs in through noVNC, then the agent calls `confirm_manual_login` with the
same `instance_id`.

### MCP HTTP Headers

`GET http://localhost:8000/mcp` may return `406 Not Acceptable`. That is expected: FastMCP's
HTTP transport requires clients to accept JSON and server-sent events.

Use:

```text
Accept: application/json, text/event-stream
Content-Type: application/json
```

### MCP Client Template for Docker HTTP

Use this template when Ghost Browser is already running through Docker Compose:

```json
{
  "mcpServers": {
    "ghost_browser_mcp": {
      "type": "http",
      "url": "http://localhost:8000/mcp",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

For hosted deployments, replace the URL with the public MCP route:

```json
{
  "mcpServers": {
    "ghost_browser_mcp": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Keep the local source template as `stdio`. Keep the Docker template as `http`.

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PORT` | `8000` | MCP HTTP port inside the container |
| `GHOST_ENABLE_NOVNC` | `true` | Starts Xvfb, x11vnc, and noVNC inside the container |
| `GHOST_REMOTE_VIEWER_ENABLED` | `true` in compose | Adds remote login metadata to pending-login responses |
| `GHOST_REMOTE_VIEWER_PUBLIC_URL` | `http://localhost:6080` | Public URL agents should send to the user |
| `GHOST_REMOTE_VIEWER_TOKEN_SECRET` | `change-me-local-only` | Signs manual-login URLs for downstream gateways |
| `GHOST_REMOTE_VIEWER_TOKEN_TTL_SECONDS` | `900` | Expiration window for generated login URLs |
| `STEALTH_BROWSER_STORAGE_FILE` | `/data/storage/instances.json` | Persistent runtime instance metadata |

### Verified Smoke Test

The Docker runtime was verified with:

```bash
docker compose config
docker compose build
docker compose up -d
docker compose ps
```

The MCP server exposed all `225` tools, `spawn_browser(headless=false)` created a visible
Chromium session in noVNC, `navigate` loaded `https://example.com`, and `take_screenshot`
saved an image under `/data/output`.

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
