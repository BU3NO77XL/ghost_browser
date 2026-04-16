"""CDP Advanced tools — Performance, Emulation, Accessibility, Console, DOM inspection, PDF."""

import asyncio
from typing import Any, Dict, List, Optional

from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    # ── helpers ───────────────────────────────────────────────────────────────

    async def _tab(instance_id):
        return await browser_manager.get_tab(instance_id)

    async def _send(tab, method, **params):
        """Send raw CDP command via nodriver."""
        return await tab.send(tab.browser.connection.send(method, **params))

    async def _eval(tab, js):
        return await tab.evaluate(js)

    # ── PERFORMANCE ───────────────────────────────────────────────────────────

    @section_tool("cdp-advanced")
    async def get_performance_metrics(instance_id: str) -> Dict[str, Any]:
        """
        Get runtime performance metrics via CDP Performance domain.
        Returns JS heap size, DOM nodes count, layout count, FPS estimate and more.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Dict[str, Any]: Performance metrics dictionary.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}
        try:
            # Enable Performance domain then get metrics
            await tab.send(tab.browser.connection.send("Performance.enable"))
            result = await tab.send(tab.browser.connection.send("Performance.getMetrics"))
            metrics = {}
            for m in result.get("metrics", []):
                metrics[m["name"]] = m["value"]

            # Enrich with JS-side timing
            timing = await tab.evaluate("""
                (function() {
                    var t = performance.timing;
                    var nav = performance.getEntriesByType('navigation')[0] || {};
                    return {
                        dom_content_loaded: t.domContentLoadedEventEnd - t.navigationStart,
                        load_event: t.loadEventEnd - t.navigationStart,
                        first_byte: t.responseStart - t.navigationStart,
                        dom_interactive: t.domInteractive - t.navigationStart,
                        transfer_size: nav.transferSize || 0,
                        encoded_body_size: nav.encodedBodySize || 0,
                    };
                })()
            """)
            if isinstance(timing, dict):
                metrics.update(timing)

            return {"success": True, "metrics": metrics}
        except Exception as e:
            return {"error": str(e)}

    @section_tool("cdp-advanced")
    async def get_page_vitals(instance_id: str) -> Dict[str, Any]:
        """
        Get Core Web Vitals: LCP, FID, CLS, FCP, TTFB via PerformanceObserver.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Dict[str, Any]: Web Vitals values.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}
        try:
            vitals = await tab.evaluate("""
                (function() {
                    var result = {};
                    // FCP
                    var fcp = performance.getEntriesByName('first-contentful-paint');
                    if (fcp.length) result.fcp_ms = Math.round(fcp[0].startTime);
                    // LCP (last entry)
                    var lcp = performance.getEntriesByType('largest-contentful-paint');
                    if (lcp.length) result.lcp_ms = Math.round(lcp[lcp.length-1].startTime);
                    // Navigation timing
                    var nav = performance.getEntriesByType('navigation')[0];
                    if (nav) {
                        result.ttfb_ms = Math.round(nav.responseStart);
                        result.dom_complete_ms = Math.round(nav.domComplete);
                        result.load_ms = Math.round(nav.loadEventEnd);
                        result.transfer_size_bytes = nav.transferSize || 0;
                    }
                    // Resource count
                    result.resource_count = performance.getEntriesByType('resource').length;
                    // Memory (Chrome only)
                    if (performance.memory) {
                        result.js_heap_used_mb = Math.round(performance.memory.usedJSHeapSize / 1048576 * 10) / 10;
                        result.js_heap_total_mb = Math.round(performance.memory.totalJSHeapSize / 1048576 * 10) / 10;
                    }
                    return result;
                })()
            """)
            return {"success": True, "vitals": vitals if isinstance(vitals, dict) else {}}
        except Exception as e:
            return {"error": str(e)}

    # ── EMULATION ─────────────────────────────────────────────────────────────

    @section_tool("cdp-advanced")
    async def emulate_device(
        instance_id: str,
        device: str = "iPhone 14",
        width: int = None,
        height: int = None,
        device_scale_factor: float = None,
        mobile: bool = None,
        user_agent: str = None,
    ) -> Dict[str, Any]:
        """
        Emulate a mobile device or custom viewport via CDP Emulation domain.
        Presets: 'iPhone 14', 'Pixel 7', 'iPad', 'Galaxy S23', 'desktop'.

        Args:
            instance_id (str): Browser instance ID.
            device (str): Device preset name or 'custom'.
            width (int): Custom viewport width (overrides preset).
            height (int): Custom viewport height (overrides preset).
            device_scale_factor (float): Custom device pixel ratio.
            mobile (bool): Whether to emulate mobile.
            user_agent (str): Custom user agent string.

        Returns:
            Dict[str, Any]: Emulation result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}

        presets = {
            "iPhone 14": {
                "width": 390,
                "height": 844,
                "dsf": 3.0,
                "mobile": True,
                "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            },
            "Pixel 7": {
                "width": 412,
                "height": 915,
                "dsf": 2.625,
                "mobile": True,
                "ua": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36",
            },
            "iPad": {
                "width": 820,
                "height": 1180,
                "dsf": 2.0,
                "mobile": True,
                "ua": "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            },
            "Galaxy S23": {
                "width": 360,
                "height": 780,
                "dsf": 3.0,
                "mobile": True,
                "ua": "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36",
            },
            "desktop": {"width": 1920, "height": 1080, "dsf": 1.0, "mobile": False, "ua": None},
        }

        preset = presets.get(device, presets["desktop"])
        w = width or preset["width"]
        h = height or preset["height"]
        dsf = device_scale_factor or preset["dsf"]
        mob = mobile if mobile is not None else preset["mobile"]
        ua = user_agent or preset["ua"]

        try:
            await tab.send(
                tab.browser.connection.send(
                    "Emulation.setDeviceMetricsOverride",
                    width=w,
                    height=h,
                    deviceScaleFactor=dsf,
                    mobile=mob,
                )
            )
            if ua:
                await tab.send(
                    tab.browser.connection.send(
                        "Emulation.setUserAgentOverride",
                        userAgent=ua,
                    )
                )
            return {
                "success": True,
                "device": device,
                "viewport": {"width": w, "height": h},
                "device_scale_factor": dsf,
                "mobile": mob,
                "user_agent_set": bool(ua),
            }
        except Exception as e:
            return {"error": str(e)}

    @section_tool("cdp-advanced")
    async def emulate_geolocation(
        instance_id: str,
        latitude: float,
        longitude: float,
        accuracy: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Override geolocation via CDP Emulation domain.

        Args:
            instance_id (str): Browser instance ID.
            latitude (float): Latitude (-90 to 90).
            longitude (float): Longitude (-180 to 180).
            accuracy (float): Accuracy in meters.

        Returns:
            Dict[str, Any]: Result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}
        try:
            await tab.send(
                tab.browser.connection.send(
                    "Emulation.setGeolocationOverride",
                    latitude=latitude,
                    longitude=longitude,
                    accuracy=accuracy,
                )
            )
            return {
                "success": True,
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy,
            }
        except Exception as e:
            return {"error": str(e)}

    @section_tool("cdp-advanced")
    async def emulate_color_scheme(
        instance_id: str,
        scheme: str = "dark",
    ) -> Dict[str, Any]:
        """
        Emulate prefers-color-scheme media feature (dark/light).

        Args:
            instance_id (str): Browser instance ID.
            scheme (str): 'dark' or 'light'.

        Returns:
            Dict[str, Any]: Result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}
        try:
            await tab.send(
                tab.browser.connection.send(
                    "Emulation.setEmulatedMedia",
                    features=[{"name": "prefers-color-scheme", "value": scheme}],
                )
            )
            return {"success": True, "scheme": scheme}
        except Exception as e:
            return {"error": str(e)}

    @section_tool("cdp-advanced")
    async def emulate_network_conditions(
        instance_id: str,
        preset: str = "3G",
        download_throughput: int = None,
        upload_throughput: int = None,
        latency: int = None,
    ) -> Dict[str, Any]:
        """
        Throttle network speed via CDP Network domain.
        Presets: 'offline', '2G', '3G', '4G', 'fast3G', 'wifi', 'none'.

        Args:
            instance_id (str): Browser instance ID.
            preset (str): Network preset name.
            download_throughput (int): Custom download in bytes/s.
            upload_throughput (int): Custom upload in bytes/s.
            latency (int): Custom latency in ms.

        Returns:
            Dict[str, Any]: Result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}

        # bytes/s values
        presets = {
            "offline": {"dl": 0, "ul": 0, "lat": 0, "offline": True},
            "2G": {"dl": 50000, "ul": 20000, "lat": 300, "offline": False},
            "3G": {"dl": 375000, "ul": 125000, "lat": 100, "offline": False},
            "fast3G": {"dl": 1500000, "ul": 750000, "lat": 40, "offline": False},
            "4G": {"dl": 4000000, "ul": 3000000, "lat": 20, "offline": False},
            "wifi": {"dl": 30000000, "ul": 15000000, "lat": 2, "offline": False},
            "none": {"dl": -1, "ul": -1, "lat": 0, "offline": False},
        }
        p = presets.get(preset, presets["3G"])
        dl = download_throughput if download_throughput is not None else p["dl"]
        ul = upload_throughput if upload_throughput is not None else p["ul"]
        lat = latency if latency is not None else p["lat"]

        try:
            await tab.send(
                tab.browser.connection.send(
                    "Network.emulateNetworkConditions",
                    offline=p.get("offline", False),
                    downloadThroughput=dl,
                    uploadThroughput=ul,
                    latency=lat,
                )
            )
            return {
                "success": True,
                "preset": preset,
                "download_kbps": round(dl / 1000, 1) if dl > 0 else 0,
                "upload_kbps": round(ul / 1000, 1) if ul > 0 else 0,
                "latency_ms": lat,
            }
        except Exception as e:
            return {"error": str(e)}

    # ── ACCESSIBILITY ─────────────────────────────────────────────────────────

    @section_tool("cdp-advanced")
    async def get_accessibility_tree(
        instance_id: str,
        selector: str = None,
        depth: int = 4,
    ) -> Dict[str, Any]:
        """
        Get the accessibility tree (AXTree) for the page or a specific element.
        Useful for testing screen reader compatibility and ARIA attributes.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector to scope the tree (None = full page).
            depth (int): Max depth to traverse.

        Returns:
            Dict[str, Any]: Accessibility tree nodes.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}
        try:
            await tab.send(tab.browser.connection.send("Accessibility.enable"))

            if selector:
                # Get node ID for selector first
                doc = await tab.send(tab.browser.connection.send("DOM.getDocument", depth=0))
                root_id = doc.get("root", {}).get("nodeId", 1)
                node = await tab.send(
                    tab.browser.connection.send(
                        "DOM.querySelector", nodeId=root_id, selector=selector
                    )
                )
                node_id = node.get("nodeId")
                if node_id:
                    result = await tab.send(
                        tab.browser.connection.send(
                            "Accessibility.getPartialAXTree",
                            nodeId=node_id,
                            fetchRelatives=True,
                        )
                    )
                else:
                    return {"error": f"Selector not found: {selector}"}
            else:
                result = await tab.send(
                    tab.browser.connection.send(
                        "Accessibility.getFullAXTree",
                        depth=depth,
                    )
                )

            nodes = result.get("nodes", [])

            def _clean(node):
                out = {"role": node.get("role", {}).get("value", ""), "name": ""}
                name_val = node.get("name", {})
                if isinstance(name_val, dict):
                    out["name"] = name_val.get("value", "")
                props = {}
                for p in node.get("properties", []):
                    props[p.get("name", "")] = p.get("value", {}).get("value")
                if props:
                    out["properties"] = props
                children = node.get("childIds", [])
                if children:
                    out["child_count"] = len(children)
                return out

            cleaned = [_clean(n) for n in nodes[:200]]  # cap at 200 nodes
            return {
                "success": True,
                "node_count": len(nodes),
                "nodes": cleaned,
                "selector": selector,
            }
        except Exception as e:
            return {"error": str(e)}

    # ── CONSOLE ───────────────────────────────────────────────────────────────

    @section_tool("cdp-advanced")
    async def get_console_logs(
        instance_id: str,
        level: str = "all",
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Capture browser console logs (errors, warnings, info, log) via CDP Log domain.

        Args:
            instance_id (str): Browser instance ID.
            level (str): Filter by level: 'all', 'error', 'warning', 'info', 'log'.
            limit (int): Max number of entries to return.

        Returns:
            Dict[str, Any]: Console log entries.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}
        try:
            # Use JS to get console history injected via override
            logs = await tab.evaluate("""
                (function() {
                    if (!window.__ghost_console_logs__) return [];
                    return window.__ghost_console_logs__;
                })()
            """)
            if not isinstance(logs, list):
                logs = []

            if level != "all":
                logs = [l for l in logs if l.get("level") == level]

            return {
                "success": True,
                "count": len(logs),
                "level_filter": level,
                "logs": logs[:limit],
            }
        except Exception as e:
            return {"error": str(e)}

    @section_tool("cdp-advanced")
    async def inject_console_capture(instance_id: str) -> Dict[str, Any]:
        """
        Inject console capture script into the page.
        Must be called before navigating to capture logs from page load.
        After injection, use get_console_logs() to retrieve captured entries.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Dict[str, Any]: Injection result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}
        try:
            await tab.evaluate("""
                (function() {
                    window.__ghost_console_logs__ = [];
                    var levels = ['log', 'info', 'warn', 'error', 'debug'];
                    levels.forEach(function(level) {
                        var orig = console[level].bind(console);
                        console[level] = function() {
                            var args = Array.from(arguments).map(function(a) {
                                try { return typeof a === 'object' ? JSON.stringify(a) : String(a); }
                                catch(e) { return String(a); }
                            });
                            window.__ghost_console_logs__.push({
                                level: level === 'warn' ? 'warning' : level,
                                message: args.join(' '),
                                timestamp: new Date().toISOString(),
                            });
                            orig.apply(console, arguments);
                        };
                    });
                    // Capture unhandled errors
                    window.addEventListener('error', function(e) {
                        window.__ghost_console_logs__.push({
                            level: 'error',
                            message: e.message + ' (' + e.filename + ':' + e.lineno + ')',
                            timestamp: new Date().toISOString(),
                        });
                    });
                })()
            """)
            return {
                "success": True,
                "message": "Console capture injected. Use get_console_logs() to retrieve.",
            }
        except Exception as e:
            return {"error": str(e)}

    # ── DOM INSPECTION ────────────────────────────────────────────────────────

    @section_tool("cdp-advanced")
    async def get_dom_node_info(
        instance_id: str,
        selector: str,
    ) -> Dict[str, Any]:
        """
        Get detailed CDP DOM node information for an element: nodeId, attributes,
        bounding box, computed styles summary, and ARIA info.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector.

        Returns:
            Dict[str, Any]: Node details.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}
        try:
            info = await tab.evaluate(f"""
                (function() {{
                    var el = document.querySelector({repr(selector)});
                    if (!el) return null;
                    var rect = el.getBoundingClientRect();
                    var cs = window.getComputedStyle(el);
                    return {{
                        tag: el.tagName.toLowerCase(),
                        id: el.id || null,
                        class_list: Array.from(el.classList),
                        attributes: (function() {{
                            var attrs = {{}};
                            for (var i = 0; i < el.attributes.length; i++) {{
                                attrs[el.attributes[i].name] = el.attributes[i].value;
                            }}
                            return attrs;
                        }})(),
                        bounding_box: {{
                            x: Math.round(rect.x), y: Math.round(rect.y),
                            width: Math.round(rect.width), height: Math.round(rect.height),
                            top: Math.round(rect.top), right: Math.round(rect.right),
                            bottom: Math.round(rect.bottom), left: Math.round(rect.left),
                        }},
                        computed: {{
                            display: cs.display,
                            visibility: cs.visibility,
                            opacity: cs.opacity,
                            position: cs.position,
                            z_index: cs.zIndex,
                            color: cs.color,
                            background: cs.backgroundColor,
                            font_size: cs.fontSize,
                            font_weight: cs.fontWeight,
                        }},
                        aria: {{
                            role: el.getAttribute('role'),
                            label: el.getAttribute('aria-label'),
                            hidden: el.getAttribute('aria-hidden'),
                            expanded: el.getAttribute('aria-expanded'),
                        }},
                        text_content: el.textContent.trim().slice(0, 200),
                        inner_html_length: el.innerHTML.length,
                        child_count: el.children.length,
                        is_visible: rect.width > 0 && rect.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none',
                    }};
                }})()
            """)
            if info is None:
                return {"error": f"Selector not found: {selector}"}
            return {"success": True, "selector": selector, "node": info}
        except Exception as e:
            return {"error": str(e)}

    # ── PDF EXPORT ────────────────────────────────────────────────────────────

    @section_tool("cdp-advanced")
    async def print_to_pdf(
        instance_id: str,
        output_path: str,
        landscape: bool = False,
        print_background: bool = True,
        scale: float = 1.0,
        paper_width: float = 8.5,
        paper_height: float = 11.0,
    ) -> Dict[str, Any]:
        """
        Export the current page as PDF via CDP Page.printToPDF.

        Args:
            instance_id (str): Browser instance ID.
            output_path (str): File path to save the PDF.
            landscape (bool): Landscape orientation.
            print_background (bool): Include background graphics.
            scale (float): Scale factor (0.1 to 2.0).
            paper_width (float): Paper width in inches (default 8.5 = Letter).
            paper_height (float): Paper height in inches (default 11.0 = Letter).

        Returns:
            Dict[str, Any]: Result with file path and size.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}
        try:
            import base64
            from pathlib import Path

            result = await tab.send(
                tab.browser.connection.send(
                    "Page.printToPDF",
                    landscape=landscape,
                    printBackground=print_background,
                    scale=scale,
                    paperWidth=paper_width,
                    paperHeight=paper_height,
                    marginTop=0.4,
                    marginBottom=0.4,
                    marginLeft=0.4,
                    marginRight=0.4,
                )
            )
            data = result.get("data", "")
            pdf_bytes = base64.b64decode(data)
            Path(output_path).write_bytes(pdf_bytes)
            return {
                "success": True,
                "output_path": output_path,
                "size_bytes": len(pdf_bytes),
                "size_kb": round(len(pdf_bytes) / 1024, 1),
            }
        except Exception as e:
            return {"error": str(e)}

    # ── MOUSE EVENTS ──────────────────────────────────────────────────────────

    @section_tool("cdp-advanced")
    async def dispatch_mouse_event(
        instance_id: str,
        event_type: str,
        x: int,
        y: int,
        button: str = "left",
        click_count: int = 1,
    ) -> Dict[str, Any]:
        """
        Dispatch low-level mouse events via CDP Input domain.
        Useful for hover, drag, right-click, double-click.
        event_type: 'mouseMoved', 'mousePressed', 'mouseReleased', 'mouseWheel'.

        Args:
            instance_id (str): Browser instance ID.
            event_type (str): CDP mouse event type.
            x (int): X coordinate.
            y (int): Y coordinate.
            button (str): 'left', 'right', 'middle', 'none'.
            click_count (int): Click count (2 for double-click).

        Returns:
            Dict[str, Any]: Result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}
        try:
            await tab.send(
                tab.browser.connection.send(
                    "Input.dispatchMouseEvent",
                    type=event_type,
                    x=x,
                    y=y,
                    button=button,
                    clickCount=click_count,
                )
            )
            return {"success": True, "event": event_type, "x": x, "y": y}
        except Exception as e:
            return {"error": str(e)}

    @section_tool("cdp-advanced")
    async def hover_element(
        instance_id: str,
        selector: str,
    ) -> Dict[str, Any]:
        """
        Hover over an element by dispatching mouseMoved CDP event to its center.

        Args:
            instance_id (str): Browser instance ID.
            selector (str): CSS selector of the element to hover.

        Returns:
            Dict[str, Any]: Result with element coordinates.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await _tab(instance_id)
        if not tab:
            return {"error": f"Instance not found: {instance_id}"}
        try:
            rect = await tab.evaluate(f"""
                (function() {{
                    var el = document.querySelector({repr(selector)});
                    if (!el) return null;
                    var r = el.getBoundingClientRect();
                    return {{ x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2) }};
                }})()
            """)
            if not rect:
                return {"error": f"Selector not found: {selector}"}
            await tab.send(
                tab.browser.connection.send(
                    "Input.dispatchMouseEvent",
                    type="mouseMoved",
                    x=rect["x"],
                    y=rect["y"],
                    button="none",
                )
            )
            return {"success": True, "selector": selector, "x": rect["x"], "y": rect["y"]}
        except Exception as e:
            return {"error": str(e)}

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
