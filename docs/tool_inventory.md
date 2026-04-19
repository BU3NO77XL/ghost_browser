# Inventario de ferramentas MCP

Total detectado em `src/tools`: 225 ferramentas em 32 secoes.
Todas ficam habilitadas por padrao. Use `--minimal` para manter apenas o nucleo ou `--disable-<secao>` para podar secoes especificas.

## Resumo por utilidade

### A - Mais uteis / manter primeiro (36 ferramentas)
- `browser-management` (11): Core. Manter. Essencial para criar, navegar, recuperar e fechar browsers.
- `cookies-storage` (3): Core para sessao. Pequeno e valioso para login, cookies e estado.
- `element-interaction` (12): Core. Manter. Essencial para clicar, digitar, consultar DOM, capturar tela e ler pagina.
- `network-debugging` (5): Core para diagnostico. Alto valor para scraping, depuracao e entender chamadas de rede.
- `tabs` (5): Core. Manter. Muito util para fluxos reais com varias abas.

### B - Muito uteis sob demanda (90 ferramentas)
- `browser-cdp-management` (6): Muito util sob demanda. Janelas, permissoes e downloads; importante em automacao mais completa.
- `cdp-advanced` (13): Muito util sob demanda. Performance, emulacao, acessibilidade, PDF e input baixo nivel.
- `cdp-functions` (13): Poderoso, usar com criterio. Execucao JS/CDP generica; flexivel, mas aumenta superficie e escolhas.
- `css-management` (6): Muito util sob demanda. Inspecao/edicao CSS; util para frontend e clonagem visual.
- `debugging` (7): Manter em desenvolvimento. Diagnostico do servidor; pode ser removido em producao enxuta.
- `dom-snapshot-management` (3): Muito util sob demanda. Snapshots completos; muito bom para analise, pesado para uso comum.
- `element-extraction` (9): Muito util sob demanda. Clonagem/extracao detalhada de elementos; alto valor, custo maior.
- `fetch-management` (7): Muito util sob demanda. Intercepcao/modificacao de requests; poderoso, mas nem todo fluxo precisa.
- `storage-management` (15): Muito util sob demanda. Amplo controle de storage; util quando precisa estado persistido.
- `system-info-management` (4): Util leve. Info do servidor/browser/processos; barato e bom para diagnostico.
- `target-management` (7): Muito util sob demanda. Poderoso para targets, workers e iframes, mas duplica parte de abas/browser.

### C - Especializadas / candidatas a disable (75 ferramentas)
- `debugger-management` (9): Especializado. Debugger JS completo; valioso para dev, pesado para automacao simples.
- `dynamic-hooks` (10): Especializado. Hooks dinamicos de rede; poderoso, mas complexo e menos comum.
- `file-extraction` (8): Especializado. Versoes que escrevem em arquivo; util para artefatos grandes, mas duplicativo.
- `log-management` (5): Especializado. Dominio Log/violations; util em auditoria, pouco usado em navegacao comum.
- `overlay-management` (8): Especializado visual. Overlays CDP; util para debug visual, dispensavel em automacao headless.
- `profiler-management` (5): Especializado. CPU profiling e coverage; manter para performance/debug.
- `progressive-cloning` (10): Especializado. Clonagem incremental rica; manter se esse fluxo for frequente.
- `security-management` (3): Sensivel. Certificados/estado de seguranca; pequeno, mas pode enfraquecer seguranca.
- `serviceworker-management` (7): Especializado PWA. Bom para PWAs; desnecessario para navegacao simples.
- `storage-cdp-management` (4): Especializado. Quota e limpeza por origem; bom para debug, menos usado no dia a dia.
- `webauthn-management` (6): Especializado auth. Passkeys/FIDO2 virtual; manter se testa autenticacao moderna.

### D - Menos uteis para uso geral / candidatas fortes a remover (24 ferramentas)
- `animation-management` (6): Baixa utilidade geral. Controle de animacoes; util em testes visuais especificos.
- `audits-management` (4): Baixa utilidade geral. Contraste/respostas codificadas; bom nicho de auditoria.
- `backgroundservice-management` (4): Baixa utilidade geral. Eventos PWA de background; nicho.
- `database-management` (3): Legado/nicho. WebSQL e legado; candidato forte a remover se nao usado.
- `heapprofiler-management` (7): Baixa utilidade geral. Heap snapshots e GC; raro fora de investigacao de memoria.

## Lista completa por secao

### animation-management (6)
Classificacao: D - Baixa utilidade geral.
Criterio: Controle de animacoes; util em testes visuais especificos.

