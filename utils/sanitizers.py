"""
Input Sanitization and Validation
Prevents security vulnerabilities like SSRF, Path Traversal, Code Injection
"""

import re
from typing import Optional, List
from urllib.parse import urlparse, quote, unquote
from pathlib import Path
import ipaddress
from loguru import logger

from core.exceptions import ValidationError


class InputSanitizer:
    """
    Comprehensive input sanitization and validation

    Prevents:
    - SSRF (Server-Side Request Forgery)
    - Path Traversal
    - Code Injection
    - XSS (when generating reports)
    - Command Injection
    """

    # Dangerous patterns
    DANGEROUS_PATTERNS = [
        r'__import__',
        r'eval\s*\(',
        r'exec\s*\(',
        r'compile\s*\(',
        r'os\.system',
        r'subprocess\.',
        r'open\s*\(',
        r'file\s*\(',
    ]

    # Private IP ranges
    PRIVATE_IP_RANGES = [
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16'),
        ipaddress.ip_network('127.0.0.0/8'),
        ipaddress.ip_network('169.254.0.0/16'),
        ipaddress.ip_network('::1/128'),
        ipaddress.ip_network('fc00::/7'),
        ipaddress.ip_network('fe80::/10'),
    ]

    # Cloud metadata endpoints
    METADATA_ENDPOINTS = [
        '169.254.169.254',  # AWS, Azure, GCP
        'metadata.google.internal',
        '100.100.100.200',  # Alibaba Cloud
    ]

    @staticmethod
    def sanitize_url(url: str, allow_private: bool = False) -> str:
        """
        Sanitize and validate URL

        Args:
            url: URL to sanitize
            allow_private: Allow private/internal IPs (default: False)

        Returns:
            Sanitized URL

        Raises:
            ValidationError: If URL is invalid or dangerous
        """
        if not url or not isinstance(url, str):
            raise ValidationError(
                "URL must be a non-empty string",
                details={'url': url}
            )

        # Remove whitespace
        url = url.strip()

        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValidationError(
                f"Invalid URL format: {str(e)}",
                details={'url': url},
                original_error=e
            )

        # Validate scheme
        if parsed.scheme not in ['http', 'https']:
            raise ValidationError(
                f"Invalid URL scheme: {parsed.scheme}",
                details={'url': url, 'scheme': parsed.scheme},
                suggestion="Only HTTP and HTTPS schemes are allowed"
            )

        # Validate hostname
        if not parsed.hostname:
            raise ValidationError(
                "URL must have a hostname",
                details={'url': url}
            )

        hostname = parsed.hostname.lower()

        # Check for localhost
        if hostname in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
            if not allow_private:
                raise ValidationError(
                    "Localhost URLs are not allowed",
                    details={'url': url, 'hostname': hostname},
                    suggestion="Use allow_private=True to allow localhost"
                )

        # Check for metadata endpoints
        if hostname in InputSanitizer.METADATA_ENDPOINTS:
            raise ValidationError(
                "Cloud metadata endpoints are not allowed",
                details={'url': url, 'hostname': hostname},
                suggestion="This looks like a cloud metadata endpoint (SSRF risk)"
            )

        # Check for private IPs
        try:
            ip = ipaddress.ip_address(hostname)
            if not allow_private:
                for private_range in InputSanitizer.PRIVATE_IP_RANGES:
                    if ip in private_range:
                        raise ValidationError(
                            "Private IP addresses are not allowed",
                            details={'url': url, 'ip': str(ip)},
                            suggestion="Use allow_private=True to allow private IPs"
                        )
        except ValueError:
            # Not an IP address, check if resolves to private IP
            pass

        # Check for suspicious patterns
        if '..' in url or '//' in parsed.path:
            logger.warning(f"Suspicious URL pattern detected: {url}")

        return url

    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 255) -> str:
        """
        Sanitize filename to prevent path traversal

        Args:
            filename: Filename to sanitize
            max_length: Maximum filename length

        Returns:
            Sanitized filename

        Raises:
            ValidationError: If filename is invalid
        """
        if not filename or not isinstance(filename, str):
            raise ValidationError(
                "Filename must be a non-empty string",
                details={'filename': filename}
            )

        # Remove path separators
        filename = filename.replace('/', '_').replace('\\', '_')
        filename = filename.replace('..', '_')

        # Remove dangerous characters
        dangerous_chars = '<>:"|?*\x00'
        for char in dangerous_chars:
            filename = filename.replace(char, '_')

        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)

        # Prevent dotfiles (Unix hidden files)
        if filename.startswith('.'):
            filename = '_' + filename[1:]

        # Limit length
        if len(filename) > max_length:
            name, ext = Path(filename).stem, Path(filename).suffix
            max_name_length = max_length - len(ext)
            filename = name[:max_name_length] + ext

        # Ensure not empty after sanitization
        if not filename or filename.strip() == '':
            raise ValidationError(
                "Filename is empty after sanitization",
                details={'original': filename}
            )

        return filename

    @staticmethod
    def sanitize_path(path: str, base_dir: Optional[str] = None) -> str:
        """
        Sanitize file path to prevent directory traversal

        Args:
            path: Path to sanitize
            base_dir: Base directory to restrict to

        Returns:
            Sanitized path

        Raises:
            ValidationError: If path is dangerous
        """
        if not path or not isinstance(path, str):
            raise ValidationError(
                "Path must be a non-empty string",
                details={'path': path}
            )

        # Convert to Path object
        try:
            sanitized = Path(path).resolve()
        except Exception as e:
            raise ValidationError(
                f"Invalid path: {str(e)}",
                details={'path': path},
                original_error=e
            )

        # Check for traversal attempts
        if '..' in path or path.startswith('/') or path.startswith('\\'):
            logger.warning(f"Path traversal attempt detected: {path}")

        # If base_dir specified, ensure path is within it
        if base_dir:
            try:
                base = Path(base_dir).resolve()
                if not str(sanitized).startswith(str(base)):
                    raise ValidationError(
                        "Path is outside allowed directory",
                        details={
                            'path': path,
                            'resolved': str(sanitized),
                            'base_dir': str(base)
                        },
                        suggestion=f"Path must be within {base_dir}"
                    )
            except Exception as e:
                raise ValidationError(
                    f"Path validation failed: {str(e)}",
                    details={'path': path, 'base_dir': base_dir},
                    original_error=e
                )

        return str(sanitized)

    @staticmethod
    def sanitize_config_value(value: str) -> str:
        """
        Sanitize configuration value to prevent code injection

        Args:
            value: Configuration value

        Returns:
            Sanitized value

        Raises:
            ValidationError: If value contains dangerous patterns
        """
        if not isinstance(value, str):
            return value

        # Check for dangerous patterns
        for pattern in InputSanitizer.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValidationError(
                    f"Dangerous pattern detected in configuration value",
                    details={
                        'value': value,
                        'pattern': pattern
                    },
                    suggestion="Remove dangerous code patterns from configuration"
                )

        return value

    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Sanitize HTML to prevent XSS in reports

        Args:
            text: HTML text to sanitize

        Returns:
            Sanitized HTML
        """
        if not isinstance(text, str):
            return text

        # Escape HTML special characters
        html_escape_table = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;',
        }

        return ''.join(html_escape_table.get(c, c) for c in text)

    @staticmethod
    def sanitize_command_arg(arg: str) -> str:
        """
        Sanitize command-line argument

        Args:
            arg: Command argument

        Returns:
            Sanitized argument

        Raises:
            ValidationError: If argument contains dangerous characters
        """
        if not isinstance(arg, str):
            return arg

        # Check for shell metacharacters
        dangerous_chars = [';', '&', '|', '$', '`', '\n', '\r', '(', ')']
        for char in dangerous_chars:
            if char in arg:
                raise ValidationError(
                    "Dangerous character in command argument",
                    details={'arg': arg, 'char': char},
                    suggestion="Remove shell metacharacters"
                )

        return arg

    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email address

        Args:
            email: Email to validate

        Returns:
            Validated email

        Raises:
            ValidationError: If email is invalid
        """
        if not email or not isinstance(email, str):
            raise ValidationError(
                "Email must be a non-empty string",
                details={'email': email}
            )

        # Simple email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            raise ValidationError(
                "Invalid email format",
                details={'email': email},
                suggestion="Use format: user@example.com"
            )

        return email.lower()

    @staticmethod
    def validate_port(port: int) -> int:
        """
        Validate port number

        Args:
            port: Port number

        Returns:
            Validated port

        Raises:
            ValidationError: If port is invalid
        """
        if not isinstance(port, int):
            raise ValidationError(
                "Port must be an integer",
                details={'port': port, 'type': type(port).__name__}
            )

        if port < 1 or port > 65535:
            raise ValidationError(
                "Port must be between 1 and 65535",
                details={'port': port},
                suggestion="Use a valid port number (1-65535)"
            )

        # Warn about privileged ports
        if port < 1024:
            logger.warning(f"Using privileged port: {port}")

        return port

    @staticmethod
    def sanitize_header_value(value: str) -> str:
        """
        Sanitize HTTP header value

        Args:
            value: Header value

        Returns:
            Sanitized value

        Raises:
            ValidationError: If value contains newlines (header injection)
        """
        if not isinstance(value, str):
            return value

        # Check for header injection (CRLF)
        if '\r' in value or '\n' in value:
            raise ValidationError(
                "Header injection attempt detected",
                details={'value': value},
                suggestion="Remove CRLF characters from header value"
            )

        return value

    @staticmethod
    def sanitize_sql_identifier(identifier: str) -> str:
        """
        Sanitize SQL identifier (table/column name)

        Args:
            identifier: SQL identifier

        Returns:
            Sanitized identifier

        Raises:
            ValidationError: If identifier is invalid
        """
        if not identifier or not isinstance(identifier, str):
            raise ValidationError(
                "SQL identifier must be a non-empty string",
                details={'identifier': identifier}
            )

        # Only allow alphanumeric and underscore
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            raise ValidationError(
                "Invalid SQL identifier",
                details={'identifier': identifier},
                suggestion="Use only letters, numbers, and underscores"
            )

        # Check for SQL keywords
        sql_keywords = [
            'select', 'insert', 'update', 'delete', 'drop', 'create',
            'alter', 'table', 'from', 'where', 'union', 'exec'
        ]

        if identifier.lower() in sql_keywords:
            raise ValidationError(
                "SQL keyword cannot be used as identifier",
                details={'identifier': identifier},
                suggestion="Use a different identifier name"
            )

        return identifier


# Convenience functions

def sanitize_url(url: str, allow_private: bool = False) -> str:
    """Sanitize URL (convenience function)"""
    return InputSanitizer.sanitize_url(url, allow_private)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename (convenience function)"""
    return InputSanitizer.sanitize_filename(filename)


def sanitize_path(path: str, base_dir: Optional[str] = None) -> str:
    """Sanitize path (convenience function)"""
    return InputSanitizer.sanitize_path(path, base_dir)
