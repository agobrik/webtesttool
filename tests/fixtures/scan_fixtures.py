"""
Test fixtures for scan results and findings
"""

import pytest
from datetime import datetime, timedelta
from core.models import (
    ScanResult, ModuleResult, TestResult, Finding,
    Severity, FindingCategory, Evidence, Recommendation
)


@pytest.fixture
def sample_finding():
    """Create a sample security finding"""
    return Finding(
        title="SQL Injection Vulnerability",
        description="Potential SQL injection found in login form",
        severity=Severity.HIGH,
        category=FindingCategory.SECURITY,
        url="https://example.com/login",
        method="POST",
        parameter="username",
        evidence=[
            Evidence(
                type="request",
                content="username=' OR '1'='1",
                description="Malicious payload"
            )
        ],
        recommendations=[
            Recommendation(
                title="Use Parameterized Queries",
                description="Always use parameterized queries or prepared statements",
                priority=1
            )
        ],
        cvss_score=7.5,
        cwe_id="CWE-89"
    )


@pytest.fixture
def sample_test_result():
    """Create a sample test result"""
    return TestResult(
        name="SQL Injection Test",
        passed=False,
        duration=2.5,
        findings=[],
        metadata={
            'payloads_tested': 50,
            'vulnerabilities_found': 1
        }
    )


@pytest.fixture
def sample_module_result():
    """Create a sample module result"""
    return ModuleResult(
        module_name="security",
        status="completed",
        duration=15.3,
        tests_run=14,
        tests_passed=13,
        tests_failed=1,
        findings=[],
        metadata={}
    )


@pytest.fixture
def sample_scan_result():
    """Create a complete sample scan result"""
    start_time = datetime.now()
    return ScanResult(
        target_url="https://example.com",
        start_time=start_time,
        end_time=start_time + timedelta(minutes=5),
        duration=timedelta(minutes=5),
        status="completed",
        modules_results=[],
        summary={
            'total_findings': 5,
            'critical_findings': 1,
            'high_findings': 2,
            'medium_findings': 1,
            'low_findings': 1,
            'pages_scanned': 25
        }
    )


@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response"""
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self.headers = {
                'Content-Type': 'text/html',
                'Server': 'nginx'
            }
            self.text = '<html><body><h1>Test Page</h1></body></html>'
            self.content = self.text.encode()
            self.url = 'https://example.com'

        async def json(self):
            return {'status': 'ok'}

    return MockResponse()
