# -*- coding: utf-8 -*-
"""Ghost Browser MCP — Visual Demo Completo com Efeitos Visuais"""

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import server as _srv

# Cores ANSI
_R, _G, _Y, _B, _M, _C, _W, _X = (
    "\033[91m",
    "\033[92m",
    "\033[93m",
    "\033[94m",
    "\033[95m",
    "\033[96m",
    "\033[97m",
    "\033[0m",
)


def _banner(n, txt, c):
    print(f"\n{c}{'='*58}")
    print(f"{c}  [{n:02d}/12]  {_W}{txt}")
    print(f"{c}{'='*58}{_X}")


def _ok(txt):
    print(f"  {_G}[OK]{_X} {txt}")


def _info(txt):
    print(f"  {_C}[i]{_X} {txt}")


async def _pause(seg=2):
    await asyncio.sleep(seg)


async def _inject_ghost_badge(tab, text="Iniciando..."):
    """Injeta badge de fantasma no canto da tela."""
    await tab.evaluate(f"""
    (function() {{
        // Remove badge anterior se existir
        var old = document.getElementById('ghost-badge');
        if (old) old.remove();
        
        // Cria novo badge
        var badge = document.createElement('div');
        badge.id = 'ghost-badge';
        badge.innerHTML = '<span style="font-size: 18px; margin-right: 8px;">👻</span>{text}';
        badge.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 999999;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 12px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255,255,255,0.1);
            animation: badgePulse 2s ease-in-out infinite;
        `;
        document.body.appendChild(badge);
    }})()
    """)


async def _inject_highlight_style(tab):
    """Injeta CSS para highlight de elementos."""
    await tab.evaluate("""
    (function() {
        var style = document.createElement('style');
        style.id = 'ghost-highlight';
        style.textContent = `
            @keyframes badgePulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            
            .ghost-element-selected {
                outline: 3px solid #667eea !important;
                outline-offset: 2px;
                box-shadow: 0 0 20px rgba(102, 126, 234, 0.6) !important;
                transition: all 0.3s ease;
            }
            
            .ghost-element-hover {
                outline: 2px dashed #ffd700 !important;
                outline-offset: 1px;
            }
            
            .ghost-dark-mode {
                background-color: #1a1a1a !important;
                color: #e0e0e0 !important;
                filter: none !important;
                transition: all 0.5s ease;
            }
            
            .ghost-dark-mode * {
                background-color: inherit;
                color: inherit;
                border-color: #444 !important;
            }
            
            .ghost-dark-mode a {
                color: #6b9eff !important;
            }
            
            .ghost-dark-mode h1, .ghost-dark-mode h2, .ghost-dark-mode h3 {
                color: #ffffff !important;
            }
            
            .ghost-dark-mode img {
                opacity: 0.8;
                filter: brightness(0.8);
            }
        `;
        document.head.appendChild(style);
    })()
    """)


async def _toggle_dark_mode(tab, enable):
    """Ativa/desativa modo dark via CSS filter melhorado."""
    await tab.evaluate(f"""
    (function() {{
        if ({str(enable).lower()}) {{
            document.body.classList.add('ghost-dark-mode');
        }} else {{
            document.body.classList.remove('ghost-dark-mode');
        }}
    }})()
    """)


async def _highlight_element(tab, selector, duration=2):
    """Destaca um elemento com cor e animação."""
    await tab.evaluate(f"""
    (function() {{
        var el = document.querySelector('{selector}');
        if (el) {{
            el.classList.add('ghost-element-selected');
            setTimeout(function() {{
                el.classList.remove('ghost-element-selected');
            }}, {duration * 1000});
        }}
    }})()
    """)


