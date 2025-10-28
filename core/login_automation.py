"""
Advanced Login Automation with Playwright
Handles complex login scenarios including form-based, OAuth, and session management
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Optional, Any, List
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from loguru import logger
import pickle


class LoginAutomation:
    """
    Advanced Login Automation
    Handles browser-based login with session persistence
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Login Automation

        Args:
            config: Login configuration
        """
        self.config = config
        self.login_url = config.get('login_url')
        self.username = config.get('username')
        self.password = config.get('password')
        self.username_selector = config.get('username_selector', 'input[name="username"], input[type="email"], input[name="email"]')
        self.password_selector = config.get('password_selector', 'input[name="password"], input[type="password"]')
        self.submit_selector = config.get('submit_selector', 'button[type="submit"], input[type="submit"], button:has-text("Login"), button:has-text("Sign in")')
        self.success_indicator = config.get('success_indicator', None)  # URL or element to check after login
        self.wait_after_login = config.get('wait_after_login', 2000)  # milliseconds

        # Session persistence
        self.session_file = Path("data/sessions") / f"{self._sanitize_url(self.login_url)}.json"
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.cookies: List[Dict] = []
        self.storage_state: Optional[Dict] = None

    def _sanitize_url(self, url: str) -> str:
        """Sanitize URL for use as filename"""
        import re
        return re.sub(r'[^\w\-_]', '_', url)

    async def perform_login(self, headless: bool = True) -> bool:
        """
        Perform automated login

        Args:
            headless: Run browser in headless mode

        Returns:
            True if login successful
        """
        try:
            async with async_playwright() as p:
                # Launch browser
                self.browser = await p.chromium.launch(headless=headless)
                self.context = await self.browser.new_context()
                page = await self.context.new_page()

                logger.info(f"Navigating to login page: {self.login_url}")
                await page.goto(self.login_url, wait_until='networkidle')

                # Wait for login form
                await page.wait_for_selector(self.username_selector, timeout=10000)

                # Fill username
                logger.info("Filling username/email")
                await page.fill(self.username_selector, self.username)

                # Fill password
                logger.info("Filling password")
                await page.fill(self.password_selector, self.password)

                # Click submit button
                logger.info("Clicking submit button")
                async with page.expect_navigation(wait_until='networkidle', timeout=15000):
                    await page.click(self.submit_selector)

                # Wait a bit for any redirects or AJAX
                await asyncio.sleep(self.wait_after_login / 1000)

                # Check if login was successful
                success = await self._verify_login_success(page)

                if success:
                    # Save session
                    await self._save_session()
                    logger.info("✅ Login successful!")
                    return True
                else:
                    logger.error("❌ Login failed - could not verify success")
                    return False

        except Exception as e:
            logger.error(f"Login automation error: {str(e)}")
            return False
        finally:
            if self.browser:
                await self.browser.close()

    async def _verify_login_success(self, page: Page) -> bool:
        """Verify if login was successful"""
        try:
            # Method 1: Check if URL changed (redirect after login)
            current_url = page.url
            if current_url != self.login_url and 'login' not in current_url.lower():
                logger.debug(f"URL changed to: {current_url}")
                return True

            # Method 2: Check for success indicator
            if self.success_indicator:
                if self.success_indicator.startswith('http'):
                    # URL-based check
                    if self.success_indicator in current_url:
                        return True
                else:
                    # Element-based check
                    try:
                        await page.wait_for_selector(self.success_indicator, timeout=5000)
                        return True
                    except:
                        pass

            # Method 3: Check for common error messages
            error_selectors = [
                'text=/invalid|error|failed|incorrect/i',
                '.error, .alert-danger, .alert-error',
                '[role="alert"]'
            ]

            for selector in error_selectors:
                try:
                    error_elem = await page.query_selector(selector)
                    if error_elem:
                        error_text = await error_elem.inner_text()
                        if error_text and len(error_text) > 0:
                            logger.warning(f"Possible error message: {error_text[:100]}")
                            return False
                except:
                    pass

            # Method 4: Check if login form is still visible
            try:
                login_form = await page.query_selector(self.username_selector)
                if not login_form:
                    # Login form disappeared, likely successful
                    return True
            except:
                pass

            # If we can't determine, assume success if no errors found
            logger.warning("Could not definitively verify login success, assuming success")
            return True

        except Exception as e:
            logger.error(f"Error verifying login: {str(e)}")
            return False

    async def _save_session(self):
        """Save session cookies and storage state"""
        try:
            if self.context:
                # Get cookies
                self.cookies = await self.context.cookies()

                # Get storage state (includes localStorage, sessionStorage, cookies)
                self.storage_state = await self.context.storage_state()

                # Save to file
                session_data = {
                    'cookies': self.cookies,
                    'storage_state': self.storage_state,
                    'timestamp': asyncio.get_event_loop().time()
                }

                with open(self.session_file, 'w') as f:
                    json.dump(session_data, f, indent=2)

                logger.info(f"Session saved to {self.session_file}")

        except Exception as e:
            logger.error(f"Error saving session: {str(e)}")

    async def load_session(self) -> bool:
        """
        Load previously saved session

        Returns:
            True if session loaded successfully
        """
        try:
            if not self.session_file.exists():
                logger.info("No saved session found")
                return False

            with open(self.session_file, 'r') as f:
                session_data = json.load(f)

            self.cookies = session_data.get('cookies', [])
            self.storage_state = session_data.get('storage_state')

            # Check if session is not too old (e.g., 24 hours)
            timestamp = session_data.get('timestamp', 0)
            current_time = asyncio.get_event_loop().time()
            age_hours = (current_time - timestamp) / 3600

            if age_hours > 24:
                logger.warning(f"Session is {age_hours:.1f} hours old, might be expired")

            logger.info(f"Loaded session with {len(self.cookies)} cookies")
            return True

        except Exception as e:
            logger.error(f"Error loading session: {str(e)}")
            return False

    async def apply_session_to_context(self, context: BrowserContext):
        """
        Apply saved session to a browser context

        Args:
            context: Playwright browser context
        """
        try:
            if self.storage_state:
                # Add cookies
                if self.cookies:
                    await context.add_cookies(self.cookies)
                    logger.info(f"Applied {len(self.cookies)} cookies to context")

                # Note: storage_state (localStorage, sessionStorage) needs to be set when creating context
                logger.info("Session applied to browser context")
            else:
                logger.warning("No session state available to apply")

        except Exception as e:
            logger.error(f"Error applying session: {str(e)}")

    def get_cookies_dict(self) -> Dict[str, str]:
        """Get cookies as a simple dict for httpx/aiohttp"""
        return {cookie['name']: cookie['value'] for cookie in self.cookies}

    def export_cookies_for_httpx(self) -> Dict[str, str]:
        """Export cookies in format suitable for httpx"""
        return self.get_cookies_dict()

    async def interactive_login(self, headless: bool = False) -> bool:
        """
        Interactive login - opens browser and waits for user to login manually

        Args:
            headless: Run browser in headless mode (False for interactive)

        Returns:
            True if session saved successfully
        """
        try:
            async with async_playwright() as p:
                # Launch browser in non-headless mode for user interaction
                self.browser = await p.chromium.launch(headless=headless, slow_mo=50)
                self.context = await self.browser.new_context()
                page = await self.context.new_page()

                logger.info(f"🌐 Opening browser - Please login manually")
                await page.goto(self.login_url)

                # Wait for user to complete login
                print("\n" + "="*60)
                print("🔐 MANUAL LOGIN MODE")
                print("="*60)
                print("1. Complete the login process in the browser window")
                print("2. Press ENTER here when you're logged in successfully")
                print("="*60 + "\n")

                # Wait for user confirmation
                await asyncio.get_event_loop().run_in_executor(None, input, "Press ENTER when logged in: ")

                # Save the session
                await self._save_session()

                logger.info("✅ Session saved! You can now use automated scanning")
                return True

        except Exception as e:
            logger.error(f"Interactive login error: {str(e)}")
            return False
        finally:
            if self.browser:
                await self.browser.close()

    async def verify_session_valid(self) -> bool:
        """
        Verify if saved session is still valid

        Returns:
            True if session is valid
        """
        try:
            if not await self.load_session():
                return False

            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=True)

                # Create context with saved session
                if self.storage_state:
                    self.context = await self.browser.new_context(storage_state=self.storage_state)
                else:
                    self.context = await self.browser.new_context()
                    await self.apply_session_to_context(self.context)

                page = await self.context.new_page()

                # Try to access a protected page (not login page)
                base_url = '/'.join(self.login_url.split('/')[:3])  # Get base URL
                await page.goto(base_url, wait_until='networkidle')

                # Check if redirected to login
                if 'login' in page.url.lower():
                    logger.info("Session expired - redirected to login")
                    return False

                logger.info("✅ Session is still valid")
                return True

        except Exception as e:
            logger.error(f"Error verifying session: {str(e)}")
            return False
        finally:
            if self.browser:
                await self.browser.close()

    def delete_session(self):
        """Delete saved session"""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
                logger.info("Session deleted")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            return False