- `get_animation_timing` - Get the current timing information for a specific animation.
- `list_animations` - List all active animations on the current page.
- `pause_animation` - Pause a specific animation by its ID.
- `play_animation` - Resume (play) a paused animation by its ID.
- `seek_animations` - Seek one or more animations to a specific time position.
- `set_animation_playback_rate` - Set the global playback rate for all animations on the page.

### audits-management (4)
Classificacao: D - Baixa utilidade geral.
Criterio: Contraste/respostas codificadas; bom nicho de auditoria.

- `audits_check_contrast` - Trigger a contrast check on the current page.
- `audits_disable` - Disable the Audits domain for a browser instance.
- `audits_enable` - Enable the Audits domain for a browser instance.
- `audits_get_encoded_response` - Get an encoded version of a network response.

### backgroundservice-management (4)
Classificacao: D - Baixa utilidade geral.
Criterio: Eventos PWA de background; nicho.

- `clear_background_service_events` - Clear all recorded background service events for a given service type.
- `get_background_service_events` - Retrieve recorded background service events for a given service type.
- `start_observing_background_service` - Start observing background service events for a given service type.
- `stop_observing_background_service` - Stop observing background service events for a given service type.

### browser-cdp-management (6)
Classificacao: B - Muito util sob demanda.
Criterio: Janelas, permissoes e downloads; importante em automacao mais completa.

- `browser_get_window_bounds` - Get the bounds of a browser window.
- `browser_get_window_for_target` - Get the browser window ID and bounds for the current target.
- `browser_grant_permissions` - Grant browser permissions for an origin.
- `browser_reset_permissions` - Reset all browser permissions, optionally for a specific origin.
- `browser_set_download_behavior` - Set the download behavior for the browser.
- `browser_set_window_bounds` - Set the bounds (position/size/state) of a browser window.

### browser-management (11)
Classificacao: A - Core. Manter.
Criterio: Essencial para criar, navegar, recuperar e fechar browsers.

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
Classificacao: B - Muito util sob demanda.
Criterio: Performance, emulacao, acessibilidade, PDF e input baixo nivel.

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
Classificacao: B - Poderoso, usar com criterio.
Criterio: Execucao JS/CDP generica; flexivel, mas aumenta superficie e escolhas.

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
Classificacao: A - Core para sessao.
Criterio: Pequeno e valioso para login, cookies e estado.

- `clear_cookies` - Clear cookies.
- `get_cookies` - Get cookies for current page or specific URLs.
- `set_cookie` - Set a cookie.

### css-management (6)
Classificacao: B - Muito util sob demanda.
Criterio: Inspecao/edicao CSS; util para frontend e clonagem visual.

- `get_computed_style` - Get computed CSS styles for an element (all resolved values).
- `get_inline_styles` - Get inline CSS styles for an element.
- `get_matched_styles` - Get all matched CSS styles for an element.
- `get_media_queries` - Get all media queries from the page's stylesheets.
- `get_stylesheet_text` - Get the full text content of a stylesheet by its ID.
- `set_stylesheet_text` - Replace the full text content of a stylesheet.

### database-management (3)
Classificacao: D - Legado/nicho.
Criterio: WebSQL e legado; candidato forte a remover se nao usado.

- `execute_websql_query` - Execute a SQL query against a WebSQL database.
- `get_websql_table_names` - Get all table names in a WebSQL database.
- `list_websql_databases` - List all WebSQL databases on the current page.

### debugger-management (9)
Classificacao: C - Especializado.
Criterio: Debugger JS completo; valioso para dev, pesado para automacao simples.

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
Classificacao: B - Manter em desenvolvimento.
Criterio: Diagnostico do servidor; pode ser removido em producao enxuta.

- `clear_debug_view` - Clear all debug logs and statistics with timeout protection.
- `export_debug_logs` - Export debug logs to a file using the fastest available method with timeout protection.
- `get_debug_lock_status` - Get current debug logger lock status for debugging hanging exports.
- `get_debug_view` - Get comprehensive debug view with all logged errors and statistics.
- `hot_reload` - Hot reload all modules without restarting the server.
- `reload_status` - Check the status of loaded modules.
- `validate_browser_environment_tool` - Validate browser environment and diagnose potential issues.

### dom-snapshot-management (3)
Classificacao: B - Muito util sob demanda.
Criterio: Snapshots completos; muito bom para analise, pesado para uso comum.

