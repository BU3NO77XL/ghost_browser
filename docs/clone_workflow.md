# Ghost Browser Clone Workflow

Use this workflow for pixel-perfect site clones.

1. Start with the real page, not a synthetic rebuild:
   - `spawn_browser`
   - `navigate`
   - `save_page_html`
   - `take_screenshot`
   - In Docker mode, write artifacts under `/workspace/...`. Paths such as
     `/app/govbr/index.html` are redirected to the client-visible
     `ghost_browser_mcp_output/govbr/index.html` folder.

2. Download local assets before rewriting anything:
   - `download_element_assets_to_folder`
   - Use `selector: "html"` or `selector: "body"` for full-page clones.
   - It downloads only resources the browser actually loaded for the current page state.

3. Use extraction tools for missing details only:
   - `extract_element_structure_to_file` for DOM fragments.
   - `extract_element_styles_to_file` for a specific element.
   - Avoid `extract_complete_element_to_file` on `html` with children unless needed; it is heavy.

4. Build the clone from the saved HTML:
   - Read the saved HTML file from the workspace/output folder. Do not recreate
     it from chat context if `save_page_html` already succeeded.
   - Rewrite asset URLs to the downloaded files from `manifest.json`.
   - Prefer local CSS/assets over CDN links when the goal is an offline pixel clone.
   - Keep CDN links only as a fallback when an asset cannot be downloaded.

5. Validate visually:
   - Open the clone.
   - Take a screenshot.
   - Compare against the original screenshot.
