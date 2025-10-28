"""
Performance Testing Module
Tests for load, stress, response time, and resource optimization
"""

import asyncio
import time
import httpx
from loguru import logger

from core.module_loader import BaseTestModule
from core.models import (
    Category, ModuleResult, TestResult, TestStatus,
    Finding, Severity, TestContext
)


class PerformanceModule(BaseTestModule):
    """Performance Testing Module"""

    name = "performance"
    description = "Performance testing including load, stress, and response time analysis"
    category = Category.PERFORMANCE
    version = "1.0.0"

    async def run(self, context: TestContext) -> ModuleResult:
        """Run performance tests"""

        module_result = ModuleResult(
            name=self.name,
            category=self.category,
            status=TestStatus.RUNNING
        )

        module_config = self.config.get_module_config(self.name)

        # Response Time Test
        if module_config.get('response_time', {}).get('enabled', True):
            test_result = await self._test_response_time(context, module_config)
            module_result.add_test_result(test_result)

        # Load Test (simplified)
        if module_config.get('load_test', {}).get('enabled', True):
            test_result = await self._test_load(context, module_config)
            module_result.add_test_result(test_result)

        # Resource Analysis
        if module_config.get('resource_analysis', {}).get('enabled', True):
            test_result = await self._test_resources(context, module_config)
            module_result.add_test_result(test_result)

        module_result.mark_completed(TestStatus.PASSED)
        return module_result

    async def _test_response_time(self, context: TestContext, config: dict) -> TestResult:
        """Test response times"""

        test_result = TestResult(
            name="response_time_test",
            description="Measures page response times",
            category=self.category,
            status=TestStatus.RUNNING
        )

        threshold_warning = config.get('response_time', {}).get('threshold_warning', 1000)
        threshold_critical = config.get('response_time', {}).get('threshold_critical', 3000)

        # Test main page and crawled pages
        test_urls = [context.target_url] + [p.url for p in context.crawled_pages[:10]]

        for url in test_urls:
            try:
                start = time.time()
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url)
                elapsed_ms = (time.time() - start) * 1000

                if elapsed_ms > threshold_critical:
                    test_result.add_finding(Finding(
                        title=f"Slow Response Time (Critical): {url}",
                        description=f"Page took {elapsed_ms:.0f}ms to load (threshold: {threshold_critical}ms)",
                        severity=Severity.HIGH,
                        category=self.category,
                        url=url,
                        metadata={'response_time_ms': elapsed_ms}
                    ))
                elif elapsed_ms > threshold_warning:
                    test_result.add_finding(Finding(
                        title=f"Slow Response Time (Warning): {url}",
                        description=f"Page took {elapsed_ms:.0f}ms to load (threshold: {threshold_warning}ms)",
                        severity=Severity.MEDIUM,
                        category=self.category,
                        url=url,
                        metadata={'response_time_ms': elapsed_ms}
                    ))

                logger.debug(f"Response time for {url}: {elapsed_ms:.0f}ms")

            except Exception as e:
                logger.error(f"Error testing response time for {url}: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_load(self, context: TestContext, config: dict) -> TestResult:
        """Simple load test"""

        test_result = TestResult(
            name="load_test",
            description="Simulates concurrent users",
            category=self.category,
            status=TestStatus.RUNNING
        )

        users = min(config.get('load_test', {}).get('users', 10), 50)  # Cap at 50 for safety

        logger.info(f"Running load test with {users} concurrent users")

        async def make_request():
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    start = time.time()
                    response = await client.get(context.target_url)
                    return time.time() - start, response.status_code
            except Exception as e:
                return None, None

        # Run concurrent requests
        tasks = [make_request() for _ in range(users)]
        results = await asyncio.gather(*tasks)

        # Analyze results
        successful = sum(1 for r in results if r[1] and r[1] < 400)
        failed = sum(1 for r in results if r[1] is None or r[1] >= 400)
        avg_time = sum(r[0] for r in results if r[0]) / len([r for r in results if r[0]]) if any(r[0] for r in results) else 0

        if failed > users * 0.1:  # More than 10% failed
            test_result.add_finding(Finding(
                title="High Failure Rate Under Load",
                description=f"{failed}/{users} requests failed ({failed/users*100:.1f}%)",
                severity=Severity.HIGH,
                category=self.category,
                url=context.target_url
            ))

        if avg_time > 5:  # Average > 5 seconds
            test_result.add_finding(Finding(
                title="Poor Performance Under Load",
                description=f"Average response time: {avg_time:.2f}s with {users} users",
                severity=Severity.MEDIUM,
                category=self.category,
                url=context.target_url
            ))

        logger.info(f"Load test complete: {successful} successful, {failed} failed, avg: {avg_time:.2f}s")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_resources(self, context: TestContext, config: dict) -> TestResult:
        """Test resource optimization"""

        test_result = TestResult(
            name="resource_optimization",
            description="Checks resource compression and caching",
            category=self.category,
            status=TestStatus.RUNNING
        )

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(context.target_url)

                # Check compression
                if 'gzip' not in response.headers.get('Content-Encoding', '').lower() and \
                   'br' not in response.headers.get('Content-Encoding', '').lower():
                    test_result.add_finding(Finding(
                        title="No Compression Enabled",
                        description="Server does not use gzip or brotli compression",
                        severity=Severity.LOW,
                        category=self.category,
                        url=context.target_url
                    ))

                # Check caching
                cache_control = response.headers.get('Cache-Control', '')
                if not cache_control:
                    test_result.add_finding(Finding(
                        title="No Cache-Control Header",
                        description="Resources may not be cached effectively",
                        severity=Severity.LOW,
                        category=self.category,
                        url=context.target_url
                    ))

                # Check content size
                content_length = len(response.content)
                if content_length > 5 * 1024 * 1024:  # 5MB
                    test_result.add_finding(Finding(
                        title="Large Page Size",
                        description=f"Page is {content_length / 1024 / 1024:.2f}MB",
                        severity=Severity.MEDIUM,
                        category=self.category,
                        url=context.target_url
                    ))

        except Exception as e:
            logger.error(f"Error testing resources: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result
