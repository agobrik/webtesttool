"""
WebTestool Core Framework
Main package initialization
"""

__version__ = "1.5.0"
__author__ = "WebTestool Framework"
__license__ = "MIT"

from .engine import TestEngine
from .config import ConfigManager
from .scanner import WebScanner
from .module_loader import ModuleLoader
from .progress import ProgressTracker, create_progress_tracker
from .exceptions import (
    WebTestoolError,
    ConfigurationError,
    NetworkError,
    AuthenticationError,
    ValidationError,
    ModuleError,
    ScanError,
    ReportGenerationError,
    DatabaseError,
    SystemError,
    DependencyError,
    RateLimitError,
    TimeoutError,
)

__all__ = [
    "TestEngine",
    "ConfigManager",
    "WebScanner",
    "ModuleLoader",
    "ProgressTracker",
    "create_progress_tracker",
    "WebTestoolError",
    "ConfigurationError",
    "NetworkError",
    "AuthenticationError",
    "ValidationError",
    "ModuleError",
    "ScanError",
    "ReportGenerationError",
    "DatabaseError",
    "SystemError",
    "DependencyError",
    "RateLimitError",
    "TimeoutError",
]
