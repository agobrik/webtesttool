"""
Main Security Testing Module
"""

from loguru import logger

from core.module_loader import BaseTestModule
from core.models import (
    Category, ModuleResult, TestResult, TestStatus, TestContext
)

from .tests.sql_injection import SQLInjectionTest
from .tests.xss import XSSTest
from .tests.csrf import CSRFTest
from .tests.xxe import XXETest
from .tests.ssrf import SSRFTest
from .tests.command_injection import CommandInjectionTest
from .tests.path_traversal import PathTraversalTest
from .tests.security_headers import SecurityHeadersTest
from .tests.ssl_tls import SSLTLSTest
from .tests.cors import CORSTest
from .tests.cookies_security import CookiesSecurityTest
from .tests.info_disclosure import InfoDisclosureTest
from .tests.clickjacking import ClickjackingTest
from .tests.open_redirect import OpenRedirectTest


class SecurityModule(BaseTestModule):
    """
    Security Testing Module
    Performs comprehensive security testing
    """

    name = "security"
    description = "Comprehensive security testing including OWASP Top 10"
    category = Category.SECURITY
    version = "1.0.0"

    def __init__(self, config):
        super().__init__(config)

        # Initialize test classes
        self.test_classes = [
            SQLInjectionTest,
            XSSTest,
            CSRFTest,
            XXETest,
            SSRFTest,
            CommandInjectionTest,
            PathTraversalTest,
            SecurityHeadersTest,
            SSLTLSTest,
            CORSTest,
            CookiesSecurityTest,
            InfoDisclosureTest,
            ClickjackingTest,
            OpenRedirectTest,
        ]

    async def run(self, context: TestContext) -> ModuleResult:
        """
        Run all security tests

        Args:
            context: Test context

        Returns:
            ModuleResult with all security test results
        """
        logger.info(f"Starting {self.name} module")

        module_result = ModuleResult(
            name=self.name,
            category=self.category,
            status=TestStatus.RUNNING
        )

        # Get module configuration
        module_config = self.config.get_module_config(self.name)

        # Run each test
        for test_class in self.test_classes:
            test_instance = test_class(self.config, module_config)

            # Check if this specific test is enabled
            if test_instance.is_enabled():
                try:
                    logger.debug(f"Running security test: {test_instance.name}")
                    test_result = await test_instance.execute(context)
                    module_result.add_test_result(test_result)
                except Exception as e:
                    logger.error(f"Error running {test_instance.name}: {str(e)}")
                    # Create error test result
                    error_result = TestResult(
                        name=test_instance.name,
                        description=test_instance.description,
                        category=self.category,
                        status=TestStatus.ERROR,
                        error_message=str(e)
                    )
                    error_result.mark_completed(TestStatus.ERROR)
                    module_result.add_test_result(error_result)

        module_result.mark_completed(TestStatus.PASSED)
        return module_result
