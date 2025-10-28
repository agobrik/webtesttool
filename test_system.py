"""
System Test and Validation Script
Tests all components of WebTestool
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from colorama import init, Fore, Style

init(autoreset=True)


class SystemTester:
    """System testing and validation"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def test(self, name: str):
        """Decorator for test functions"""
        def decorator(func):
            self.tests.append((name, func))
            return func
        return decorator

    async def run_all_tests(self):
        """Run all registered tests"""
        print(Fore.CYAN + Style.BRIGHT + "\n" + "="*80)
        print(Fore.CYAN + Style.BRIGHT + "WebTestool System Validation")
        print(Fore.CYAN + Style.BRIGHT + "="*80 + "\n")

        for name, test_func in self.tests:
            try:
                print(f"Running: {name}...", end=" ")
                if asyncio.iscoroutinefunction(test_func):
                    await test_func()
                else:
                    test_func()
                print(Fore.GREEN + "✓ PASSED")
                self.passed += 1
            except Exception as e:
                print(Fore.RED + f"✗ FAILED: {str(e)}")
                self.failed += 1

        print("\n" + "="*80)
        print(f"Results: {Fore.GREEN}{self.passed} passed{Style.RESET_ALL}, "
              f"{Fore.RED if self.failed > 0 else Fore.GREEN}{self.failed} failed{Style.RESET_ALL}")
        print("="*80 + "\n")

        return self.failed == 0


# Create tester instance
tester = SystemTester()


@tester.test("Import core modules")
def test_import_core():
    """Test core module imports"""
    from core import ConfigManager, TestEngine, WebScanner, ModuleLoader
    from core.models import ScanResult, Finding, TestResult, ModuleResult
    assert ConfigManager
    assert TestEngine
    assert WebScanner
    assert ModuleLoader


@tester.test("Import security module")
def test_import_security():
    """Test security module import"""
    from modules.security import SecurityModule
    from modules.security.tests.sql_injection import SQLInjectionTest
    from modules.security.tests.xss import XSSTest
    assert SecurityModule
    assert SQLInjectionTest
    assert XSSTest


@tester.test("Import performance module")
def test_import_performance():
    """Test performance module import"""
    from modules.performance import PerformanceModule
    assert PerformanceModule


@tester.test("Import SEO module")
def test_import_seo():
    """Test SEO module import"""
    from modules.seo import SEOModule
    assert SEOModule


@tester.test("Import accessibility module")
def test_import_accessibility():
    """Test accessibility module import"""
    from modules.accessibility import AccessibilityModule
    assert AccessibilityModule


@tester.test("Import API module")
def test_import_api():
    """Test API module import"""
    from modules.api import APIModule
    assert APIModule


@tester.test("Import infrastructure module")
def test_import_infrastructure():
    """Test infrastructure module import"""
    from modules.infrastructure import InfrastructureModule
    assert InfrastructureModule


@tester.test("Import functional module")
def test_import_functional():
    """Test functional module import"""
    from modules.functional import FunctionalModule
    assert FunctionalModule


@tester.test("Import visual module")
def test_import_visual():
    """Test visual module import"""
    from modules.visual import VisualModule
    assert VisualModule


@tester.test("Import reporters")
def test_import_reporters():
    """Test reporter imports"""
    from reporters import ReportGenerator, HTMLReporter, JSONReporter
    assert ReportGenerator
    assert HTMLReporter
    assert JSONReporter


@tester.test("Import database layer")
def test_import_database():
    """Test database layer import"""
    from database import DatabaseManager
    assert DatabaseManager


@tester.test("Import utilities")
def test_import_utils():
    """Test utility imports"""
    from utils import HTTPUtils, PayloadLoader, URLValidator
    assert HTTPUtils
    assert PayloadLoader
    assert URLValidator


@tester.test("Import AuthManager")
def test_import_auth_manager():
    """Test AuthManager import"""
    from core.auth_manager import AuthManager
    assert AuthManager


