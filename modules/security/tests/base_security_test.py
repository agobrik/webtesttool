"""
Base class for security tests
"""

from abc import abstractmethod
from typing import Any, Dict
import httpx
from loguru import logger

from core.models import (
    TestResult, TestStatus, Category, Finding,
    Severity, Evidence, Recommendation, TestContext
)


class BaseSecurityTest:
    """
    Base class for all security tests
    """

    name: str = "base_security_test"
    description: str = "Base security test"
    config_key: str = None  # Key in module config (e.g., 'sql_injection')

    def __init__(self, config, module_config: Dict[str, Any]):
        """
        Initialize security test

        Args:
            config: Global configuration
            module_config: Security module specific configuration
        """
        self.config = config
        self.module_config = module_config
        self.test_result = TestResult(
            name=self.name,
            description=self.description,
            category=Category.SECURITY,
            status=TestStatus.PENDING
        )
        self.timeout = 30
        self.max_retries = 3

    def is_enabled(self) -> bool:
        """
        Check if this test is enabled in configuration

        Returns:
            True if enabled, False otherwise
        """
        if self.config_key:
            test_config = self.module_config.get(self.config_key, {})
            return test_config.get('enabled', True)
        return True

    async def execute(self, context: TestContext) -> TestResult:
        """
        Execute the security test

        Args:
            context: Test context

        Returns:
            TestResult object
        """
        logger.debug(f"Executing {self.name}")
        self.test_result.status = TestStatus.RUNNING

        try:
            await self.run_test(context)

            # Mark as passed if no errors occurred
            if self.test_result.status == TestStatus.RUNNING:
                self.test_result.mark_completed(TestStatus.PASSED)

        except Exception as e:
            logger.error(f"Error in {self.name}: {str(e)}")
            self.test_result.status = TestStatus.ERROR
            self.test_result.error_message = str(e)
            self.test_result.mark_completed(TestStatus.ERROR)

        return self.test_result

    @abstractmethod
    async def run_test(self, context: TestContext) -> None:
        """
        Run the actual test logic
        Must be implemented by subclasses

        Args:
            context: Test context
        """
        pass

    async def make_request(
        self,
        url: str,
        method: str = "GET",
        data: Dict = None,
        headers: Dict = None,
        cookies: Dict = None,
        allow_redirects: bool = True
    ) -> httpx.Response:
        """
        Make HTTP request with proper error handling

        Args:
            url: Target URL
            method: HTTP method
            data: Request data
            headers: Request headers
            cookies: Request cookies
            allow_redirects: Whether to follow redirects

        Returns:
            HTTP response
        """
        if headers is None:
            headers = self.config.config.target.headers.copy()

        if cookies is None:
            cookies = self.config.config.target.cookies.copy()

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=allow_redirects,
            verify=False  # For testing purposes
        ) as client:
            response = await client.request(
                method=method,
                url=url,
                data=data,
                headers=headers,
                cookies=cookies
            )
            return response

    def add_finding(
        self,
        title: str,
        description: str,
        severity: Severity,
        url: str = None,
        evidence: list = None,
        recommendations: list = None,
        cwe_id: str = None,
        owasp_category: str = None,
        **kwargs
    ) -> None:
        """
        Add a security finding

        Args:
            title: Finding title
            description: Finding description
            severity: Severity level
            url: Affected URL
            evidence: List of Evidence objects
            recommendations: List of Recommendation objects
            cwe_id: CWE identifier
            owasp_category: OWASP category
            **kwargs: Additional metadata
        """
        finding = Finding(
            title=title,
            description=description,
            severity=severity,
            category=Category.SECURITY,
            url=url,
            evidence=evidence or [],
            recommendations=recommendations or [],
            cwe_id=cwe_id,
            owasp_category=owasp_category,
            metadata=kwargs
        )

        self.test_result.add_finding(finding)

        # Log the finding
        severity_emoji = {
            Severity.CRITICAL: "🔴",
            Severity.HIGH: "🟠",
            Severity.MEDIUM: "🟡",
            Severity.LOW: "🟢",
            Severity.INFO: "ℹ️"
        }
        logger.warning(f"{severity_emoji.get(severity, '')} Found: {title} ({severity.value})")

    def create_evidence(self, evidence_type: str, data: Any, description: str = None) -> Evidence:
        """
        Create evidence object

        Args:
            evidence_type: Type of evidence (request, response, screenshot, etc.)
            data: Evidence data
            description: Evidence description

        Returns:
            Evidence object
        """
        return Evidence(
            type=evidence_type,
            data=data,
            description=description
        )

    def create_recommendation(
        self,
        title: str,
        description: str,
        references: list = None,
        code_example: str = None
    ) -> Recommendation:
        """
        Create recommendation object

        Args:
            title: Recommendation title
            description: Recommendation description
            references: List of reference URLs
            code_example: Code example

        Returns:
            Recommendation object
        """
        return Recommendation(
            title=title,
            description=description,
            references=references or [],
            code_example=code_example
        )

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value for this test

        Args:
            key: Configuration key
            default: Default value

        Returns:
            Configuration value
        """
        if self.config_key:
            test_config = self.module_config.get(self.config_key, {})
            return test_config.get(key, default)
        return default
