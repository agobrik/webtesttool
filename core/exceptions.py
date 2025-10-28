"""
Custom Exceptions for WebTestool
Provides structured error handling with user-friendly messages
"""

from typing import Dict, Optional, Any
from enum import Enum


class ErrorCategory(Enum):
    """Error categories for better classification"""
    CONFIGURATION = "configuration"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    MODULE = "module"
    SCANNING = "scanning"
    REPORTING = "reporting"
    DATABASE = "database"
    SYSTEM = "system"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WebTestoolError(Exception):
    """
    Base exception for all WebTestool errors

    Attributes:
        message: Error message
        details: Additional error details
        category: Error category
        severity: Error severity
        suggestion: Suggested fix
        original_error: Original exception (if wrapped)
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize WebTestool error

        Args:
            message: Error message
            details: Additional details
            category: Error category
            severity: Error severity
            suggestion: Suggested fix
            original_error: Original exception
        """
        self.message = message
        self.details = details or {}
        self.category = category
        self.severity = severity
        self.suggestion = suggestion
        self.original_error = original_error

        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary

        Returns:
            Dictionary representation of error
        """
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.value,
            'details': self.details,
            'suggestion': self.suggestion,
            'original_error': str(self.original_error) if self.original_error else None
        }

    def __str__(self) -> str:
        """String representation"""
        parts = [self.message]

        if self.details:
            parts.append(f"Details: {self.details}")

        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")

        return " | ".join(parts)


class ConfigurationError(WebTestoolError):
    """
    Configuration-related errors

    Raised when:
    - Invalid configuration file
    - Missing required configuration
    - Invalid configuration values
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            details=details,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            suggestion=suggestion,
            original_error=original_error
        )


class NetworkError(WebTestoolError):
    """
    Network connectivity errors

    Raised when:
    - Cannot connect to target
    - DNS resolution fails
    - Timeout occurs
    - Connection reset
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            details=details,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            suggestion=suggestion or "Check network connectivity and target URL",
            original_error=original_error
        )


class AuthenticationError(WebTestoolError):
    """
    Authentication failures

    Raised when:
    - Invalid credentials
    - Authentication token expired
    - Authorization denied
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            details=details,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            suggestion=suggestion or "Verify credentials in configuration",
            original_error=original_error
        )


class ValidationError(WebTestoolError):
    """
    Data validation errors

    Raised when:
    - Invalid URL format
    - Invalid parameter values
    - Schema validation fails
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            details=details,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            suggestion=suggestion,
            original_error=original_error
        )


class ModuleError(WebTestoolError):
    """
    Test module execution errors

    Raised when:
    - Module fails to load
    - Module execution fails
    - Module returns invalid result
    """

    def __init__(
        self,
        message: str,
        module_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        if module_name:
            details = details or {}
            details['module'] = module_name

        super().__init__(
            message=message,
            details=details,
            category=ErrorCategory.MODULE,
            severity=ErrorSeverity.MEDIUM,
            suggestion=suggestion,
            original_error=original_error
        )


class ScanError(WebTestoolError):
    """
    Scanning/crawling errors

    Raised when:
    - Crawler fails
    - Page fetch fails
    - Parsing errors
    """

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        if url:
            details = details or {}
            details['url'] = url

        super().__init__(
            message=message,
            details=details,
            category=ErrorCategory.SCANNING,
            severity=ErrorSeverity.MEDIUM,
            suggestion=suggestion,
            original_error=original_error
        )


class ReportGenerationError(WebTestoolError):
    """
    Report generation errors

    Raised when:
    - Report template not found
    - Report writing fails
    - Invalid report format
    """

    def __init__(
        self,
        message: str,
        report_format: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        if report_format:
            details = details or {}
            details['format'] = report_format

        super().__init__(
            message=message,
            details=details,
            category=ErrorCategory.REPORTING,
            severity=ErrorSeverity.MEDIUM,
            suggestion=suggestion,
            original_error=original_error
        )


class DatabaseError(WebTestoolError):
    """
    Database operation errors

    Raised when:
    - Database connection fails
    - Query execution fails
    - Data integrity errors
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            details=details,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            suggestion=suggestion or "Check database configuration and connectivity",
            original_error=original_error
        )