@tester.test("Import Notifier")
def test_import_notifier():
    """Test Notifier import"""
    from core.notifier import Notifier
    assert Notifier


@tester.test("Import GraphQL tester")
def test_import_graphql_tester():
    """Test GraphQL tester import"""
    from modules.api.graphql_tester import GraphQLTester
    assert GraphQLTester


@tester.test("Import WebSocket tester")
def test_import_websocket_tester():
    """Test WebSocket tester import"""
    from modules.api.websocket_tester import WebSocketTester
    assert WebSocketTester


@tester.test("Import CI/CD integrations")
def test_import_integrations():
    """Test CI/CD integration helpers import"""
    from integrations.github_actions import GitHubActionsHelper
    from integrations.gitlab_ci import GitLabCIHelper
    from integrations.jenkins import JenkinsHelper
    assert GitHubActionsHelper
    assert GitLabCIHelper
    assert JenkinsHelper


@tester.test("Load default configuration")
def test_load_config():
    """Test configuration loading"""
    from core import ConfigManager

    config = ConfigManager()
    assert config.config is not None
    assert hasattr(config.config, 'target')
    assert hasattr(config.config, 'crawler')
    assert hasattr(config.config, 'modules')


@tester.test("Configuration validation")
def test_config_validation():
    """Test configuration validation"""
    from core import ConfigManager

    config = ConfigManager()
    config.set('target.url', 'https://example.com')

    is_valid, errors = config.validate()
    assert is_valid, f"Configuration validation failed: {errors}"


@tester.test("URL validation")
def test_url_validation():
    """Test URL validation"""
    from utils import URLValidator

    assert URLValidator.is_valid_url('https://example.com')
    assert URLValidator.is_valid_url('http://example.com')
    assert not URLValidator.is_valid_url('not a url')
    assert not URLValidator.is_valid_url('ftp://example.com')


@tester.test("Payload loader")
def test_payload_loader():
    """Test payload loading"""
    from utils import PayloadLoader

    loader = PayloadLoader()
    sqli_payloads = loader.load_sqli_payloads()
    xss_payloads = loader.load_xss_payloads()

    assert len(sqli_payloads) > 0, "No SQL injection payloads loaded"
    assert len(xss_payloads) > 0, "No XSS payloads loaded"


@tester.test("Module loader discovery")
async def test_module_loader():
    """Test module loader"""
    from core import ConfigManager, ModuleLoader

    config = ConfigManager()
    config.set('target.url', 'https://example.com')

    loader = ModuleLoader(config)
    loader.discover_modules()

    modules = loader.list_modules()
    assert len(modules) > 0, "No modules discovered"
    assert 'security' in modules, "Security module not found"


@tester.test("Database operations")
def test_database():
    """Test database operations"""
    from database import DatabaseManager
    import os

    # Use test database
    test_db_path = 'data/test_db.db'
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    db = DatabaseManager(f'sqlite:///{test_db_path}')

    # Test statistics
    stats = db.get_statistics()
    assert stats['total_scans'] == 0
    assert stats['total_findings'] == 0

    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@tester.test("Data models")
def test_data_models():
    """Test data models"""
    from core.models import (
        ScanResult, Finding, TestResult, ModuleResult,
        Severity, TestStatus, Category
    )

    # Create test finding
    finding = Finding(
        title="Test Finding",
        description="Test description",
        severity=Severity.HIGH,
        category=Category.SECURITY,
        url="https://example.com"
    )

    assert finding.title == "Test Finding"
    assert finding.severity == Severity.HIGH

    # Create test result
    test_result = TestResult(
        name="test",
        description="Test",
        category=Category.SECURITY,
        status=TestStatus.PENDING
    )

    test_result.add_finding(finding)
    assert len(test_result.findings) == 1


