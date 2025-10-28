"""
Advanced Authentication Manager
Supports multiple authentication types and session management
"""

import base64
import jwt
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import httpx
from loguru import logger


class AuthManager:
    """
    Advanced Authentication Manager
    Handles various authentication methods
    """

    def __init__(self, auth_config: Dict[str, Any]):
        """
        Initialize AuthManager

        Args:
            auth_config: Authentication configuration
        """
        self.auth_type = auth_config.get('type', 'none')
        self.username = auth_config.get('username')
        self.password = auth_config.get('password')
        self.token = auth_config.get('token')
        self.api_key = auth_config.get('api_key')
        self.custom_headers = auth_config.get('custom_headers', {})
        self.session_cookie = None
        self.csrf_token = None

    async def authenticate(self, client: httpx.AsyncClient, login_url: Optional[str] = None) -> bool:
        """
        Perform authentication

        Args:
            client: HTTP client
            login_url: Login endpoint URL

        Returns:
            True if authentication successful
        """
        if self.auth_type == 'none':
            return True

        elif self.auth_type == 'basic':
            return self._setup_basic_auth(client)

        elif self.auth_type == 'bearer':
            return self._setup_bearer_auth(client)

        elif self.auth_type == 'api_key':
            return self._setup_api_key_auth(client)

        elif self.auth_type == 'digest':
            return self._setup_digest_auth(client)

        elif self.auth_type == 'oauth2':
            return await self._setup_oauth2(client)

        elif self.auth_type == 'form':
            return await self._setup_form_auth(client, login_url)

        elif self.auth_type == 'jwt':
            return self._setup_jwt_auth(client)

        else:
            logger.warning(f"Unknown auth type: {self.auth_type}")
            return False

    def _setup_basic_auth(self, client: httpx.AsyncClient) -> bool:
        """Setup HTTP Basic Authentication"""
        if not self.username or not self.password:
            logger.error("Username and password required for basic auth")
            return False

        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()

        client.headers['Authorization'] = f"Basic {encoded}"
        logger.info("Basic authentication configured")
        return True

    def _setup_bearer_auth(self, client: httpx.AsyncClient) -> bool:
        """Setup Bearer Token Authentication"""
        if not self.token:
            logger.error("Token required for bearer auth")
            return False

        client.headers['Authorization'] = f"Bearer {self.token}"
        logger.info("Bearer token authentication configured")
        return True

    def _setup_api_key_auth(self, client: httpx.AsyncClient) -> bool:
        """Setup API Key Authentication"""
        if not self.api_key:
            logger.error("API key required")
            return False

        # API key can be in header or query param
        client.headers['X-API-Key'] = self.api_key
        logger.info("API key authentication configured")
        return True

    def _setup_digest_auth(self, client: httpx.AsyncClient) -> bool:
        """Setup Digest Authentication"""
        if not self.username or not self.password:
            logger.error("Username and password required for digest auth")
            return False

        # Digest auth is handled by httpx's auth parameter
        client.auth = httpx.DigestAuth(self.username, self.password)
        logger.info("Digest authentication configured")
        return True

    def _setup_jwt_auth(self, client: httpx.AsyncClient) -> bool:
        """Setup JWT Authentication"""
        if not self.token:
            # Generate JWT if credentials provided
            if self.username and self.password:
                payload = {
                    'username': self.username,
                    'exp': datetime.utcnow() + timedelta(hours=1)
                }
                # Note: In real scenario, you'd get this from the server
                self.token = jwt.encode(payload, 'secret', algorithm='HS256')

        if self.token:
            client.headers['Authorization'] = f"Bearer {self.token}"
            logger.info("JWT authentication configured")
            return True

        logger.error("JWT token not available")
        return False

    async def _setup_oauth2(self, client: httpx.AsyncClient) -> bool:
        """Setup OAuth2 Authentication"""
        # Simplified OAuth2 - in reality this would involve redirect flows
        if not self.token:
            logger.error("OAuth2 token required")
            return False

        client.headers['Authorization'] = f"Bearer {self.token}"
        logger.info("OAuth2 authentication configured")
        return True

    async def _setup_form_auth(self, client: httpx.AsyncClient, login_url: Optional[str]) -> bool:
        """Setup Form-based Authentication"""
        if not login_url:
            logger.error("Login URL required for form auth")
            return False

        if not self.username or not self.password:
            logger.error("Username and password required for form auth")
            return False

        try:
            # First, get the login page to extract CSRF token if present
            response = await client.get(login_url)

            # Try to extract CSRF token
            csrf_token = await self._extract_csrf_token(response.text)

            # Prepare login data
            login_data = {
                'username': self.username,
                'password': self.password
            }

            if csrf_token:
                login_data['csrf_token'] = csrf_token

            # Perform login
            response = await client.post(login_url, data=login_data)

            if response.status_code in [200, 302, 303]:
                # Store session cookie
                if response.cookies:
                    logger.info("Form authentication successful - session cookies obtained")
                    return True

            logger.error(f"Form authentication failed with status {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Form authentication error: {str(e)}")
            return False

    async def _extract_csrf_token(self, html: str) -> Optional[str]:
        """Extract CSRF token from HTML"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'lxml')

        # Common CSRF token patterns
        csrf_selectors = [
            'input[name="csrf_token"]',
            'input[name="_csrf"]',
            'input[name="csrf"]',
            'input[name="_token"]',
            'meta[name="csrf-token"]'
        ]

        for selector in csrf_selectors:
            element = soup.select_one(selector)
            if element:
                token = element.get('value') or element.get('content')
                if token:
                    logger.debug(f"CSRF token extracted: {token[:10]}...")
                    return token

        return None

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        headers = self.custom_headers.copy()

        if self.auth_type == 'bearer' and self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        elif self.auth_type == 'api_key' and self.api_key:
            headers['X-API-Key'] = self.api_key

        return headers

    def get_cookies(self) -> Dict[str, str]:
        """Get authentication cookies"""
        cookies = {}

        if self.session_cookie:
            cookies['session'] = self.session_cookie

        return cookies

    async def refresh_token(self, client: httpx.AsyncClient, refresh_url: str) -> bool:
        """
        Refresh authentication token

        Args:
            client: HTTP client
            refresh_url: Token refresh endpoint

        Returns:
            True if refresh successful
        """
        try:
            response = await client.post(refresh_url, json={
                'refresh_token': self.token
            })

            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                logger.info("Token refreshed successfully")
                return True

            logger.error(f"Token refresh failed with status {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return False

    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        if self.auth_type == 'none':
            return True

        if self.auth_type in ['bearer', 'jwt', 'api_key']:
            return bool(self.token or self.api_key)

        if self.auth_type in ['basic', 'digest']:
            return bool(self.username and self.password)

        if self.auth_type == 'form':
            return bool(self.session_cookie)

        return False