class SystemError(WebTestoolError):
    """
    System-level errors

    Raised when:
    - File system errors
    - Permission denied
    - Resource exhaustion
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            details=details,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            suggestion=suggestion,
            original_error=original_error
        )


class DependencyError(WebTestoolError):
    """
    Missing or incompatible dependencies

    Raised when:
    - Required package not installed
    - Package version incompatible
    - Browser driver missing (Playwright)
    """

    def __init__(
        self,
        message: str,
        dependency: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        if dependency:
            details = details or {}
            details['dependency'] = dependency

        super().__init__(
            message=message,
            details=details,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            suggestion=suggestion or f"Install missing dependency: pip install {dependency}",
            original_error=original_error
        )


class RateLimitError(WebTestoolError):
    """
    Rate limiting errors

    Raised when:
    - Target server returns 429
    - Too many requests
    - Need to slow down
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        if retry_after:
            details = details or {}
            details['retry_after'] = retry_after
            suggestion = suggestion or f"Wait {retry_after} seconds before retrying"

        super().__init__(
            message=message,
            details=details,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            suggestion=suggestion or "Reduce request rate or increase delay",
            original_error=original_error
        )


class TimeoutError(WebTestoolError):
    """
    Timeout errors

    Raised when:
    - Request timeout
    - Scan timeout
    - Operation takes too long
    """

    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        if timeout_seconds:
            details = details or {}
            details['timeout'] = timeout_seconds

        super().__init__(
            message=message,
            details=details,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            suggestion=suggestion or "Increase timeout value in configuration",
            original_error=original_error
        )


# Helper functions

def wrap_exception(
    original_error: Exception,
    message: Optional[str] = None,
    error_class: type = WebTestoolError,
    **kwargs
) -> WebTestoolError:
    """
    Wrap generic exception into WebTestool exception

    Args:
        original_error: Original exception
        message: Custom message (uses original if None)
        error_class: Exception class to use
        **kwargs: Additional arguments for error class

    Returns:
        WebTestool exception
    """
    msg = message or str(original_error)
    return error_class(
        message=msg,
        original_error=original_error,
        **kwargs
    )


def is_network_error(error: Exception) -> bool:
    """
    Check if error is network-related

    Args:
        error: Exception to check

    Returns:
        True if network-related
    """
    if isinstance(error, NetworkError):
        return True

    error_str = str(error).lower()
    network_keywords = [
        'connection', 'network', 'dns', 'timeout',
        'unreachable', 'refused', 'reset'
    ]

    return any(keyword in error_str for keyword in network_keywords)


def format_error_message(error: WebTestoolError) -> str:
    """
    Format error message for display

    Args:
        error: WebTestool error

    Returns:
        Formatted error message
    """
    lines = []

    # Icon based on severity
    icons = {
        ErrorSeverity.LOW: "ℹ️",
        ErrorSeverity.MEDIUM: "⚠️",
        ErrorSeverity.HIGH: "🔴",
        ErrorSeverity.CRITICAL: "🚨"
    }
    icon = icons.get(error.severity, "❌")

    # Main message
    lines.append(f"{icon} {error.__class__.__name__}: {error.message}")

    # Details
    if error.details:
        lines.append("\nDetails:")
        for key, value in error.details.items():
            lines.append(f"  • {key}: {value}")

    # Suggestion
    if error.suggestion:
        lines.append(f"\n💡 Suggestion: {error.suggestion}")

    # Original error
    if error.original_error:
        lines.append(f"\nOriginal error: {error.original_error}")

    return "\n".join(lines)