@tester.test("HTTP utilities")
async def test_http_utils():
    """Test HTTP utilities"""
    from utils import HTTPUtils

    assert HTTPUtils.is_valid_url('https://example.com')
    assert HTTPUtils.extract_domain('https://example.com/path') == 'example.com'
    assert HTTPUtils.is_same_domain('https://example.com/a', 'https://example.com/b')


@tester.test("Report generation (mock)")
def test_report_generation():
    """Test report generation with mock data"""
    from reporters import ReportGenerator
    from core import ConfigManager
    from core.models import ScanResult, Finding, Severity, Category
    import os
    import tempfile

    config = ConfigManager()

    # Use temp directory for test reports
    with tempfile.TemporaryDirectory() as tmpdir:
        config.set('reporting.output_dir', tmpdir)

        # Create mock scan result
        scan_result = ScanResult(
            target_url="https://example.com"
        )

        finding = Finding(
            title="Test Finding",
            description="Test",
            severity=Severity.HIGH,
            category=Category.SECURITY
        )

        scan_result.module_results = []
        scan_result.mark_completed("passed")

        # Generate reports
        generator = ReportGenerator(config)
        reports = generator.generate_reports(scan_result)

        assert len(reports) > 0, "No reports generated"


@tester.test("AuthManager initialization")
def test_auth_manager():
    """Test AuthManager initialization with different auth types"""
    from core.auth_manager import AuthManager

    # Test basic auth
    auth_basic = AuthManager(
        auth_type='basic',
        username='test',
        password='test'
    )
    assert auth_basic.auth_type == 'basic'

    # Test bearer auth
    auth_bearer = AuthManager(
        auth_type='bearer',
        token='test-token'
    )
    assert auth_bearer.auth_type == 'bearer'


@tester.test("Notifier initialization")
def test_notifier_init():
    """Test Notifier initialization"""
    from core.notifier import Notifier
    from core import ConfigManager

    config = ConfigManager()
    config.set('notifications.enabled', False)

    notifier = Notifier(config)
    assert notifier is not None


@tester.test("CI/CD workflow generation")
def test_workflow_generation():
    """Test CI/CD workflow generation"""
    from integrations.github_actions import GitHubActionsHelper
    from integrations.gitlab_ci import GitLabCIHelper
    from integrations.jenkins import JenkinsHelper

    # Test GitHub Actions
    gh_workflow = GitHubActionsHelper.generate_workflow(
        target_url='https://example.com',
        profile='security'
    )
    assert 'name:' in gh_workflow
    assert 'jobs:' in gh_workflow

    # Test GitLab CI
    gl_pipeline = GitLabCIHelper.generate_pipeline(
        target_url='https://example.com',
        profile='security'
    )
    assert 'stages:' in gl_pipeline

    # Test Jenkins
    jenkins_file = JenkinsHelper.generate_jenkinsfile(
        target_url='https://example.com',
        profile='security'
    )
    assert 'pipeline' in jenkins_file
    assert 'stages' in jenkins_file


@tester.test("File structure")
def test_file_structure():
    """Test that all required files exist"""
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'USAGE_GUIDE.md',
        'ADVANCED_FEATURES.md',
        'RELEASE_NOTES.md',
        'setup.py',
        'core/__init__.py',
        'core/auth_manager.py',
        'core/notifier.py',
        'modules/security/__init__.py',
        'modules/functional/__init__.py',
        'modules/visual/__init__.py',
        'reporters/__init__.py',
        'integrations/github_actions.py',
        'integrations/gitlab_ci.py',
        'integrations/jenkins.py',
        'config/default_config.yaml'
    ]

    for file in required_files:
        filepath = Path(file)
        assert filepath.exists(), f"Required file not found: {file}"


async def main():
    """Run all tests"""
    success = await tester.run_all_tests()

    if success:
        print(Fore.GREEN + Style.BRIGHT + "All tests passed! ✓")
        print(Fore.GREEN + "System is ready to use.")
        return 0
    else:
        print(Fore.RED + Style.BRIGHT + "Some tests failed! ✗")
        print(Fore.RED + "Please fix the issues before using the system.")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