- `dom_snapshot_capture` - Capture a full DOM snapshot of the current page including computed styles.
- `dom_snapshot_disable` - Disable the DOMSnapshot domain for a browser instance.
- `dom_snapshot_enable` - Enable the DOMSnapshot domain for a browser instance.

### dynamic-hooks (10)
Classificacao: C - Especializado.
Criterio: Hooks dinamicos de rede; poderoso, mas complexo e menos comum.

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
Classificacao: B - Muito util sob demanda.
Criterio: Clonagem/extracao detalhada de elementos; alto valor, custo maior.

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
Classificacao: A - Core. Manter.
Criterio: Essencial para clicar, digitar, consultar DOM, capturar tela e ler pagina.

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
Classificacao: B - Muito util sob demanda.
Criterio: Intercepcao/modificacao de requests; poderoso, mas nem todo fluxo precisa.

- `fetch_continue_request` - Continue an intercepted request, optionally modifying it.
- `fetch_continue_with_auth` - Continue an intercepted request that requires authentication.
- `fetch_disable` - Disable the Fetch domain, stopping request interception for a browser instance.
- `fetch_enable` - Enable the Fetch domain to intercept network requests for a browser instance.
- `fetch_fail_request` - Cause an intercepted request to fail with the given network error reason.
- `fetch_fulfill_request` - Fulfill an intercepted request with the given response.
- `fetch_get_response_body` - Get the response body for an intercepted request.

### file-extraction (8)
Classificacao: C - Especializado.
Criterio: Versoes que escrevem em arquivo; util para artefatos grandes, mas duplicativo.

- `clone_element_to_file` - Clone element completely and save directly to output_path in the workspace.
- `download_element_assets_to_folder` - Download images, backgrounds, icons, fonts, and media related to an element.
- `extract_complete_element_to_file` - Extract complete element via comprehensive cloner and save to output_path.
- `extract_element_animations_to_file` - Extract element animations and save to output_path.
- `extract_element_assets_to_file` - Extract element assets and save to output_path.
- `extract_element_events_to_file` - Extract element events and save to output_path.
- `extract_element_structure_to_file` - Extract element structure and save to output_path.
- `extract_element_styles_to_file` - Extract element styles and save to output_path.

### heapprofiler-management (7)
Classificacao: D - Baixa utilidade geral.
Criterio: Heap snapshots e GC; raro fora de investigacao de memoria.

- `collect_garbage` - Force a JavaScript garbage collection cycle.
- `get_object_by_heap_id` - Get a JavaScript object by its heap snapshot object ID.
- `start_heap_sampling` - Start heap sampling profiler (low-overhead memory profiling).
- `start_tracking_heap_objects` - Start tracking heap object allocations over time.
- `stop_heap_sampling` - Stop heap sampling and return the sampling profile.
- `stop_tracking_heap_objects` - Stop tracking heap object allocations.
- `take_heap_snapshot` - Take a heap snapshot of the current JavaScript heap.

### log-management (5)
Classificacao: C - Especializado.
Criterio: Dominio Log/violations; util em auditoria, pouco usado em navegacao comum.

- `log_clear` - Clear the browser log for a browser instance.
- `log_disable` - Disable the Log domain for a browser instance.
- `log_enable` - Enable the Log domain for a browser instance.
- `log_start_violations_report` - Start violation reporting for a browser instance.
- `log_stop_violations_report` - Stop violation reporting for a browser instance.

### network-debugging (5)
Classificacao: A - Core para diagnostico.
Criterio: Alto valor para scraping, depuracao e entender chamadas de rede.

- `get_request_details` - Get detailed information about a network request.
- `get_response_content` - Get response body content.
- `get_response_details` - Get response details for a network request.
- `list_network_requests` - List captured network requests.
- `modify_headers` - Modify request headers for future requests.

### overlay-management (8)
Classificacao: C - Especializado visual.
Criterio: Overlays CDP; util para debug visual, dispensavel em automacao headless.

- `overlay_disable` - Disable the Overlay domain for a browser instance.
- `overlay_enable` - Enable the Overlay domain for a browser instance.
- `overlay_hide_highlight` - Hide any active highlight on a browser instance.
- `overlay_highlight_node` - Highlight a DOM node with the given highlight configuration.
- `overlay_highlight_rect` - Highlight a rectangular area on the page.
- `overlay_set_show_flex_overlays` - Show CSS flexbox overlays for the specified nodes.
- `overlay_set_show_grid_overlays` - Show CSS grid overlays for the specified nodes.
- `overlay_set_show_scroll_snap_overlays` - Show scroll snap overlays for the specified nodes.

