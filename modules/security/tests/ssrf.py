"""Server-Side Request Forgery (SSRF) Testing"""

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest
from loguru import logger


class SSRFTest(BaseSecurityTest):
    """Test for SSRF vulnerabilities"""

    name = "ssrf"
    description = "Tests for Server-Side Request Forgery (SSRF) vulnerabilities"
    config_key = "ssrf"

    SSRF_PAYLOADS = [
        'http://localhost',
        'http://127.0.0.1',
        'http://0.0.0.0',
        'http://[::1]',
        'http://169.254.169.254/latest/meta-data/',  # AWS metadata
        'http://metadata.google.internal',  # GCP metadata
        'file:///etc/passwd',
        'dict://localhost:11211',
        'gopher://localhost:3306',
    ]

    async def run_test(self, context: TestContext) -> None:
        """Run SSRF tests"""

        for page in context.crawled_pages:
            # Look for URL parameters
            for form in page.forms:
                for inp in form.get('inputs', []):
                    name = inp.get('name', '').lower()
                    if any(keyword in name for keyword in ['url', 'uri', 'link', 'callback', 'webhook']):
                        await self._test_ssrf_parameter(form, page.url, inp['name'])

    async def _test_ssrf_parameter(self, form: dict, page_url: str, param_name: str) -> None:
        """Test parameter for SSRF"""

        url = form.get('action') or page_url
        method = form.get('method', 'GET').upper()

        for payload in self.SSRF_PAYLOADS[:3]:  # Limit testing
            try:
                data = {inp['name']: payload if inp['name'] == param_name else 'test'
                       for inp in form.get('inputs', []) if inp.get('name')}

                response = await self.make_request(url, method=method, data=data)

                # Check for SSRF indicators
                if self._check_ssrf_success(response.text, payload):
                    self.add_finding(
                        title="Server-Side Request Forgery (SSRF) Vulnerability",
                        description=f"SSRF vulnerability detected in parameter '{param_name}'. "
                                  "Attacker can make the server send requests to arbitrary URLs.",
                        severity=Severity.CRITICAL,
                        url=url,
                        cwe_id="CWE-918",
                        owasp_category="A10:2021-Server-Side Request Forgery",
                        parameter=param_name,
                        payload=payload
                    )

            except Exception as e:
                logger.debug(f"Error testing SSRF: {str(e)}")

    def _check_ssrf_success(self, response_text: str, payload: str) -> bool:
        """Check if SSRF was successful"""
        indicators = ['root:', 'ami-id', 'instance-id', 'metadata']
        return any(ind in response_text.lower() for ind in indicators)
