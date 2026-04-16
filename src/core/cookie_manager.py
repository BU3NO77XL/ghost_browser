"""Cookie management for browser automation.

Handles Netscape cookie file parsing, domain matching, and cookie injection
into browser tabs via CDP.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import nodriver as uc

from core.debug_logger import debug_logger


def domain_matches_host(cookie_domain: str, host: str) -> bool:
    """Check if a cookie domain applies to a host."""
    if not cookie_domain or not host:
        return False

    normalized_domain = cookie_domain.lstrip(".").lower()
    normalized_host = host.lower()

    return normalized_host == normalized_domain or normalized_host.endswith(f".{normalized_domain}")


def hosts_represent_same_site(host_a: str, host_b: str) -> bool:
    """Allow exact match and subdomain/base-domain canonical redirects."""
    if not host_a or not host_b:
        return False
    return domain_matches_host(host_a, host_b) or domain_matches_host(host_b, host_a)


async def wait_for_target_host(
    tab: Any,
    target_url: str,
    max_wait_ms: int = 10000,
    poll_interval_ms: int = 200,
) -> Dict[str, Any]:
    """Wait until browser reaches the target host (or equivalent canonical host)."""
    target_host = (urlparse(target_url).hostname or "").lower()
    if not target_host:
        return {
            "matched": False,
            "reason": "invalid_target_url",
            "target_host": "",
            "current_url": "",
            "current_host": "",
        }

    loop = asyncio.get_running_loop()
    deadline = loop.time() + (max_wait_ms / 1000)
    last_url = ""
    last_host = ""

    while True:
        try:
            current_url = await tab.evaluate("window.location.href")
            if isinstance(current_url, str):
                last_url = current_url
            else:
                last_url = ""
        except Exception:
            last_url = ""

        last_host = (urlparse(last_url).hostname or "").lower()
        if hosts_represent_same_site(target_host, last_host):
            return {
                "matched": True,
                "reason": "target_host_reached",
                "target_host": target_host,
                "current_url": last_url,
                "current_host": last_host,
            }

        if loop.time() >= deadline:
            return {
                "matched": False,
                "reason": "wait_timeout",
                "target_host": target_host,
                "current_url": last_url,
                "current_host": last_host,
            }

        await asyncio.sleep(poll_interval_ms / 1000)


def parse_netscape_cookie_line(line: str) -> Optional[Dict[str, Any]]:
    """
    Parse one Netscape cookies.txt line.

    Returns a dict with:
      - cookie: fields suitable for CDP Network.setCookie
      - match_domain: canonical host/domain used for matching against target host
      - host_only: whether this cookie should only apply to the exact host
    """
    if not line:
        return None

    http_only = False
    raw_line = line.strip()

    if not raw_line:
        return None

    if raw_line.startswith("#HttpOnly_"):
        http_only = True
        raw_line = raw_line[len("#HttpOnly_") :]
    elif raw_line.startswith("#"):
        return None

    parts = raw_line.split("\t")
    if len(parts) != 7:
        return None

    domain, include_subdomains_flag, path, secure_flag, expires_at, name, value = parts

    if not domain or not name:
        return None

    secure = secure_flag.upper() == "TRUE"
    include_subdomains = include_subdomains_flag.upper() == "TRUE"
    host_only = not include_subdomains
    normalized_domain = domain.lstrip(".").lower()

    cookie_data: Dict[str, Any] = {
        "name": name,
        "value": value,
        "path": path or "/",
        "secure": secure,
        "http_only": http_only,
    }

    # Host-only cookies (include_subdomains == FALSE in Netscape format) are best
    # represented via a concrete URL so CDP creates the correct host scoping.
    # Secure cookies require an https:// URL.
    if host_only:
        cookie_data["url"] = f"https://{normalized_domain}{cookie_data['path']}"
    else:
        cookie_data["domain"] = normalized_domain

    try:
        expires_int = int(expires_at)
        if expires_int > 0:
            # nodriver expects CDP "TimeSinceEpoch", not a raw int.
            cookie_data["expires"] = uc.cdp.network.TimeSinceEpoch(expires_int)
    except (TypeError, ValueError):
        pass

    return {
        "cookie": cookie_data,
        "match_domain": normalized_domain,
        "host_only": host_only,
    }


async def inject_cookies_from_file(
    tab: Any,
    target_url: str,
    network_interceptor: Any,
    cookies_file: str = "cookies.txt",
) -> Dict[str, Any]:
    """
    Inject matching cookies from cookies.txt before navigation.

    Rules:
    - If file does not exist, continue without injection.
    - If file is empty, continue without injection.
    - If cookies exist, inject only cookies matching target URL host.

    Args:
        tab: Browser tab object.
        target_url: URL to navigate to (used for host matching).
        network_interceptor: NetworkInterceptor instance for set_cookie.
        cookies_file: Path to Netscape cookies.txt file.

    Returns:
        Dict with injection result (attempted, reason, cookies_injected, etc.).
    """
    target_host = (urlparse(target_url).hostname or "").lower()
    if not target_host:
        return {
            "attempted": False,
            "reason": "invalid_target_url",
            "file_path": cookies_file,
            "cookies_injected": 0,
        }

    file_path = Path(cookies_file).expanduser()
    if not file_path.is_absolute():
        # Try CWD first, then fall back to project root so "cookies.txt"
        # works even if server is started from src/ or elsewhere.
        cwd_candidate = (Path.cwd() / file_path).resolve()
        # Use the debug_logger's module location to find project root
        import cookie_manager

        project_root = Path(cookie_manager.__file__).resolve().parent.parent
        repo_root_candidate = (project_root / file_path).resolve()
        if cwd_candidate.exists():
            file_path = cwd_candidate
        elif repo_root_candidate.exists():
            file_path = repo_root_candidate

    if not file_path.exists():
        debug_logger.log_info(
            "cookie_manager",
            "inject_cookies",
            f"Cookie file not found, skipping injection: {file_path}",
        )
        return {
            "attempted": False,
            "reason": "file_not_found",
            "file_path": str(file_path),
            "cookies_injected": 0,
        }

    try:
        content = file_path.read_text(encoding="utf-8-sig", errors="ignore")
    except Exception as read_error:
        debug_logger.log_warning(
            "cookie_manager",
            "inject_cookies",
            f"Failed to read cookie file, skipping injection: {read_error}",
        )
        return {
            "attempted": False,
            "reason": "file_read_error",
            "file_path": str(file_path),
            "cookies_injected": 0,
        }

    if not content.strip():
        debug_logger.log_info(
            "cookie_manager",
            "inject_cookies",
            f"Cookie file is empty, skipping injection: {file_path}",
        )
        return {
            "attempted": False,
            "reason": "file_empty",
            "file_path": str(file_path),
            "cookies_injected": 0,
        }

    parsed_cookies: List[Dict[str, Any]] = []
    for line in content.splitlines():
        parsed = parse_netscape_cookie_line(line)
        if not parsed:
            continue
        match_domain = (parsed.get("match_domain") or "").lower()
        host_only = bool(parsed.get("host_only"))
        if host_only:
            if match_domain and match_domain == target_host:
                parsed_cookies.append(parsed)
        else:
            if domain_matches_host(match_domain, target_host):
                parsed_cookies.append(parsed)

    if not parsed_cookies:
        return {
            "attempted": True,
            "reason": "no_matching_cookies",
            "file_path": str(file_path),
            "cookies_injected": 0,
        }

    injected_count = 0
    for cookie in parsed_cookies:
        try:
            await network_interceptor.set_cookie(tab, cookie["cookie"])
            injected_count += 1
        except Exception as cookie_error:
            debug_logger.log_warning(
                "cookie_manager",
                "inject_cookies",
                f"Failed to inject cookie '{cookie.get('cookie', {}).get('name', 'unknown')}': {cookie_error}",
            )

    return {
        "attempted": True,
        "reason": "cookies_processed",
        "file_path": str(file_path),
        "cookies_matched": len(parsed_cookies),
        "cookies_injected": injected_count,
    }