### profiler-management (5)
Classificacao: C - Especializado.
Criterio: CPU profiling e coverage; manter para performance/debug.

- `start_code_coverage` - Start collecting JavaScript code coverage data.
- `start_cpu_profiling` - Start CPU profiling for a browser instance.
- `stop_code_coverage` - Stop collecting JavaScript code coverage data.
- `stop_cpu_profiling` - Stop CPU profiling and return the profile data.
- `take_code_coverage_snapshot` - Take a snapshot of the current code coverage data.

### progressive-cloning (10)
Classificacao: C - Especializado.
Criterio: Clonagem incremental rica; manter se esse fluxo for frequente.

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
Classificacao: C - Sensivel.
Criterio: Certificados/estado de seguranca; pequeno, mas pode enfraquecer seguranca.

- `get_security_state` - Get the current security state of the page.
- `handle_certificate_error` - Handle a certificate error event by continuing or cancelling the request.
- `set_ignore_certificate_errors` - Set whether SSL/TLS certificate errors should be ignored.

### serviceworker-management (7)
Classificacao: C - Especializado PWA.
Criterio: Bom para PWAs; desnecessario para navegacao simples.

- `deliver_push_message` - Deliver a simulated push message to a service worker.
- `dispatch_sync_event` - Dispatch a background sync event to a service worker.
- `force_update_service_worker` - Force update a service worker (bypass the 24-hour update throttle).
- `list_service_workers` - List all registered service workers for the current page.
- `set_service_worker_force_update` - Set whether service workers should be force-updated on every page load.
- `skip_waiting_service_worker` - Skip the waiting phase and immediately activate a new service worker.
- `unregister_service_worker` - Unregister a service worker by its scope URL.

### storage-cdp-management (4)
Classificacao: C - Especializado.
Criterio: Quota e limpeza por origem; bom para debug, menos usado no dia a dia.

- `storage_clear_data_for_origin` - Clear storage data for a given origin.
- `storage_get_usage_and_quota` - Get storage usage and quota for a given origin.
- `storage_track_cache_storage_for_origin` - Start tracking cache storage for a given origin.
- `storage_untrack_cache_storage_for_origin` - Stop tracking cache storage for a given origin.

### storage-management (15)
Classificacao: B - Muito util sob demanda.
Criterio: Amplo controle de storage; util quando precisa estado persistido.

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
Classificacao: B - Util leve.
Criterio: Info do servidor/browser/processos; barato e bom para diagnostico.

- `get_server_info` - Return information about the MCP server process itself.
- `system_info_get_feature_state` - Return the state of a browser feature flag for a browser instance.
- `system_info_get_info` - Return information about the system for a browser instance.
- `system_info_get_process_info` - Return information about all running browser processes for a browser instance.

### tabs (5)
Classificacao: A - Core. Manter.
Criterio: Muito util para fluxos reais com varias abas.

- `close_tab` - Close a specific tab.
- `get_active_tab` - Get information about the currently active tab.
- `list_tabs` - List all tabs for a browser instance.
- `new_tab` - Open a new tab in the browser instance.
- `switch_tab` - Switch to a specific tab by bringing it to front.

### target-management (7)
Classificacao: B - Muito util sob demanda.
Criterio: Poderoso para targets, workers e iframes, mas duplica parte de abas/browser.

- `target_activate_target` - Activate (focus) a browser target.
- `target_attach_to_target` - Attach to a browser target to create a debugging session.
- `target_close_target` - Close a browser target.
- `target_create_target` - Create a new browser target (tab/window).
- `target_detach_from_target` - Detach from a browser target session.
- `target_get_target_info` - Get info for a specific browser target.
- `target_get_targets` - Get all browser targets (pages, workers, iframes), excluding browser-type targets.

### webauthn-management (6)
Classificacao: C - Especializado auth.
Criterio: Passkeys/FIDO2 virtual; manter se testa autenticacao moderna.

- `add_virtual_authenticator` - Add a virtual WebAuthn authenticator for testing passkeys and FIDO2.
- `add_webauthn_credential` - Add a credential to a virtual WebAuthn authenticator.
- `get_webauthn_credentials` - Get all credentials stored in a virtual WebAuthn authenticator.
- `remove_virtual_authenticator` - Remove a virtual WebAuthn authenticator.
- `remove_webauthn_credential` - Remove a credential from a virtual WebAuthn authenticator.
- `set_webauthn_user_verified` - Set the user verified state for a virtual WebAuthn authenticator.

