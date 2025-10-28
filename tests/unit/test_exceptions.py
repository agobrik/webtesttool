"""
Unit tests for Custom Exceptions
"""

import pytest
from core.exceptions import (
    WebTestoolError,
    ConfigurationError,
    NetworkError,
    AuthenticationError,
    ValidationError,
    ModuleError,
    ScanError,
    ErrorCategory,
    ErrorSeverity,
    wrap_exception,
    is_network_error,
    format_error_message,
)


class TestWebTestoolError:
    """Test base WebTestoolError"""

    def test_basic_error(self):
        """Test basic error creation"""
        error = WebTestoolError("Test error")

        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.category == ErrorCategory.SYSTEM
        assert error.severity == ErrorSeverity.MEDIUM

    def test_error_with_details(self):
        """Test error with details"""
        error = WebTestoolError(
            "Test error",
            details={'url': 'https://example.com', 'status': 404}
        )

        assert error.details['url'] == 'https://example.com'
        assert error.details['status'] == 404

    def test_error_with_suggestion(self):
        """Test error with suggestion"""
        error = WebTestoolError(
            "Test error",
            suggestion="Try this fix"
        )

        assert error.suggestion == "Try this fix"
        assert "Try this fix" in str(error)

    def test_error_to_dict(self):
        """Test error dictionary conversion"""
        error = WebTestoolError(
            "Test error",
            details={'key': 'value'},
            suggestion="Fix it"
        )

        error_dict = error.to_dict()

        assert error_dict['error_type'] == 'WebTestoolError'
        assert error_dict['message'] == 'Test error'
        assert error_dict['category'] == 'system'
        assert error_dict['severity'] == 'medium'
        assert error_dict['details'] == {'key': 'value'}
        assert error_dict['suggestion'] == 'Fix it'


class TestSpecificErrors:
    """Test specific error types"""

    def test_configuration_error(self):
        """Test ConfigurationError"""
        error = ConfigurationError(
            "Invalid configuration",
            details={'field': 'target.url'},
            suggestion="Set target.url in config"
        )

        assert isinstance(error, WebTestoolError)
        assert error.category == ErrorCategory.CONFIGURATION
        assert error.severity == ErrorSeverity.HIGH
        assert error.details['field'] == 'target.url'

    def test_network_error(self):
        """Test NetworkError"""
        error = NetworkError(
            "Connection failed",
            details={'url': 'https://example.com'}
        )

        assert isinstance(error, WebTestoolError)
        assert error.category == ErrorCategory.NETWORK
        assert error.severity == ErrorSeverity.HIGH
        assert "network connectivity" in error.suggestion.lower()

    def test_authentication_error(self):
        """Test AuthenticationError"""
        error = AuthenticationError(
            "Invalid credentials",
            details={'username': 'testuser'}
        )

        assert isinstance(error, WebTestoolError)
        assert error.category == ErrorCategory.AUTHENTICATION
        assert error.severity == ErrorSeverity.HIGH

    def test_validation_error(self):
        """Test ValidationError"""
        error = ValidationError(
            "Invalid URL format",
            details={'url': 'not-a-url'}
        )

        assert isinstance(error, WebTestoolError)
        assert error.category == ErrorCategory.VALIDATION
        assert error.severity == ErrorSeverity.MEDIUM

    def test_module_error(self):
        """Test ModuleError"""
        error = ModuleError(
            "Module failed",
            module_name="security"
        )

        assert isinstance(error, WebTestoolError)
        assert error.category == ErrorCategory.MODULE
        assert error.details['module'] == 'security'

    def test_scan_error(self):
        """Test ScanError"""
        error = ScanError(
            "Failed to fetch page",
            url="https://example.com/page"
        )

        assert isinstance(error, WebTestoolError)
        assert error.category == ErrorCategory.SCANNING
        assert error.details['url'] == 'https://example.com/page'


class TestHelperFunctions:
    """Test helper functions"""

    def test_wrap_exception(self):
        """Test exception wrapping"""
        original = ValueError("Original error")

        wrapped = wrap_exception(
            original,
            message="Wrapped error",
            error_class=ConfigurationError
        )

        assert isinstance(wrapped, ConfigurationError)
        assert wrapped.message == "Wrapped error"
        assert wrapped.original_error is original

    def test_is_network_error(self):
        """Test network error detection"""
        # Network error
        network_err = NetworkError("Connection failed")
        assert is_network_error(network_err) is True

        # Generic error with network keywords
        generic_err = Exception("Connection timeout")
        assert is_network_error(generic_err) is True

        # Non-network error
        other_err = ValidationError("Invalid format")
        assert is_network_error(other_err) is False

    def test_format_error_message(self):
        """Test error message formatting"""
        error = ConfigurationError(
            "Invalid config",
            details={'field': 'target.url', 'value': None},
            suggestion="Set target URL"
        )

        formatted = format_error_message(error)

        assert "ConfigurationError" in formatted
        assert "Invalid config" in formatted
        assert "field" in formatted
        assert "target.url" in formatted
        assert "💡 Suggestion" in formatted
        assert "Set target URL" in formatted


class TestErrorSeverity:
    """Test error severity handling"""

    def test_severity_levels(self):
        """Test different severity levels"""
        low = WebTestoolError("Low", severity=ErrorSeverity.LOW)
        medium = WebTestoolError("Medium", severity=ErrorSeverity.MEDIUM)
        high = WebTestoolError("High", severity=ErrorSeverity.HIGH)
        critical = WebTestoolError("Critical", severity=ErrorSeverity.CRITICAL)

        assert low.severity == ErrorSeverity.LOW
        assert medium.severity == ErrorSeverity.MEDIUM
        assert high.severity == ErrorSeverity.HIGH
        assert critical.severity == ErrorSeverity.CRITICAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
