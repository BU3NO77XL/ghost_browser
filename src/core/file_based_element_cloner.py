"""
File-based element cloner.

All extraction methods require an explicit *output_path* pointing to a
location inside the client's workspace.  Files are NEVER saved to a
server-side directory — that would expose cloned content to the server
and accumulate disk garbage.
"""

import asyncio
import json
import mimetypes
import re
import sys
import uuid
from base64 import b64decode
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import unquote, urljoin, urlparse

import httpx

try:
    from core.debug_logger import debug_logger
except ImportError:
    from debug_logger import debug_logger

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.comprehensive_element_cloner import ComprehensiveElementCloner
from core.element_cloner import element_cloner
from core.output_paths import output_path_metadata, resolve_output_path


class FileBasedElementCloner:
    """Element cloner that saves data directly to a caller-supplied path."""

    def __init__(self):
        self.comprehensive_cloner = ComprehensiveElementCloner()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _safe_process_framework_handlers(self, framework_handlers):
        """Safely process framework handlers that might be dict or list."""
        if isinstance(framework_handlers, dict):
            return {
                k: len(v) if isinstance(v, list) else str(v) for k, v in framework_handlers.items()
            }
        elif isinstance(framework_handlers, list):
            return {"handlers": len(framework_handlers)}
        else:
            return {"value": str(framework_handlers)}

    def _generate_filename(self, prefix: str, extension: str = "json") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{timestamp}_{unique_id}.{extension}"

    def _save_to_file(
        self,
        data: Dict[str, Any],
        output_path: str,
        client_roots=None,
    ) -> str:
        """
        Write *data* as JSON to *output_path*.

        The parent directory is created automatically.  Returns the absolute
        path of the written file.

        Args:
            data: Data to serialise.
            output_path: Destination path (absolute or relative to CWD).

        Returns:
            Absolute path string of the written file.

        Raises:
            ValueError: If output_path is empty or None.
        """
        if not output_path:
            raise ValueError(
                "output_path is required. Pass an absolute path inside your workspace so the "
                "file is written directly there and never stored on the server."
            )
        file_path = resolve_output_path(output_path, client_roots)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return str(file_path.absolute())

    def _path_metadata(self, path: str) -> Dict[str, str]:
        return output_path_metadata(Path(path))

    def _safe_filename(self, url: str, content_type: Optional[str], index: int) -> str:
        parsed = urlparse(url)
        name = unquote(Path(parsed.path).name)
        if not name or name in {"/", ".", ".."}:
            extension = mimetypes.guess_extension((content_type or "").split(";")[0].strip())
            name = f"asset_{index}{extension or '.bin'}"
        name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
        if not Path(name).suffix and content_type:
            extension = mimetypes.guess_extension(content_type.split(";")[0].strip())
            if extension:
                name = f"{name}{extension}"
        return name or f"asset_{index}.bin"

    def _unique_path(self, directory: Path, filename: str, overwrite: bool) -> Path:
        target = directory / filename
        if overwrite or not target.exists():
            return target
        stem = target.stem
        suffix = target.suffix
        counter = 2
        while True:
            candidate = directory / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def _category_for_loaded_resource(self, url: str, initiator_type: str) -> Optional[str]:
        suffix = Path(urlparse(url).path.lower()).suffix
        initiator = (initiator_type or "").lower()

        if suffix == ".css":
            return "stylesheets"
        if suffix in {".woff", ".woff2", ".ttf", ".otf", ".eot"}:
            return "fonts"
        if suffix in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif", ".ico"}:
            return "images"
        if suffix in {".mp4", ".webm", ".mov", ".m4v", ".mp3", ".wav", ".ogg", ".aac"}:
            return "media"
        if initiator in {"img", "image", "css"}:
            return "images"
        if initiator in {"link"}:
            return "stylesheets"
        if initiator in {"video", "audio"}:
            return "media"
        return None

    def _iter_loaded_resource_urls(
        self,
        asset_data: Dict[str, Any],
        include_images: bool,
        include_fonts: bool,
        include_media: bool,
        include_stylesheets: bool,
    ):
        seen = set()
        for resource in asset_data.get("loaded_resources", []) or []:
            url = resource.get("url")
            if not url:
                continue
            category = self._category_for_loaded_resource(url, resource.get("initiator_type", ""))
            if not category:
                continue
            if category == "images" and not include_images:
                continue
            if category == "fonts" and not include_fonts:
                continue
            if category == "stylesheets" and not include_stylesheets:
                continue
            if category == "media" and not include_media:
                continue
            key = (category, url)
            if key in seen:
                continue
            seen.add(key)
            yield {"category": category, "url": url, "source": resource}

    def _count_asset_candidates(self, asset_data: Dict[str, Any]) -> int:
        total = 0
        for key in (
            "images",
            "background_images",
            "icons",
            "stylesheets",
            "videos",
            "audio",
            "loaded_resources",
        ):
            value = asset_data.get(key, [])
            if isinstance(value, list):
                total += len(value)
        fonts = asset_data.get("fonts", {})
        if isinstance(fonts, dict) and isinstance(fonts.get("font_faces"), list):
            total += len(fonts["font_faces"])
        return total

    async def _download_asset(
        self,
        client: httpx.AsyncClient,
        asset: Dict[str, Any],
        output_dir: Path,
        base_url: str,
        index: int,
        overwrite: bool,
    ) -> Dict[str, Any]:
        category = asset["category"]
        raw_url = asset["url"]
        resolved_url = urljoin(base_url, raw_url)
        category_dir = output_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        if resolved_url.startswith("data:"):
            header, _, payload = resolved_url.partition(",")
            is_base64 = ";base64" in header
            content_type = header[5:].split(";")[0] if header.startswith("data:") else None
            content = b64decode(payload) if is_base64 else unquote(payload).encode("utf-8")
            filename = self._safe_filename(f"asset_{index}", content_type, index)
            file_path = self._unique_path(category_dir, filename, overwrite)
            file_path.write_bytes(content)
            return {
                "url": raw_url[:120],
                "resolved_url": "data:",
                "category": category,
                "file_path": str(file_path.absolute()),
                "content_type": content_type,
                "size": len(content),
                "status": "downloaded",
            }

        parsed = urlparse(resolved_url)
        if parsed.scheme not in {"http", "https"}:
            return {
                "url": raw_url,
                "resolved_url": resolved_url,
                "category": category,
                "status": "skipped",
                "error": f"Unsupported URL scheme: {parsed.scheme or 'relative'}",
            }

        response = await client.get(resolved_url, follow_redirects=True)
        response.raise_for_status()
        content_type = response.headers.get("content-type")
        if (content_type or "").split(";")[0].strip().lower() == "text/html":
            return {
                "url": raw_url,
                "resolved_url": str(response.url),
                "category": category,
                "content_type": content_type,
                "status_code": response.status_code,
                "status": "skipped",
                "error": "Skipped HTML document; loaded-resource downloads only keep asset files.",
            }
        filename = self._safe_filename(str(response.url), content_type, index)
        file_path = self._unique_path(category_dir, filename, overwrite)
        file_path.write_bytes(response.content)
        return {
            "url": raw_url,
            "resolved_url": str(response.url),
            "category": category,
            "file_path": str(file_path.absolute()),
            "content_type": content_type,
            "size": len(response.content),
            "status_code": response.status_code,
            "status": "downloaded",
        }

    # ------------------------------------------------------------------
    # Public extraction methods
    # ------------------------------------------------------------------

    async def extract_element_styles_to_file(
        self,
        tab,
        selector: str,
        output_path: str,
        include_computed: bool = True,
        include_css_rules: bool = True,
        include_pseudo: bool = True,
        include_inheritance: bool = False,
        instance_id: str = None,
        client_roots=None,
    ) -> Dict[str, Any]:
        """
        Extract element styles and save to *output_path*.

        Args:
            tab: Browser tab instance.
            selector: CSS selector for the element.
            output_path: Absolute destination path inside the workspace.
            include_computed: Include computed styles.
            include_css_rules: Include matching CSS rules.
            include_pseudo: Include pseudo-element styles.
            include_inheritance: Include style inheritance chain.
            instance_id: Unused — kept for API compatibility.

        Returns:
            Dict with file_path and extraction summary.
        """
        try:
            debug_logger.log_info(
                "file_element_cloner",
                "extract_styles_to_file",
                f"Starting style extraction for selector: {selector}",
            )
            style_data = await element_cloner.extract_element_styles(
                tab,
                selector=selector,
                include_computed=include_computed,
                include_css_rules=include_css_rules,
                include_pseudo=include_pseudo,
                include_inheritance=include_inheritance,
            )
            file_path = self._save_to_file(style_data, output_path, client_roots)
            debug_logger.log_info(
                "file_element_cloner", "extract_styles_to_file", f"Styles saved to {file_path}"
            )
            return {
                **self._path_metadata(file_path),
                "extraction_type": "styles",
                "selector": selector,
                "url": getattr(tab, "url", "unknown"),
                "components": {
                    "computed_styles_count": len(style_data.get("computed_styles", {})),
                    "css_rules_count": len(style_data.get("css_rules", [])),
                    "pseudo_elements_count": len(style_data.get("pseudo_elements", {})),
                    "custom_properties_count": len(style_data.get("custom_properties", {})),
                },
            }
        except Exception as e:
            debug_logger.log_error("file_element_cloner", "extract_styles_to_file", e)
            return {"error": str(e)}

    async def extract_complete_element_to_file(
        self,
        tab,
        selector: str,
        output_path: str,
        include_children: bool = True,
        instance_id: str = None,
        client_roots=None,
    ) -> Dict[str, Any]:
        """
        Extract complete element via comprehensive cloner and save to *output_path*.

        Args:
            tab: Browser tab object.
            selector: CSS selector for the element.
            output_path: Absolute destination path inside the workspace.
            include_children: Whether to include children.
            instance_id: Unused — kept for API compatibility.

        Returns:
            Dict with file_path and extraction summary.
        """
        try:
            complete_data = await self.comprehensive_cloner.extract_complete_element(
                tab, selector, include_children
            )
            complete_data["_metadata"] = {
                "extraction_type": "complete_comprehensive",
                "selector": selector,
                "timestamp": datetime.now().isoformat(),
                "include_children": include_children,
            }
            file_path = self._save_to_file(complete_data, output_path, client_roots)
            debug_logger.log_info(
                "file_element_cloner",
                "extract_complete_to_file",
                f"Saved complete element data to {file_path}",
            )
            return {
                **self._path_metadata(file_path),
                "extraction_type": "complete_comprehensive",
                "selector": selector,
                "url": complete_data.get("url", "unknown"),
                "summary": {
                    "tag_name": complete_data.get("html", {}).get("tagName", "unknown"),
                    "computed_styles_count": len(complete_data.get("styles", {})),
                    "attributes_count": len(complete_data.get("html", {}).get("attributes", [])),
                    "event_listeners_count": len(complete_data.get("eventListeners", [])),
                    "children_count": (
                        len(complete_data.get("children", [])) if include_children else 0
                    ),
                    "has_pseudo_elements": bool(complete_data.get("pseudoElements")),
                    "css_rules_count": len(complete_data.get("cssRules", [])),
                    "animations_count": len(complete_data.get("animations", [])),
                    "file_size_kb": round(len(json.dumps(complete_data)) / 1024, 2),
                },
            }
        except Exception as e:
            debug_logger.log_error("file_element_cloner", "extract_complete_to_file", e)
            return {"error": str(e)}

    async def extract_element_structure_to_file(
        self,
        tab,
        output_path: str,
        element=None,
        selector: str = None,
        include_children: bool = False,
        include_attributes: bool = True,
        include_data_attributes: bool = True,
        max_depth: int = 3,
        instance_id: str = None,
        client_roots=None,
    ) -> Dict[str, Any]:
        """
        Extract element structure and save to *output_path*.

        Args:
            tab: Browser tab object.
            output_path: Absolute destination path inside the workspace.
            element: DOM element object (optional).
            selector: CSS selector for the element.
            include_children: Whether to include children.
            include_attributes: Whether to include attributes.
            include_data_attributes: Whether to include data attributes.
            max_depth: Maximum depth for extraction.
            instance_id: Unused — kept for API compatibility.

        Returns:
            Dict with file_path and extraction summary.
        """
        try:
            structure_data = await element_cloner.extract_element_structure(
                tab,
                element,
                selector,
                include_children,
                include_attributes,
                include_data_attributes,
                max_depth,
            )
            structure_data["_metadata"] = {
                "extraction_type": "structure",
                "selector": selector,
                "timestamp": datetime.now().isoformat(),
                "options": {
                    "include_children": include_children,
                    "include_attributes": include_attributes,
                    "include_data_attributes": include_data_attributes,
                    "max_depth": max_depth,
                },
            }
            file_path = self._save_to_file(structure_data, output_path, client_roots)
            debug_logger.log_info(
                "file_element_cloner",
                "extract_structure_to_file",
                f"Saved structure data to {file_path}",
            )
            return {
                **self._path_metadata(file_path),
                "extraction_type": "structure",
                "selector": selector,
                "summary": {
                    "tag_name": structure_data.get("tag_name"),
                    "attributes_count": len(structure_data.get("attributes", {})),
                    "data_attributes_count": len(structure_data.get("data_attributes", {})),
                    "children_count": len(structure_data.get("children", [])),
                    "dom_path": structure_data.get("dom_path"),
                },
            }
        except Exception as e:
            debug_logger.log_error("file_element_cloner", "extract_structure_to_file", e)
            return {"error": str(e)}

    async def extract_element_events_to_file(
        self,
        tab,
        output_path: str,
        element=None,
        selector: str = None,
        include_inline: bool = True,
        include_listeners: bool = True,
        include_framework: bool = True,
        analyze_handlers: bool = True,
        instance_id: str = None,
        client_roots=None,
    ) -> Dict[str, Any]:
        """
        Extract element events and save to *output_path*.

        Args:
            tab: Browser tab object.
            output_path: Absolute destination path inside the workspace.
            element: DOM element object (optional).
            selector: CSS selector for the element.
            include_inline: Include inline event handlers.
            include_listeners: Include event listeners.
            include_framework: Include framework event handlers.
            analyze_handlers: Analyze event handlers.
            instance_id: Unused — kept for API compatibility.

        Returns:
            Dict with file_path and extraction summary.
        """
        try:
            event_data = await element_cloner.extract_element_events(
                tab,
                element,
                selector,
                include_inline,
                include_listeners,
                include_framework,
                analyze_handlers,
            )
            event_data["_metadata"] = {
                "extraction_type": "events",
                "selector": selector,
                "timestamp": datetime.now().isoformat(),
                "options": {
                    "include_inline": include_inline,
                    "include_listeners": include_listeners,
                    "include_framework": include_framework,
                    "analyze_handlers": analyze_handlers,
                },
            }
            file_path = self._save_to_file(event_data, output_path, client_roots)
            debug_logger.log_info(
                "file_element_cloner", "extract_events_to_file", f"Saved events data to {file_path}"
            )
            return {
                **self._path_metadata(file_path),
                "extraction_type": "events",
                "selector": selector,
                "summary": {
                    "inline_handlers_count": len(event_data.get("inline_handlers", [])),
                    "event_listeners_count": len(event_data.get("event_listeners", [])),
                    "detected_frameworks": event_data.get("detected_frameworks", []),
                    "framework_handlers": self._safe_process_framework_handlers(
                        event_data.get("framework_handlers", {})
                    ),
                },
            }
        except Exception as e:
            debug_logger.log_error("file_element_cloner", "extract_events_to_file", e)
            return {"error": str(e)}

    async def extract_element_animations_to_file(
        self,
        tab,
        output_path: str,
        element=None,
        selector: str = None,
        include_css_animations: bool = True,
        include_transitions: bool = True,
        include_transforms: bool = True,
        analyze_keyframes: bool = True,
        instance_id: str = None,
        client_roots=None,
    ) -> Dict[str, Any]:
        """
        Extract element animations and save to *output_path*.

        Args:
            tab: Browser tab object.
            output_path: Absolute destination path inside the workspace.
            element: DOM element object (optional).
            selector: CSS selector for the element.
            include_css_animations: Include CSS animations.
            include_transitions: Include transitions.
            include_transforms: Include transforms.
            analyze_keyframes: Analyze keyframes.
            instance_id: Unused — kept for API compatibility.

        Returns:
            Dict with file_path and extraction summary.
        """
        try:
            animation_data = await element_cloner.extract_element_animations(
                tab,
                element,
                selector,
                include_css_animations,
                include_transitions,
                include_transforms,
                analyze_keyframes,
            )
            animation_data["_metadata"] = {
                "extraction_type": "animations",
                "selector": selector,
                "timestamp": datetime.now().isoformat(),
                "options": {
                    "include_css_animations": include_css_animations,
                    "include_transitions": include_transitions,
                    "include_transforms": include_transforms,
                    "analyze_keyframes": analyze_keyframes,
                },
            }
            file_path = self._save_to_file(animation_data, output_path, client_roots)
            debug_logger.log_info(
                "file_element_cloner",
                "extract_animations_to_file",
                f"Saved animations data to {file_path}",
            )
            return {
                **self._path_metadata(file_path),
                "extraction_type": "animations",
                "selector": selector,
                "summary": {
                    "has_animations": animation_data.get("animations", {}).get(
                        "animation_name", "none"
                    )
                    != "none",
                    "has_transitions": animation_data.get("transitions", {}).get(
                        "transition_property", "none"
                    )
                    != "none",
                    "has_transforms": animation_data.get("transforms", {}).get("transform", "none")
                    != "none",
                    "keyframes_count": len(animation_data.get("keyframes", [])),
                },
            }
        except Exception as e:
            debug_logger.log_error("file_element_cloner", "extract_animations_to_file", e)
            return {"error": str(e)}

    async def extract_element_assets_to_file(
        self,
        tab,
        output_path: str,
        element=None,
        selector: str = None,
        include_images: bool = True,
        include_backgrounds: bool = True,
        include_fonts: bool = True,
        fetch_external: bool = False,
        instance_id: str = None,
        client_roots=None,
    ) -> Dict[str, Any]:
        """
        Extract element assets and save to *output_path*.

        Args:
            tab: Browser tab object.
            output_path: Absolute destination path inside the workspace.
            element: DOM element object (optional).
            selector: CSS selector for the element.
            include_images: Include images.
            include_backgrounds: Include background images.
            include_fonts: Include fonts.
            fetch_external: Fetch external assets.
            instance_id: Unused — kept for API compatibility.

        Returns:
            Dict with file_path and extraction summary.
        """
        try:
            asset_data = await element_cloner.extract_element_assets(
                tab,
                element,
                selector,
                include_images,
                include_backgrounds,
                include_fonts,
                fetch_external,
            )
            asset_data["_metadata"] = {
                "extraction_type": "assets",
                "selector": selector,
                "timestamp": datetime.now().isoformat(),
                "options": {
                    "include_images": include_images,
                    "include_backgrounds": include_backgrounds,
                    "include_fonts": include_fonts,
                    "fetch_external": fetch_external,
                },
            }
            file_path = self._save_to_file(asset_data, output_path, client_roots)
            debug_logger.log_info(
                "file_element_cloner", "extract_assets_to_file", f"Saved assets data to {file_path}"
            )
            return {
                **self._path_metadata(file_path),
                "extraction_type": "assets",
                "selector": selector,
                "summary": {
                    "images_count": len(asset_data.get("images", [])),
                    "background_images_count": len(asset_data.get("background_images", [])),
                    "font_family": asset_data.get("fonts", {}).get("family"),
                    "custom_fonts_count": len(asset_data.get("fonts", {}).get("custom_fonts", [])),
                    "icons_count": len(asset_data.get("icons", [])),
                    "videos_count": len(asset_data.get("videos", [])),
                    "audio_count": len(asset_data.get("audio", [])),
                },
            }
        except Exception as e:
            debug_logger.log_error("file_element_cloner", "extract_assets_to_file", e)
            return {"error": str(e)}

    async def download_element_assets_to_folder(
        self,
        tab,
        selector: str,
        output_dir: str,
        include_images: bool = True,
        include_backgrounds: bool = True,
        include_fonts: bool = True,
        include_icons: bool = True,
        include_media: bool = True,
        include_stylesheets: bool = True,
        wait_for_assets_seconds: float = 5.0,
        overwrite: bool = False,
        timeout: float = 20.0,
        max_assets: int = 200,
        instance_id: str = None,
        client_roots=None,
    ) -> Dict[str, Any]:
        """
        Extract asset URLs for an element, download them, and save a manifest.

        Args:
            tab: Browser tab object.
            selector: CSS selector for the element.
            output_dir: Destination folder for assets and manifest.json.
            include_images: Download img/srcset URLs.
            include_backgrounds: Download CSS background images.
            include_fonts: Download readable @font-face URLs.
            include_icons: Download page icons.
            include_media: Download video/audio sources and posters.
            include_stylesheets: Download linked CSS files.
            Only resources actually loaded by the browser are downloaded.
            wait_for_assets_seconds: Retry extraction for this many seconds if no assets are ready.
            overwrite: Replace files with the same name instead of creating suffixed names.
            timeout: Per-request timeout in seconds.
            max_assets: Maximum number of assets to attempt.
            instance_id: Unused — kept for API compatibility.

        Returns:
            Dict with manifest_path, download counts, and failed/skipped entries.
        """
        try:
            if not output_dir:
                raise ValueError("output_dir is required")
            if max_assets < 1:
                raise ValueError("max_assets must be at least 1")

            destination = resolve_output_path(output_dir, client_roots)
            destination.mkdir(parents=True, exist_ok=True)

            asset_data = {}
            best_asset_data = {}
            best_asset_count = -1
            stable_count = 0
            attempts = max(1, int(wait_for_assets_seconds) + 1)
            for attempt in range(attempts):
                asset_data = await element_cloner.extract_element_assets(
                    tab,
                    selector=selector,
                    include_images=include_images,
                    include_backgrounds=include_backgrounds,
                    include_fonts=include_fonts,
                    fetch_external=False,
                )
                if "error" in asset_data:
                    break
                asset_count = self._count_asset_candidates(asset_data)
                if asset_count > best_asset_count:
                    best_asset_data = asset_data
                    best_asset_count = asset_count
                    stable_count = 0
                elif asset_count == best_asset_count and asset_count > 0:
                    stable_count += 1
                if stable_count >= 2 and attempt >= 2:
                    asset_data = best_asset_data
                    break
                if attempt < attempts - 1:
                    await asyncio.sleep(1)
            if best_asset_count > self._count_asset_candidates(asset_data):
                asset_data = best_asset_data
            if "error" in asset_data:
                return asset_data

            assets = list(
                self._iter_loaded_resource_urls(
                    asset_data,
                    include_images=include_images or include_backgrounds or include_icons,
                    include_fonts=include_fonts,
                    include_media=include_media,
                    include_stylesheets=include_stylesheets,
                )
            )
            if not include_icons:
                assets = [asset for asset in assets if asset["category"] != "icons"]

            manifest = {
                "selector": selector,
                "url": getattr(tab, "url", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "output_dir": str(destination.absolute()),
                "max_assets": max_assets,
                "download_mode": "loaded",
                "downloads": [],
                "failures": [],
                "skipped": [],
            }

            async with httpx.AsyncClient(
                timeout=timeout,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                },
            ) as client:
                manifest["requested_assets"] = len(assets)
                limited_assets = assets[:max_assets]

                for index, asset in enumerate(limited_assets, start=1):
                    try:
                        result = await self._download_asset(
                            client,
                            asset,
                            output_dir=destination,
                            base_url=getattr(tab, "url", ""),
                            index=index,
                            overwrite=overwrite,
                        )
                        if result.get("status") == "downloaded":
                            manifest["downloads"].append(result)
                        elif result.get("status") == "skipped":
                            manifest["skipped"].append(result)
                        else:
                            manifest["failures"].append(result)
                    except Exception as e:
                        manifest["failures"].append(
                            {
                                "url": asset.get("url"),
                                "category": asset.get("category"),
                                "status": "failed",
                                "error": str(e),
                            }
                        )

            manifest["summary"] = {
                "downloaded_count": len(manifest["downloads"]),
                "failed_count": len(manifest["failures"]),
                "skipped_count": len(manifest["skipped"]),
                "skipped_by_limit": max(0, len(assets) - len(limited_assets)),
                "categories": {},
            }
            for item in manifest["downloads"]:
                category = item["category"]
                manifest["summary"]["categories"][category] = (
                    manifest["summary"]["categories"].get(category, 0) + 1
                )

            manifest_path = destination / "manifest.json"
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)

            result = {
                "manifest_path": str(manifest_path.absolute()),
                "output_dir": str(destination.absolute()),
                "selector": selector,
                "url": getattr(tab, "url", "unknown"),
                "summary": manifest["summary"],
            }
            return result
        except Exception as e:
            debug_logger.log_error("file_element_cloner", "download_assets_to_folder", e)
            return {"error": str(e)}

    async def extract_related_files_to_file(
        self,
        tab,
        output_path: str,
        element=None,
        selector: str = None,
        analyze_css: bool = True,
        analyze_js: bool = True,
        follow_imports: bool = False,
        max_depth: int = 2,
        instance_id: str = None,
        client_roots=None,
    ) -> Dict[str, Any]:
        """
        Extract related files and save to *output_path*.

        Args:
            tab: Browser tab object.
            output_path: Absolute destination path inside the workspace.
            element: DOM element object (optional).
            selector: CSS selector for the element.
            analyze_css: Analyze CSS files.
            analyze_js: Analyze JS files.
            follow_imports: Follow imports.
            max_depth: Maximum depth for import following.
            instance_id: Unused — kept for API compatibility.

        Returns:
            Dict with file_path and extraction summary.
        """
        try:
            file_data = await element_cloner.extract_related_files(
                tab, element, selector, analyze_css, analyze_js, follow_imports, max_depth
            )
            file_data["_metadata"] = {
                "extraction_type": "related_files",
                "selector": selector,
                "timestamp": datetime.now().isoformat(),
                "options": {
                    "analyze_css": analyze_css,
                    "analyze_js": analyze_js,
                    "follow_imports": follow_imports,
                    "max_depth": max_depth,
                },
            }
            file_path = self._save_to_file(file_data, output_path, client_roots)
            debug_logger.log_info(
                "file_element_cloner",
                "extract_related_files_to_file",
                f"Saved related files data to {file_path}",
            )
            return {
                **self._path_metadata(file_path),
                "extraction_type": "related_files",
                "selector": selector,
                "summary": {
                    "stylesheets_count": len(file_data.get("stylesheets", [])),
                    "scripts_count": len(file_data.get("scripts", [])),
                    "imports_count": len(file_data.get("imports", [])),
                    "modules_count": len(file_data.get("modules", [])),
                },
            }
        except Exception as e:
            debug_logger.log_error("file_element_cloner", "extract_related_files_to_file", e)
            return {"error": str(e)}

    async def clone_element_complete_to_file(
        self,
        tab,
        output_path: str,
        element=None,
        selector: str = None,
        extraction_options: Dict[str, Any] = None,
        instance_id: str = None,
        client_roots=None,
    ) -> Dict[str, Any]:
        """
        Master extraction: collects all element data and saves to *output_path*.

        Args:
            tab: Browser tab object.
            output_path: Absolute destination path inside the workspace.
            element: DOM element object (optional).
            selector: CSS selector for the element.
            extraction_options: Extraction options dict.
            instance_id: Unused — kept for API compatibility.

        Returns:
            Dict with file_path and extraction summary.
        """
        try:
            complete_data = await element_cloner.clone_element_complete(
                tab, element, selector, extraction_options
            )
            if "error" in complete_data:
                return complete_data
            complete_data["_metadata"] = {
                "extraction_type": "complete_clone",
                "selector": selector,
                "timestamp": datetime.now().isoformat(),
                "extraction_options": extraction_options,
            }
            file_path = self._save_to_file(complete_data, output_path, client_roots)
            summary = {
                **self._path_metadata(file_path),
                "extraction_type": "complete_clone",
                "selector": selector,
                "url": complete_data.get("url"),
                "components": {},
            }
            if "styles" in complete_data:
                styles = complete_data["styles"]
                summary["components"]["styles"] = {
                    "computed_styles_count": len(styles.get("computed_styles", {})),
                    "css_rules_count": len(styles.get("css_rules", [])),
                    "pseudo_elements_count": len(styles.get("pseudo_elements", {})),
                }
            if "structure" in complete_data:
                structure = complete_data["structure"]
                summary["components"]["structure"] = {
                    "tag_name": structure.get("tag_name"),
                    "attributes_count": len(structure.get("attributes", {})),
                    "children_count": len(structure.get("children", [])),
                }
            if "events" in complete_data:
                events = complete_data["events"]
                summary["components"]["events"] = {
                    "inline_handlers_count": len(events.get("inline_handlers", [])),
                    "detected_frameworks": events.get("detected_frameworks", []),
                }
            if "animations" in complete_data:
                animations = complete_data["animations"]
                summary["components"]["animations"] = {
                    "has_animations": animations.get("animations", {}).get("animation_name", "none")
                    != "none",
                    "keyframes_count": len(animations.get("keyframes", [])),
                }
            if "assets" in complete_data:
                assets = complete_data["assets"]
                summary["components"]["assets"] = {
                    "images_count": len(assets.get("images", [])),
                    "background_images_count": len(assets.get("background_images", [])),
                }
            if "related_files" in complete_data:
                files = complete_data["related_files"]
                summary["components"]["related_files"] = {
                    "stylesheets_count": len(files.get("stylesheets", [])),
                    "scripts_count": len(files.get("scripts", [])),
                }
            debug_logger.log_info(
                "file_element_cloner",
                "clone_complete_to_file",
                f"Saved complete clone data to {file_path}",
            )
            return summary
        except Exception as e:
            debug_logger.log_error("file_element_cloner", "clone_complete_to_file", e)
            return {"error": str(e)}


# Global singleton — no output_dir needed since all paths are caller-supplied
file_based_element_cloner = FileBasedElementCloner()
