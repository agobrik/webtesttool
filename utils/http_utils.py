"""HTTP utility functions"""

import httpx
from typing import Dict, Optional, Any
from urllib.parse import urljoin, urlparse


class HTTPUtils:
    """HTTP utility functions"""

    @staticmethod
    async def make_request(
        url: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
        timeout: int = 30,
        allow_redirects: bool = True,
        verify_ssl: bool = False
    ) -> httpx.Response:
        """
        Make HTTP request with error handling

        Args:
            url: Target URL
            method: HTTP method
            data: Request data
            headers: Request headers
            cookies: Request cookies
            timeout: Request timeout
            allow_redirects: Follow redirects
            verify_ssl: Verify SSL certificates

        Returns:
            HTTP response
        """
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=allow_redirects,
            verify=verify_ssl
        ) as client:
            response = await client.request(
                method=method.upper(),
                url=url,
                data=data,
                headers=headers or {},
                cookies=cookies or {}
            )
            return response

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def normalize_url(url: str, base_url: Optional[str] = None) -> str:
        """Normalize URL"""
        if base_url:
            return urljoin(base_url, url)
        return url

    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc

    @staticmethod
    def is_same_domain(url1: str, url2: str) -> bool:
        """Check if two URLs are from same domain"""
        return HTTPUtils.extract_domain(url1) == HTTPUtils.extract_domain(url2)