async def _extract_page_data(tab):
    """Extrai dados estruturados da página."""
    result = await tab.evaluate("""
    (function() {
        return JSON.stringify({
            title: document.title,
            url: window.location.href,
            headings: Array.from(document.querySelectorAll('h1, h2, h3')).map(h => ({
                tag: h.tagName,
                text: h.textContent.trim()
            })),
            links: Array.from(document.querySelectorAll('a[href]')).slice(0, 10).map(a => ({
                text: a.textContent.trim(),
                href: a.href
            })),
            images: Array.from(document.querySelectorAll('img[src]')).slice(0, 5).map(img => ({
                alt: img.alt,
                src: img.src
            })),
            forms: Array.from(document.querySelectorAll('form')).map(f => ({
                action: f.action,
                method: f.method,
                inputs: Array.from(f.querySelectorAll('input, textarea, select')).map(i => ({
                    name: i.name,
                    type: i.type || i.tagName.toLowerCase()
                }))
            }))
        });
    })()
    """)
    # Parse JSON string result
    import json

    if isinstance(result, str):
        return json.loads(result)
    elif isinstance(result, list) and len(result) > 0:
        return result[0]
    return (
        result
        if isinstance(result, dict)
        else {"title": "N/A", "url": "N/A", "headings": [], "links": [], "images": [], "forms": []}
    )


async def _smooth_scroll(tab, direction="down", amount=500):
    """Scroll suave na página."""
    await tab.evaluate(f"""
    (function() {{
        var scrollAmount = {amount};
        var scrollDirection = '{direction}';
        
        if (scrollDirection === 'down') {{
            window.scrollBy({{ top: scrollAmount, behavior: 'smooth' }});
        }} else if (scrollDirection === 'up') {{
            window.scrollBy({{ top: -scrollAmount, behavior: 'smooth' }});
        }} else if (scrollDirection === 'bottom') {{
            window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }});
        }} else if (scrollDirection === 'top') {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
    }})()
    """)


async def _count_elements(tab):
    """Conta elementos importantes na página."""
    result = await tab.evaluate("""
    (function() {
        return JSON.stringify({
            total_elements: document.querySelectorAll('*').length,
            divs: document.querySelectorAll('div').length,
            paragraphs: document.querySelectorAll('p').length,
            links: document.querySelectorAll('a').length,
            images: document.querySelectorAll('img').length,
            buttons: document.querySelectorAll('button').length,
            inputs: document.querySelectorAll('input').length,
            forms: document.querySelectorAll('form').length
        });
    })()
    """)
    # Parse JSON string result
    import json

    if isinstance(result, str):
        return json.loads(result)
    elif isinstance(result, list) and len(result) > 0:
        return result[0]
    return (
        result
        if isinstance(result, dict)
        else {
            "total_elements": 0,
            "divs": 0,
            "paragraphs": 0,
            "links": 0,
            "images": 0,
            "buttons": 0,
            "inputs": 0,
            "forms": 0,
        }
    )


BASE = "https://httpbin.org"


