"""Handler for manual login scenarios - allows AI agent to pause and wait for user login.

Key design: when navigate() detects a login page, it registers the instance here.
The AI agent then asks the user to log in manually and calls confirm_manual_login
with the SAME instance_id to resume control of the SAME browser window.
"""


from typing import Dict, Optional, Any
from datetime import datetime
from pathlib import Path

import nodriver as uc
from nodriver import Tab

from debug_logger import debug_logger


class ManualLoginHandler:
    """Manages manual login scenarios where AI agent needs to wait for user interaction.
    
    Lifecycle:
    1. navigate() detects login page -> calls register_pending_login()
    2. AI agent tells user to log in manually in the open browser
    3. User logs in and tells the AI agent
    4. AI agent calls confirm_manual_login tool -> calls confirm_login()
    5. confirm_login() checks auth on the SAME tab, saves cookies, returns success
    """
    
    def __init__(self):
        # Instances waiting for manual login: {instance_id: {tab, url, registered_at, ...}}
        self._pending_logins: Dict[str, dict] = {}
    
    def register_pending_login(
        self,
        instance_id: str,
        tab: Tab,
        url: str,
        cookies_file: str = "cookies.txt"
    ) -> None:
        """
        Register a browser instance as waiting for manual login.
        Called by navigate() when it detects the page is a login page.
        
        Args:
            instance_id: The browser instance ID (same one returned by spawn_browser)
            tab: The active browser tab (kept alive for the user to interact with)
            url: The URL that triggered login detection
            cookies_file: Path to cookies file for saving after login
        """
        self._pending_logins[instance_id] = {
            'tab': tab,
            'url': url,
            'cookies_file': cookies_file,
            'registered_at': datetime.now().isoformat(),
            'status': 'waiting_for_user',
        }
        debug_logger.log_info(
            "manual_login_handler",
            "register_pending_login",
            f"Instance {instance_id} registered as pending login. URL: {url}"
        )
    
    def is_pending_login(self, instance_id: str) -> bool:
        """Check if an instance is waiting for manual login."""
        return instance_id in self._pending_logins
    
    def get_pending_info(self, instance_id: str) -> Optional[dict]:
        """Get pending login info for an instance (without the tab object)."""
        info = self._pending_logins.get(instance_id)
        if not info:
            return None
        return {
            'instance_id': instance_id,
            'url': info['url'],
            'registered_at': info['registered_at'],
            'status': info['status'],
        }
    
    def get_all_pending(self) -> list:
        """Get all instances waiting for manual login."""
        return [
            self.get_pending_info(iid)
            for iid in self._pending_logins
        ]
    
    async def confirm_login(
        self,
        instance_id: str,
        tab: Tab,
        cookies_file: str = None,
    ) -> Dict[str, Any]:
        """
        Confirm that manual login was completed on the given instance.
        Checks authentication status and saves cookies if successful.
        
        This is called by the confirm_manual_login MCP tool. The tab is passed
        from browser_manager to ensure we use the SAME browser instance.
        
        Args:
            instance_id: The browser instance ID
            tab: The active tab from browser_manager (same instance)
            cookies_file: Override cookies file path (uses pending registration default if None)
            
        Returns:
            Dict with success status, authentication details, and cookie save info
        """
        pending = self._pending_logins.get(instance_id)
        if cookies_file is None:
            cookies_file = pending.get('cookies_file', 'cookies.txt') if pending else "cookies.txt"
        
        try:
            # Step 1: Check if still on login page
            is_login = await self.detect_login_page(tab)
            
            # Step 2: Check authentication indicators
            auth_status = await self.check_authentication_status(tab)
            
            current_url = await tab.evaluate("window.location.href")
            
            if is_login and not auth_status.get('is_authenticated', False):
                debug_logger.log_warning(
                    "manual_login_handler",
                    "confirm_login",
                    f"Instance {instance_id} still appears to be on login page: {current_url}"
                )
                return {
                    'success': False,
                    'message': 'Ainda parece estar na página de login. Verifique se o login foi concluído e tente novamente.',
                    'current_url': current_url,
                    'is_login_page': True,
                    'auth_indicators': auth_status.get('indicators', {}),
                    'instance_id': instance_id,
                }
            
            # Step 3: Login confirmed — save cookies
            cookie_save_result = await self._save_cookies_from_browser(tab, cookies_file)
            
            # Step 4: Clean up pending entry
            if instance_id in self._pending_logins:
                del self._pending_logins[instance_id]
            
            debug_logger.log_info(
                "manual_login_handler",
                "confirm_login",
                f"Login confirmed for instance {instance_id}. URL: {current_url}. "
                f"Cookies saved: {cookie_save_result.get('cookies_saved', 0)}"
            )
            
            return {
                'success': True,
                'message': 'Login confirmado com sucesso! Cookies salvos. O agente pode continuar usando esta mesma instância.',
                'current_url': current_url,
                'is_login_page': False,
                'auth_indicators': auth_status.get('indicators', {}),
                'cookies_saved': cookie_save_result,
                'instance_id': instance_id,
            }
            
        except Exception as e:
            debug_logger.log_error("manual_login_handler", "confirm_login", e)
            return {
                'success': False,
                'message': f'Erro ao confirmar login: {str(e)}',
                'instance_id': instance_id,
            }

    async def detect_login_page(self, tab: Tab) -> bool:
        """
        Detect if current page is a login page by checking URL and form elements.
        
        Args:
            tab: Browser tab to check
            
        Returns:
            bool: True if on login page, False otherwise
        """
        try:
            current_url = await tab.evaluate("window.location.href")
            
            # Common login page indicators in URL
            login_url_indicators = [
                'login', 'signin', 'sign-in', 'auth', 'authenticate',
                'log-in', 'logon', 'log_in', 'sso', 'oauth',
                'accounts.google.com', 'login.microsoftonline.com',
                'login.live.com', 'appleid.apple.com',
            ]
            
            url_lower = current_url.lower()
            url_match = any(indicator in url_lower for indicator in login_url_indicators)
            
            if url_match:
                debug_logger.log_info(
                    "manual_login_handler",
                    "detect_login_page",
                    f"Login page detected by URL: {current_url}"
                )
                return True
            
            # Check for common login form elements in the DOM
            has_login_form = await tab.evaluate("""
                (() => {
                    // Check for password input
                    const passwordInputs = document.querySelectorAll('input[type="password"]');
                    if (passwordInputs.length > 0) return true;
                    
                    // Check for login-related forms
                    const forms = document.querySelectorAll('form');
                    for (const form of forms) {
                        const action = (form.action || '').toLowerCase();
                        const id = (form.id || '').toLowerCase();
                        const cls = (form.className || '').toLowerCase();
                        if (action.includes('login') || action.includes('signin') || action.includes('auth') ||
                            id.includes('login') || id.includes('signin') ||
                            cls.includes('login') || cls.includes('signin')) {
                            return true;
                        }
                    }
                    
                    // Check for login/signin buttons
                    const allClickables = Array.from(document.querySelectorAll('button, input[type="submit"], a[role="button"]'));
                    const hasLoginButton = allClickables.some(el => {
                        const text = (el.textContent || el.value || '').toLowerCase().trim();
                        return (
                            text === 'login' || text === 'log in' || text === 'sign in' ||
                            text === 'signin' || text === 'entrar' || text === 'fazer login' ||
                            text === 'iniciar sessão'
                        );
                    });
                    if (hasLoginButton) return true;
                    
                    // Check for email/username inputs combined with submit
                    const emailInputs = document.querySelectorAll(
                        'input[type="email"], input[name*="email"], input[name*="username"], ' +
                        'input[name*="user"], input[autocomplete="username"], input[autocomplete="email"]'
                    );
                    const submitButtons = document.querySelectorAll('button[type="submit"], input[type="submit"]');
                    if (emailInputs.length > 0 && submitButtons.length > 0) return true;
                    
                    return false;
                })()
            """)
            
            if has_login_form:
                debug_logger.log_info(
                    "manual_login_handler",
                    "detect_login_page",
                    "Login page detected by form elements"
                )
                return True
            
            return False
            
        except Exception as e:
            debug_logger.log_error("manual_login_handler", "detect_login_page", e)
            return False
    
    async def check_authentication_status(self, tab: Tab) -> Dict[str, Any]:
        """
        Check if user is authenticated by looking for common indicators.
        
        Args:
            tab: Browser tab to check
            
        Returns:
            Dict with authentication status, confidence, and indicator details
        """
        try:
            current_url = await tab.evaluate("window.location.href")
            
            auth_check = await tab.evaluate("""
                (() => {
                    const indicators = {
                        hasUserMenu: false,
                        hasLogoutButton: false,
                        hasProfileLink: false,
                        hasAuthToken: false,
                        hasSessionCookie: false,
                        hasDashboardContent: false
                    };
                    
                    // Check for user menu/profile/avatar elements
                    const userMenuSelectors = [
                        '[class*="user-menu"]', '[class*="profile-menu"]',
                        '[class*="account-menu"]', '[id*="user-menu"]',
                        '[class*="avatar"]', '[class*="user-avatar"]',
                        '[class*="profile-pic"]', '[data-testid*="avatar"]',
                        '[aria-label*="account"]', '[aria-label*="profile"]'
                    ];
                    indicators.hasUserMenu = userMenuSelectors.some(sel => 
                        document.querySelector(sel) !== null
                    );
                    
                    // Check for logout/signout buttons
                    const allElements = Array.from(document.querySelectorAll('button, a, [role="menuitem"]'));
                    indicators.hasLogoutButton = allElements.some(el => {
                        const text = (el.textContent || '').toLowerCase();
                        const href = (el.href || '').toLowerCase();
                        return text.includes('logout') || text.includes('sign out') || 
                               text.includes('log out') || text.includes('sair') ||
                               text.includes('desconectar') || text.includes('encerrar sessão') ||
                               href.includes('logout') || href.includes('signout');
                    });
                    
                    // Check for profile/account links
                    const links = Array.from(document.querySelectorAll('a'));
                    indicators.hasProfileLink = links.some(link => {
                        const href = (link.href || '').toLowerCase();
                        const text = (link.textContent || '').toLowerCase();
                        return href.includes('profile') || href.includes('account') || href.includes('settings') ||
                               href.includes('minha-conta') || href.includes('meu-perfil') ||
                               text.includes('my account') || text.includes('minha conta');
                    });
                    
                    // Check localStorage for auth tokens
                    try {
                        const storageKeys = Object.keys(localStorage);
                        indicators.hasAuthToken = storageKeys.some(key => {
                            const k = key.toLowerCase();
                            return k.includes('token') || k.includes('auth') || 
                                   k.includes('session') || k.includes('jwt') ||
                                   k.includes('access_token') || k.includes('id_token');
                        });
                    } catch (e) {}
                    
                    // Check for session cookies
                    const cookieStr = document.cookie.toLowerCase();
                    indicators.hasSessionCookie = cookieStr.includes('session') ||
                                                  cookieStr.includes('auth') ||
                                                  cookieStr.includes('token') ||
                                                  cookieStr.includes('logged_in') ||
                                                  cookieStr.includes('user');
                    
                    // Check for dashboard/main content (not a login form)
                    const hasDashboard = document.querySelector(
                        '[class*="dashboard"], [class*="home-content"], [class*="main-content"], ' + 
                        '[class*="feed"], [class*="inbox"], [class*="workspace"], nav[class*="main"]'
                    ) !== null;
                    indicators.hasDashboardContent = hasDashboard;
                    
                    return indicators;
                })()
            """)
            
            # Calculate confidence score
            confidence_score = sum([
                auth_check.get('hasUserMenu', False),
                auth_check.get('hasLogoutButton', False),
                auth_check.get('hasProfileLink', False),
                auth_check.get('hasAuthToken', False),
                auth_check.get('hasSessionCookie', False),
                auth_check.get('hasDashboardContent', False),
            ])
            
            # Authenticated if at least 1 strong indicator or 2 weak indicators
            is_authenticated = (
                auth_check.get('hasLogoutButton', False) or  # strong signal
                auth_check.get('hasDashboardContent', False) or  # strong signal
                confidence_score >= 2  # multiple weak signals
            )
            
            return {
                'is_authenticated': is_authenticated,
                'confidence_score': confidence_score,
                'max_score': 6,
                'indicators': auth_check,
                'current_url': current_url
            }
            
        except Exception as e:
            debug_logger.log_error("manual_login_handler", "check_authentication_status", e)
            return {
                'is_authenticated': False,
                'confidence_score': 0,
                'error': str(e)
            }

    async def _save_cookies_from_browser(
        self,
        tab: Tab,
        cookies_file: str = "cookies.txt"
    ) -> Dict[str, Any]:
        """
        Extract all cookies from the browser and save them to cookies.txt in Netscape format.
        This preserves cookies for future sessions so the login persists.
        
        Args:
            tab: Browser tab to extract cookies from
            cookies_file: Path to save cookies file
            
        Returns:
            Dict with save results
        """
        try:
            # Get all cookies via CDP
            cookies_response = await tab.send(uc.cdp.network.get_all_cookies())
            
            if not cookies_response:
                return {'cookies_saved': 0, 'reason': 'no_cookies_returned'}
            
            # Resolve file path
            file_path = Path(cookies_file).expanduser()
            if not file_path.is_absolute():
                cwd_candidate = (Path.cwd() / file_path).resolve()
                repo_root_candidate = (Path(__file__).resolve().parent.parent / file_path).resolve()
                if cwd_candidate.parent.exists():
                    file_path = cwd_candidate
                elif repo_root_candidate.parent.exists():
                    file_path = repo_root_candidate
            
            # Read existing cookies from file to preserve non-overlapping entries
            existing_lines = []
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8-sig", errors="ignore")
                    existing_lines = [
                        l for l in content.splitlines()
                        if l.strip() and (l.startswith('#') or l.startswith('//'))
                    ]
                except Exception:
                    pass
            
            # Build Netscape cookie lines from browser cookies
            new_cookie_set = set()  # Track (domain, name, path) to avoid duplicates
            cookie_lines = []
            
            for cookie in cookies_response:
                domain = getattr(cookie, 'domain', '') or ''
                name = getattr(cookie, 'name', '') or ''
                value = getattr(cookie, 'value', '') or ''
                path = getattr(cookie, 'path', '/') or '/'
                secure = getattr(cookie, 'secure', False)
                expires = getattr(cookie, 'expires', 0) or 0
                http_only = getattr(cookie, 'http_only', False)
                
                if not domain or not name:
                    continue
                
                cookie_key = (domain, name, path)
                if cookie_key in new_cookie_set:
                    continue
                new_cookie_set.add(cookie_key)
                
                # Netscape format: domain  include_subdomains  path  secure  expires  name  value
                # include_subdomains=TRUE when domain starts with '.' (applies to subdomains)
                # include_subdomains=FALSE when host-only (no dot prefix)
                include_subdomains_flag = "FALSE" if not domain.startswith('.') else "TRUE"
                secure_flag = "TRUE" if secure else "FALSE"
                expires_int = int(expires) if expires else 0
                
                # If http_only, prefix domain with #HttpOnly_
                domain_field = f"#HttpOnly_{domain}" if http_only else domain
                
                line = f"{domain_field}\t{include_subdomains_flag}\t{path}\t{secure_flag}\t{expires_int}\t{name}\t{value}"
                cookie_lines.append(line)
            
            # Write cookies file
            header = "# Netscape HTTP Cookie File\n# Auto-saved by stealth_browser after manual login\n# https://curl.se/docs/http-cookies.html\n\n"
            
            file_path.write_text(
                header + "\n".join(cookie_lines) + "\n",
                encoding="utf-8"
            )
            
            debug_logger.log_info(
                "manual_login_handler",
                "_save_cookies_from_browser",
                f"Saved {len(cookie_lines)} cookies to {file_path}"
            )
            
            return {
                'cookies_saved': len(cookie_lines),
                'file_path': str(file_path),
            }
            
        except Exception as e:
            debug_logger.log_error("manual_login_handler", "_save_cookies_from_browser", e)
            return {
                'cookies_saved': 0,
                'error': str(e),
            }


# Global instance
manual_login_handler = ManualLoginHandler()
