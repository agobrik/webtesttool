"""
API Testing Module
Tests REST APIs, GraphQL, and other API endpoints
"""

import httpx
import json
from loguru import logger

from core.module_loader import BaseTestModule
from core.models import (
    Category, ModuleResult, TestResult, TestStatus,
    Finding, Severity, TestContext
)

from .graphql_tester import GraphQLTester
from .websocket_tester import WebSocketTester


class APIModule(BaseTestModule):
    """API Testing Module"""

    name = "api"
    description = "API testing for REST, GraphQL, and other endpoints"
    category = Category.API
    version = "1.0.0"

    async def run(self, context: TestContext) -> ModuleResult:
        """Run API tests"""

        module_result = ModuleResult(
            name=self.name,
            category=self.category,
            status=TestStatus.RUNNING
        )

        module_config = self.config.get_module_config(self.name)

        # REST API Tests
        if module_config.get('rest', {}).get('enabled', True):
            test_result = await self._test_rest_apis(context, module_config)
            module_result.add_test_result(test_result)

        # Schema Validation
        if module_config.get('schema_validation', {}).get('enabled', True):
            test_result = await self._test_schema_validation(context, module_config)
            module_result.add_test_result(test_result)

        # Response Validation
        if module_config.get('response_validation', {}).get('enabled', True):
            test_result = await self._test_response_validation(context, module_config)
            module_result.add_test_result(test_result)

        # GraphQL Testing
        if module_config.get('graphql', {}).get('enabled', True):
            test_result = await self._test_graphql(context, module_config)
            module_result.add_test_result(test_result)

        # WebSocket Testing
        if module_config.get('websocket', {}).get('enabled', True):
            test_result = await self._test_websocket(context, module_config)
            module_result.add_test_result(test_result)

        module_result.mark_completed(TestStatus.PASSED)
        return module_result

    async def _test_rest_apis(self, context: TestContext, config: dict) -> TestResult:
        """Test REST API endpoints"""

        test_result = TestResult(
            name="rest_api_test",
            description="Tests REST API endpoints",
            category=self.category,
            status=TestStatus.RUNNING
        )

        methods = config.get('rest', {}).get('test_methods', ['GET', 'POST', 'PUT', 'DELETE'])

        for endpoint in context.api_endpoints[:20]:  # Limit to 20 endpoints
            try:
                # Test each HTTP method
                for method in methods:
                    if endpoint.method == 'UNKNOWN' or endpoint.method == method:
                        await self._test_endpoint(endpoint.url, method, test_result)

            except Exception as e:
                logger.debug(f"Error testing API endpoint {endpoint.url}: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_endpoint(self, url: str, method: str, test_result: TestResult) -> None:
        """Test individual API endpoint"""

        try:
            async with httpx.AsyncClient(timeout=30, verify=False) as client:
                response = await client.request(method=method, url=url)

                # Check for common API security issues

                # 1. Check for verbose error messages
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                        if any(key in str(error_data).lower() for key in ['stack', 'trace', 'exception', 'debug']):
                            test_result.add_finding(Finding(
                                title="Verbose API Error Messages",
                                description=f"API endpoint {url} returns verbose error information",
                                severity=Severity.LOW,
                                category=self.category,
                                url=url,
                                metadata={'method': method, 'status': response.status_code}
                            ))
                    except Exception as e:
                        logger.debug(f"Error checking rate limiting: {e}")

                # 2. Check for missing security headers
                if 'X-Content-Type-Options' not in response.headers:
                    test_result.add_finding(Finding(
                        title="Missing X-Content-Type-Options Header in API",
                        description="API endpoint missing security header",
                        severity=Severity.LOW,
                        category=self.category,
                        url=url
                    ))

                # 3. Check for CORS misconfig (already tested but double-check APIs)
                if response.headers.get('Access-Control-Allow-Origin') == '*':
                    if response.headers.get('Access-Control-Allow-Credentials', '').lower() == 'true':
                        test_result.add_finding(Finding(
                            title="Dangerous CORS Configuration in API",
                            description="API allows credentials with wildcard origin",
                            severity=Severity.HIGH,
                            category=self.category,
                            url=url
                        ))

                # 4. Check response time
                if hasattr(response, 'elapsed'):
                    elapsed_ms = response.elapsed.total_seconds() * 1000
                    if elapsed_ms > 3000:
                        test_result.add_finding(Finding(
                            title="Slow API Response",
                            description=f"API endpoint took {elapsed_ms:.0f}ms to respond",
                            severity=Severity.LOW,
                            category=self.category,
                            url=url,
                            metadata={'response_time_ms': elapsed_ms}
                        ))

        except httpx.RequestError as e:
            logger.debug(f"Request error testing {url}: {str(e)}")
        except Exception as e:
            logger.debug(f"Error testing {url}: {str(e)}")

    async def _test_schema_validation(self, context: TestContext, config: dict) -> TestResult:
        """Test API schema validation"""

        test_result = TestResult(
            name="schema_validation_test",
            description="Tests API schema validation",
            category=self.category,
            status=TestStatus.RUNNING
        )

        for endpoint in context.api_endpoints[:10]:
            try:
                # Try to send invalid data types
                async with httpx.AsyncClient(timeout=30, verify=False) as client:
                    # Test with invalid JSON
                    if endpoint.method in ['POST', 'PUT', 'PATCH']:
                        invalid_payloads = [
                            '{"invalid": }',  # Invalid JSON
                            '{"number": "not_a_number"}',  # Type mismatch
                            '',  # Empty
                        ]

                        for payload in invalid_payloads:
                            try:
                                response = await client.request(
                                    method=endpoint.method,
                                    url=endpoint.url,
                                    content=payload,
                                    headers={'Content-Type': 'application/json'}
                                )

                                # API should reject invalid input
                                if response.status_code < 400:
                                    test_result.add_finding(Finding(
                                        title="Weak API Input Validation",
                                        description=f"API accepts invalid data: {payload[:50]}",
                                        severity=Severity.MEDIUM,
                                        category=self.category,
                                        url=endpoint.url
                                    ))

                            except Exception:
                                pass  # Expected for invalid JSON

            except Exception as e:
                logger.debug(f"Error in schema validation: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_response_validation(self, context: TestContext, config: dict) -> TestResult:
        """Test API response validation"""

        test_result = TestResult(
            name="response_validation_test",
            description="Validates API responses",
            category=self.category,
            status=TestStatus.RUNNING
        )

        for endpoint in context.api_endpoints[:10]:
            try:
                async with httpx.AsyncClient(timeout=30, verify=False) as client:
                    response = await client.get(endpoint.url)

                    # Check Content-Type header
                    content_type = response.headers.get('Content-Type', '')

                    if 'json' in content_type.lower():
                        try:
                            data = response.json()

                            # Check for sensitive data in response
                            sensitive_keys = ['password', 'secret', 'token', 'api_key', 'private_key']
                            if isinstance(data, dict):
                                for key in data.keys():
                                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                                        test_result.add_finding(Finding(
                                            title="Potential Sensitive Data Exposure in API",
                                            description=f"API response contains field: {key}",
                                            severity=Severity.MEDIUM,
                                            category=self.category,
                                            url=endpoint.url
                                        ))

                        except json.JSONDecodeError:
                            test_result.add_finding(Finding(
                                title="Invalid JSON Response from API",
                                description="API claims JSON but returns invalid JSON",
                                severity=Severity.LOW,
                                category=self.category,
                                url=endpoint.url
                            ))

                    # Check status code consistency
                    if not config.get('response_validation', {}).get('check_status_codes', True):
                        continue

                    if response.status_code not in [200, 201, 204, 400, 401, 403, 404, 500]:
                        test_result.add_finding(Finding(
                            title="Non-Standard HTTP Status Code",
                            description=f"API returned unusual status code: {response.status_code}",
                            severity=Severity.INFO,
                            category=self.category,
                            url=endpoint.url
                        ))

            except Exception as e:
                logger.debug(f"Error validating response: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_graphql(self, context: TestContext, config: dict) -> TestResult:
        """Test GraphQL endpoints"""

        test_result = TestResult(
            name="graphql_test",
            description="Tests GraphQL API endpoints",
            category=self.category,
            status=TestStatus.RUNNING
        )

        # Only test if there are GraphQL endpoints
        graphql_endpoints = [ep for ep in context.api_endpoints if 'graphql' in ep.url.lower()]

        if graphql_endpoints:
            tester = GraphQLTester(self.config)
            for endpoint in graphql_endpoints[:5]:  # Limit to 5
                try:
                    await tester.test_graphql_endpoint(endpoint.url, test_result)
                except Exception as e:
                    logger.debug(f"Error testing GraphQL endpoint: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_websocket(self, context: TestContext, config: dict) -> TestResult:
        """Test WebSocket endpoints"""

        test_result = TestResult(
            name="websocket_test",
            description="Tests WebSocket connections",
            category=self.category,
            status=TestStatus.RUNNING
        )

        # Only test if there are WebSocket endpoints
        ws_endpoints = [ep for ep in context.api_endpoints if 'ws' in ep.url.lower() or 'websocket' in ep.url.lower()]

        if ws_endpoints:
            tester = WebSocketTester(self.config)
            for endpoint in ws_endpoints[:5]:  # Limit to 5
                try:
                    await tester.test_websocket(endpoint.url, test_result)
                except Exception as e:
                    logger.debug(f"Error testing WebSocket endpoint: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result
