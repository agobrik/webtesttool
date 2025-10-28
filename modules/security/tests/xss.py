"""
Cross-Site Scripting (XSS) Testing
Tests for reflected, stored, and DOM-based XSS vulnerabilities
"""

import asyncio
import re
from typing import List, Dict
from urllib.parse import urlencode, parse_qs, urlparse
from loguru import logger

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest


class XSSTest(BaseSecurityTest):
    """
    XSS Test
    Tests for Cross-Site Scripting vulnerabilities
    """

    name = "xss"
    description = "Tests for Cross-Site Scripting (XSS) vulnerabilities"
    config_key = "xss"

    # XSS Payloads
    XSS_PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src=javascript:alert('XSS')>",
        "<body onload=alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "<select onfocus=alert('XSS') autofocus>",
        "<textarea onfocus=alert('XSS') autofocus>",
        "<keygen onfocus=alert('XSS') autofocus>",
        "<video><source onerror=alert('XSS')>",
        "<audio src=x onerror=alert('XSS')>",
        "<details open ontoggle=alert('XSS')>",
        "'-alert('XSS')-'",
        "\"><script>alert('XSS')</script>",
        "'/><script>alert('XSS')</script>",
        "<scr<script>ipt>alert('XSS')</scr</script>ipt>",
        "%3Cscript%3Ealert('XSS')%3C/script%3E",
    ]

    # DOM-based XSS patterns
    DOM_XSS_SOURCES = [
        'document.URL',
        'document.documentURI',
        'location',
        'location.href',
        'location.search',
        'location.hash',
        'location.pathname',
        'window.name',
        'document.referrer',
    ]

    DOM_XSS_SINKS = [
        'eval(',
        'setTimeout(',
        'setInterval(',
        'Function(',
        '.innerHTML',
        '.outerHTML',
        'document.write(',
        'document.writeln(',
        '.insertAdjacentHTML',
    ]

    async def run_test(self, context: TestContext) -> None:
        """Run XSS tests"""

        test_types = self.get_config_value('test_types', ['reflected', 'stored', 'dom'])

        tasks = []

        if 'reflected' in test_types:
            tasks.append(self._test_reflected_xss(context))

        if 'dom' in test_types:
            tasks.append(self._test_dom_xss(context))

        # Note: Stored XSS testing is limited as it requires multiple page visits
        if 'stored' in test_types:
            tasks.append(self._test_stored_xss(context))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _test_reflected_xss(self, context: TestContext) -> None:
        """Test for reflected XSS vulnerabilities"""

        logger.info("Testing for reflected XSS")

        test_targets = []

        # Collect all testable inputs
        for page in context.crawled_pages:
            # Test URL parameters
            parsed = urlparse(page.url)
            if parsed.query:
                params = parse_qs(parsed.query)
                if params:
                    test_targets.append({
                        'type': 'url_param',
                        'url': page.url,
                        'params': params
                    })

            # Test forms
            for form in page.forms:
                if form.get('inputs'):
                    test_targets.append({
                        'type': 'form',
                        'url': form.get('action') or page.url,
                        'method': form.get('method', 'GET'),
                        'inputs': form.get('inputs', [])
                    })

        # Test each target with payloads
        for target in test_targets[:30]:  # Limit testing
            await self._test_target_for_xss(target, context)

    async def _test_target_for_xss(self, target: Dict, context: TestContext) -> None:
        """Test a specific target for XSS"""

        url = target['url']

        for payload in self.XSS_PAYLOADS[:5]:  # Use subset of payloads
            try:
                if target['type'] == 'form':
                    method = target.get('method', 'GET').upper()
                    data = {inp['name']: payload for inp in target.get('inputs', []) if inp.get('name')}

                    response = await self.make_request(url, method=method, data=data)

                elif target['type'] == 'url_param':
                    params = target.get('params', {})
                    for param_name in params:
                        test_params = params.copy()
                        test_params[param_name] = payload

                        test_url = f"{url.split('?')[0]}?{urlencode(test_params, doseq=True)}"
                        response = await self.make_request(test_url, method='GET')

                        # Check if payload is reflected in response
                        if self._check_xss_reflection(payload, response.text):
                            self.add_finding(
                                title="Reflected Cross-Site Scripting (XSS) Vulnerability",
                                description=f"Reflected XSS vulnerability detected in parameter '{param_name}'. "
                                          f"User input is reflected in the response without proper sanitization, "
                                          f"allowing execution of malicious JavaScript code.",
                                severity=Severity.HIGH,
                                url=test_url,
                                evidence=[
                                    self.create_evidence(
                                        "request",
                                        f"GET {test_url}\nPayload: {payload}",
                                        "Request with XSS payload"
                                    ),
                                    self.create_evidence(
                                        "response",
                                        response.text[:500],
                                        "Response reflecting XSS payload"
                                    )
                                ],
                                recommendations=[
                                    self.create_recommendation(
                                        "Implement Output Encoding",
                                        "Encode all user-supplied data before rendering in HTML context. "
                                        "Use context-appropriate encoding (HTML, JavaScript, URL, CSS).",
                                        references=[
                                            "https://owasp.org/www-community/attacks/xss/",
                                            "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"
                                        ],
                                        code_example="# Python example\nfrom html import escape\nsafe_output = escape(user_input)"
                                    ),
                                    self.create_recommendation(
                                        "Implement Content Security Policy (CSP)",
                                        "Use CSP headers to restrict sources of executable scripts.",
                                        code_example="Content-Security-Policy: default-src 'self'; script-src 'self'"
                                    )
                                ],
                                cwe_id="CWE-79",
                                owasp_category="A03:2021-Injection",
                                parameter=param_name,
                                payload=payload
                            )

            except Exception as e:
                logger.debug(f"Error testing XSS on {url}: {str(e)}")

    async def _test_dom_xss(self, context: TestContext) -> None:
        """Test for DOM-based XSS vulnerabilities"""

        logger.info("Testing for DOM-based XSS")

        for page in context.crawled_pages:
            # Get all JavaScript sources
            try:
                response = await self.make_request(page.url)
                html_content = response.text

                # Check for DOM XSS patterns in inline scripts
                if self._check_dom_xss_patterns(html_content):
                    self.add_finding(
                        title="Potential DOM-based XSS Vulnerability",
                        description="The page contains JavaScript code that uses potentially dangerous "
                                  "DOM sources (like location.href) and sinks (like innerHTML) which "
                                  "could lead to DOM-based XSS if not properly sanitized.",
                        severity=Severity.MEDIUM,
                        url=page.url,
                        evidence=[
                            self.create_evidence(
                                "javascript",
                                "DOM XSS patterns detected in JavaScript code",
                                "Potentially vulnerable code patterns"
                            )
                        ],
                        recommendations=[
                            self.create_recommendation(
                                "Sanitize DOM Sources",
                                "Always sanitize data from DOM sources before using in sinks. "
                                "Use textContent instead of innerHTML when possible.",
                                code_example="// Bad\nelement.innerHTML = location.hash;\n\n// Good\nelement.textContent = location.hash;"
                            )
                        ],
                        cwe_id="CWE-79",
                        owasp_category="A03:2021-Injection"
                    )

                # Also check external scripts
                for script_url in page.scripts:
                    await self._check_external_script_for_dom_xss(script_url, page.url)

            except Exception as e:
                logger.debug(f"Error testing DOM XSS on {page.url}: {str(e)}")

    async def _test_stored_xss(self, context: TestContext) -> None:
        """Test for stored XSS vulnerabilities"""

        logger.info("Testing for stored XSS")

        # Find forms that might store data (e.g., comments, profiles)
        for page in context.crawled_pages:
            for form in page.forms:
                method = form.get('method', 'GET').upper()

                # Only test POST forms (more likely to store data)
                if method == 'POST':
                    url = form.get('action') or page.url
                    inputs = form.get('inputs', [])

                    # Submit form with XSS payload
                    payload = "<script>alert('Stored-XSS')</script>"
                    data = {}

                    for inp in inputs:
                        name = inp.get('name')
                        if name:
                            if inp.get('type') in ['text', 'textarea', 'email']:
                                data[name] = payload
                            else:
                                data[name] = 'test'

                    try:
                        # Submit the form
                        response = await self.make_request(url, method=method, data=data)

                        # Check if payload is in response (might be stored)
                        if payload in response.text or self._check_xss_reflection(payload, response.text):
                            self.add_finding(
                                title="Potential Stored XSS Vulnerability",
                                description="The application appears to store user input and display it "
                                          "without proper sanitization, potentially allowing stored XSS attacks.",
                                severity=Severity.CRITICAL,
                                url=url,
                                cwe_id="CWE-79",
                                owasp_category="A03:2021-Injection",
                                payload=payload
                            )

                    except Exception as e:
                        logger.debug(f"Error testing stored XSS: {str(e)}")

    def _check_xss_reflection(self, payload: str, response_text: str) -> bool:
        """
        Check if XSS payload is reflected in response

        Args:
            payload: XSS payload
            response_text: HTTP response text

        Returns:
            True if payload is reflected without encoding
        """
        # Check for exact match
        if payload in response_text:
            return True

        # Check for partially reflected payload (without encoding)
        dangerous_parts = ['<script', 'onerror', 'onload', 'javascript:', 'alert(']
        for part in dangerous_parts:
            if part.lower() in payload.lower() and part.lower() in response_text.lower():
                return True

        return False

    def _check_dom_xss_patterns(self, javascript_code: str) -> bool:
        """
        Check for DOM XSS patterns in JavaScript code

        Args:
            javascript_code: JavaScript code to check

        Returns:
            True if DOM XSS patterns found
        """
        # Check for sources and sinks
        has_source = any(source in javascript_code for source in self.DOM_XSS_SOURCES)
        has_sink = any(sink in javascript_code for sink in self.DOM_XSS_SINKS)

        return has_source and has_sink

    async def _check_external_script_for_dom_xss(self, script_url: str, page_url: str) -> None:
        """Check external JavaScript file for DOM XSS patterns"""

        try:
            response = await self.make_request(script_url)

            if 'javascript' in response.headers.get('content-type', '').lower():
                if self._check_dom_xss_patterns(response.text):
                    self.add_finding(
                        title="Potential DOM-based XSS in External Script",
                        description=f"External script {script_url} contains DOM XSS patterns.",
                        severity=Severity.MEDIUM,
                        url=page_url,
                        cwe_id="CWE-79",
                        owasp_category="A03:2021-Injection",
                        script_url=script_url
                    )

        except Exception as e:
            logger.debug(f"Error checking external script {script_url}: {str(e)}")
