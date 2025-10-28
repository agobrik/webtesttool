"""Validation utilities"""

import re
from urllib.parse import urlparse
from typing import Optional


class URLValidator:
    """URL validation utilities"""

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Check if URL is valid

        Args:
            url: URL to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except Exception:
            return False

    @staticmethod
    def is_internal_url(url: str, base_url: str) -> bool:
        """
        Check if URL is internal (same domain as base)

        Args:
            url: URL to check
            base_url: Base URL to compare against

        Returns:
            True if internal, False otherwise
        """
        try:
            url_parsed = urlparse(url)
            base_parsed = urlparse(base_url)
            return url_parsed.netloc == base_parsed.netloc
        except Exception:
            return False

    @staticmethod
    def extract_scheme(url: str) -> Optional[str]:
        """Extract scheme from URL"""
        try:
            return urlparse(url).scheme
        except Exception:
            return None

    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc
        except Exception:
            return None

    @staticmethod
    def extract_path(url: str) -> Optional[str]:
        """Extract path from URL"""
        try:
            return urlparse(url).path
        except Exception:
            return None


class InputValidator:
    """Input validation utilities"""

    @staticmethod
    def is_email(value: str) -> bool:
        """Check if value is valid email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))

    @staticmethod
    def is_ip_address(value: str) -> bool:
        """Check if value is valid IP address"""
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(pattern, value))

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file operations"""
        # Remove or replace unsafe characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        return filename
