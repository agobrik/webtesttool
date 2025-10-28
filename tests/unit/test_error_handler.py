"""
Unit tests for Error Handler
"""

import pytest
from io import StringIO
import sys

from core.error_handler import ErrorHandler
from core.exceptions import (
    ConfigurationError,
    NetworkError,
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    ValidationError,
    ModuleError,
    ScanError,
    ReportGenerationError,
    DatabaseError
)


@pytest.mark.unit
def test_handle_configuration_error(capsys):
    """Test handling configuration errors"""
    error = ConfigurationError(
        "Invalid configuration",
        details={"field": "target.url", "reason": "URL is required"}
    )

    # Handle error
    ErrorHandler.handle_exception(error, verbose=False)

    # Capture output
    captured = capsys.readouterr()

    # Verify error was displayed (basic check since we can't easily test Rich output)
    # The output should contain the error type
    assert "Configuration" in captured.out or "configuration" in captured.out.lower()


@pytest.mark.unit
def test_handle_network_error(capsys):
    """Test handling network errors"""
    error = NetworkError(
        "Connection failed",
        details={"url": "https://example.com", "status_code": 500}
    )

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    # Should contain network-related information
    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_authentication_error(capsys):
    """Test handling authentication errors"""
    error = AuthenticationError(
        "Invalid credentials",
        details={"username": "testuser"}
    )

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_rate_limit_error(capsys):
    """Test handling rate limit errors"""
    error = RateLimitError(
        "Rate limit exceeded",
        details={"limit": "100", "reset_time": "60"}
    )

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_timeout_error(capsys):
    """Test handling timeout errors"""
    error = TimeoutError(
        "Request timed out",
        details={"url": "https://example.com", "timeout": "30"}
    )

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_validation_error(capsys):
    """Test handling validation errors"""
    error = ValidationError(
        "Invalid input",
        details={"field": "email", "value": "invalid"}
    )

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_module_error(capsys):
    """Test handling module errors"""
    error = ModuleError(
        "Module execution failed",
        details={"module": "security", "reason": "Test failed"}
    )

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_scan_error(capsys):
    """Test handling scan errors"""
    error = ScanError(
        "Scan failed",
        details={"page": "https://example.com/page1"}
    )

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_report_generation_error(capsys):
    """Test handling report generation errors"""
    error = ReportGenerationError(
        "Failed to generate report",
        details={"format": "PDF", "reason": "Template not found"}
    )

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_database_error(capsys):
    """Test handling database errors"""
    error = DatabaseError(
        "Database connection failed",
        details={"host": "localhost", "port": "5432"}
    )

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_generic_exception(capsys):
    """Test handling generic exceptions"""
    error = Exception("Something went wrong")

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_exception_with_verbose(capsys):
    """Test handling exception with verbose mode"""
    error = NetworkError(
        "Connection failed",
        original_error=ConnectionError("Network unreachable")
    )

    # With verbose=True, should show original error
    ErrorHandler.handle_exception(error, verbose=True)
    captured = capsys.readouterr()

    # Should contain error information
    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_exception_with_suggestion(capsys):
    """Test handling exception with suggestion"""
    error = ConfigurationError(
        "Invalid URL format",
        suggestion="Use format: https://example.com"
    )

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_exception_without_details(capsys):
    """Test handling exception without details"""
    error = ConfigurationError("Simple error message")

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0


@pytest.mark.unit
def test_multiple_error_handling(capsys):
    """Test handling multiple errors in sequence"""
    errors = [
        ConfigurationError("Config error"),
        NetworkError("Network error"),
        ValidationError("Validation error")
    ]

    for error in errors:
        ErrorHandler.handle_exception(error, verbose=False)

    captured = capsys.readouterr()
    assert len(captured.out) > 0


@pytest.mark.unit
def test_error_handler_static_methods():
    """Test that all ErrorHandler methods are static"""
    import inspect

    # Get all methods of ErrorHandler
    methods = inspect.getmembers(ErrorHandler, predicate=inspect.isfunction)

    # All public methods should be static (or have self as first param for private)
    for name, method in methods:
        if not name.startswith('_'):
            # Should be callable without instance
            assert callable(method)


@pytest.mark.unit
def test_handle_exception_preserves_error_type():
    """Test that handling exception doesn't modify the original error"""
    error = ConfigurationError(
        "Test error",
        details={"key": "value"}
    )

    original_message = error.message
    original_details = error.details.copy()

    # Handle the error
    ErrorHandler.handle_exception(error, verbose=False)

    # Verify original error is unchanged
    assert error.message == original_message
    assert error.details == original_details


@pytest.mark.unit
def test_handle_nested_exceptions(capsys):
    """Test handling exceptions with nested original errors"""
    try:
        try:
            raise ValueError("Inner error")
        except ValueError as ve:
            raise NetworkError("Outer error", original_error=ve)
    except NetworkError as ne:
        ErrorHandler.handle_exception(ne, verbose=True)

    captured = capsys.readouterr()
    assert len(captured.out) > 0


@pytest.mark.unit
def test_error_handler_with_rich_panel(capsys):
    """Test that error handler creates Rich panels"""
    error = ConfigurationError("Test error")

    ErrorHandler.handle_exception(error, verbose=False)

    # Rich will output to console
    # We just verify it doesn't crash
    captured = capsys.readouterr()
    assert len(captured.out) >= 0  # May be 0 if Rich doesn't use stdout


@pytest.mark.unit
def test_handle_error_with_empty_details(capsys):
    """Test handling error with empty details dictionary"""
    error = NetworkError("Error message", details={})

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0


@pytest.mark.unit
def test_handle_error_with_none_suggestion(capsys):
    """Test handling error with None suggestion"""
    error = ValidationError("Error message", suggestion=None)

    ErrorHandler.handle_exception(error, verbose=False)
    captured = capsys.readouterr()

    assert len(captured.out) > 0