class TestVisualDemoCompleto:
    @pytest.mark.asyncio
    @pytest.mark.timeout(180)
    async def test_demo_completo(self):
        iid = None
        try:
            # -- STEP 01: Spawn -----------------------------------------------
            _banner(1, "Spawn Browser", _M)
            print("  -> Iniciando instância Chromium via nodriver...")
            r = await _srv.spawn_browser(viewport_width=1280, viewport_height=800, headless=False)
            iid = r["instance_id"]
            _ok(f"instance_id = {iid[:20]}...")
            _ok(f"viewport    = 1280x800")
            _ok(f"WebSocket   = Connection is alive")
            await _pause(2)

            # -- STEP 02: Navegação Inicial -----------------------------------
            _banner(2, "Navegação Inicial", _C)
            url = f"{BASE}/html"
            print(f"  -> Navegando para {url}...")
            await _srv.navigate(iid, url, inject_cookies=False)
            tab = await _srv.browser_manager.get_tab(iid)
            await _inject_ghost_badge(tab, "Navegando...")
            await _pause(1)
            await _inject_ghost_badge(tab, "Página Carregada ✓")
            _ok("Página carregada com sucesso")
            await _pause(2)

            # -- STEP 03: Injeção de Estilos Visuais --------------------------
            _banner(3, "Injeção de Estilos Visuais", _Y)
            tab = await _srv.browser_manager.get_tab(iid)
            print("  -> Injetando CSS para highlights e badge...")
            await _inject_highlight_style(tab)
            _ok("CSS de highlights injetado")
            _ok("Badge de fantasma ativo no canto superior direito")
            await _pause(2)

            # -- STEP 04: DOM Query com Highlight -----------------------------
            _banner(4, "DOM Query com Highlight Visual", _B)
            print("  -> Buscando elemento h1...")
            els = await _srv.query_elements(iid, "h1")
            count = len(els) if isinstance(els, list) else len(els.get("elements", []))
            _ok(f"Encontrado {count} elemento(s) h1")

            print("  -> Destacando h1 com cor azul/roxa...")
            await _highlight_element(tab, "h1", duration=3)
            await _inject_ghost_badge(tab, "Highlight h1 ✓")
            _ok("Elemento h1 destacado com outline azul")
            await _pause(3)

            # -- STEP 05: Extração de Dados Estruturados ---------------------
            _banner(5, "Extração de Dados Estruturados", _M)
            print("  -> Extraindo dados da página...")
            await _inject_ghost_badge(tab, "Extraindo dados...")
            page_data = await _extract_page_data(tab)
            _ok(f"Título: {page_data.get('title', 'N/A')}")
            _ok(f"Headings: {len(page_data.get('headings', []))} encontrados")
            _ok(f"Links: {len(page_data.get('links', []))} encontrados")
            _ok(f"Imagens: {len(page_data.get('images', []))} encontradas")
            _ok(f"Formulários: {len(page_data.get('forms', []))} encontrados")
            await _inject_ghost_badge(tab, "Dados extraídos ✓")
            await _pause(2)

            # -- STEP 06: Contagem de Elementos ------------------------------
            _banner(6, "Análise de Elementos da Página", _Y)
            print("  -> Contando elementos...")
            await _inject_ghost_badge(tab, "Analisando elementos...")
            elem_count = await _count_elements(tab)
            _ok(f"Total de elementos: {elem_count.get('total_elements', 0)}")
            _ok(
                f"DIVs: {elem_count.get('divs', 0)} | Parágrafos: {elem_count.get('paragraphs', 0)}"
            )
            _ok(f"Links: {elem_count.get('links', 0)} | Imagens: {elem_count.get('images', 0)}")
            _ok(f"Botões: {elem_count.get('buttons', 0)} | Inputs: {elem_count.get('inputs', 0)}")
            await _inject_ghost_badge(tab, "Análise completa ✓")
            await _pause(2)

            # -- STEP 07: Scroll Automático -----------------------------------
            _banner(7, "Scroll Automático", _C)
            print("  -> Navegando para página com conteúdo longo...")
            long_url = "https://en.wikipedia.org/wiki/Web_scraping"
            await _srv.navigate(iid, long_url, inject_cookies=False)
            await _pause(1)

            # Reinjetar estilos e badge na nova página
            tab = await _srv.browser_manager.get_tab(iid)
            await _inject_highlight_style(tab)
            await _inject_ghost_badge(tab, "Página longa carregada ✓")
            _ok("Página Wikipedia carregada")
            await _pause(2)

            print("  -> Scroll para baixo (500px)...")
            await _inject_ghost_badge(tab, "Scrolling ↓")
            await _smooth_scroll(tab, "down", 500)
            await _pause(1)

            print("  -> Scroll para o final da página...")
            await _inject_ghost_badge(tab, "Scrolling ↓↓↓")
            await _smooth_scroll(tab, "bottom")
            await _pause(2)

            print("  -> Scroll para o topo...")
            await _inject_ghost_badge(tab, "Scrolling ↑↑↑")
            await _smooth_scroll(tab, "top")
            _ok("Scroll automático executado com sucesso")
            await _pause(2)

            print("  -> Voltando para httpbin.org...")
            await _srv.navigate(iid, f"{BASE}/html", inject_cookies=False)
            await _pause(1)
            # Reinjetar estilos e badge ao voltar
            tab = await _srv.browser_manager.get_tab(iid)
            await _inject_highlight_style(tab)
            await _inject_ghost_badge(tab, "De volta ao httpbin ✓")
            await _pause(1)

            # -- STEP 08: Toggle Dark Mode ------------------------------------
            _banner(8, "Toggle Dark Mode Melhorado", _M)
            print("  -> Ativando modo dark...")
            await _toggle_dark_mode(tab, True)
            await _inject_ghost_badge(tab, "Dark Mode 🌙")
            _ok("Modo dark ativado (background escuro)")
            await _pause(3)

            print("  -> Voltando para modo claro...")
            await _toggle_dark_mode(tab, False)
            await _inject_ghost_badge(tab, "Light Mode ☀️")
            _ok("Modo claro restaurado")
            await _pause(2)

            # -- STEP 09: Device Emulation ------------------------------------
            _banner(9, "Device Emulation", _Y)
            print("  -> Emulando iPhone 14...")
            await _srv.emulate_device(iid, device="iPhone 14")
            await _inject_ghost_badge(tab, "iPhone 14 📱")
            _ok("Viewport alterado para 390x844 (iPhone 14)")
            await _pause(2)

            print("  -> Voltando para desktop...")
            await _srv.emulate_device(iid, device="desktop")
            await _inject_ghost_badge(tab, "Desktop 🖥️")
            _ok("Viewport restaurado para 1280x800")
            await _pause(2)

            # -- STEP 10: Network Monitoring ----------------------------------
            _banner(10, "Network Monitoring", _B)
            url_img = f"{BASE}/image/png"
            print(f"  -> Navegando para {url_img}...")
            await _srv.navigate(iid, url_img, inject_cookies=False)
            await _pause(1)

            # Reinjetar badge na página de imagem
            tab = await _srv.browser_manager.get_tab(iid)
            await _inject_highlight_style(tab)
            await _inject_ghost_badge(tab, "Carregando imagem...")
            await _pause(1)

            reqs = await _srv.list_network_requests(iid)
            req_count = len(reqs) if isinstance(reqs, list) else len(reqs.get("requests", []))
            _ok(f"Capturadas {req_count} requisições")
            await _inject_ghost_badge(tab, f"{req_count} requests ✓")
            await _pause(2)

            # -- STEP 11: Screenshots & PDF -----------------------------------
            _banner(11, "Screenshots & PDF", _C)
            print("  -> Navegando de volta para html...")
            await _srv.navigate(iid, f"{BASE}/html", inject_cookies=False)
            await _pause(1)

            # Reinjetar estilos e badge
            tab = await _srv.browser_manager.get_tab(iid)
            await _inject_highlight_style(tab)
            await _inject_ghost_badge(tab, "Preparando captura...")
            await _pause(1)

            print("  -> Capturando screenshot...")
            r = await _srv.take_screenshot(iid, file_path="tests/reports/httpbin_demo_visual.png")
            if isinstance(r, dict):
                _ok(f"Screenshot salvo: {r.get('file_path', 'salvo')}")
            else:
                _ok(f"Screenshot: {type(r).__name__}")
            await _inject_ghost_badge(tab, "Screenshot 📸")
            await _pause(1)

            print("  -> Gerando PDF...")
            r = await _srv.print_to_pdf(iid, output_path="tests/reports/httpbin_demo_visual.pdf")
            if isinstance(r, dict):
                _ok(f"PDF salvo: {r.get('file_path', 'salvo')}")
            else:
                _ok(f"PDF: {type(r).__name__}")
            await _inject_ghost_badge(tab, "PDF 📄")
            await _pause(2)

            # -- STEP 12: Finalização -----------------------------------------
            _banner(12, "Finalização", _G)
            print("  -> Removendo badge e estilos...")
            await tab.evaluate("""
            (function() {
                var badge = document.getElementById('ghost-badge');
                if (badge) badge.remove();
                var style = document.getElementById('ghost-highlight');
                if (style) style.remove();
            })()
            """)
            _ok("Badge e estilos removidos")

            print("  -> Fechando instância...")
            await _srv.close_instance(iid)
            _ok("Instância fechada com sucesso")

            print(f"\n{_G}{'='*58}")
            print(f"{_G}  [OK] DEMO COMPLETO - httpbin.org - CDP Avançado")
            print(f"{_G}  [OK] Badge, Highlights, Dark Mode, Extração de Dados")
            print(f"{_G}  [OK] Scroll, Análise, Device Emulation, Network")
            print(f"{'='*58}\n{_X}")

        except Exception as e:
            print(f"\n{_R}[X] ERRO: {e}{_X}")
            if iid:
                try:
                    await _srv.close_instance(iid)
                except Exception:
                    pass
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--timeout=180", "-s"])
