"""Open Redirect Testing"""

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest
from urllib.parse import parse_qs, urlparse


class OpenRedirectTest(BaseSecurityTest):
    name = "open_redirect"
    description = "Tests for open redirect vulnerabilities"
    config_key = "open_redirect"

    PAYLOADS = [
        'http://evil.com',
        '//evil.com',
        '\/\/evil.com',
        'https://evil.com',
    ]

    async def run_test(self, context: TestContext) -> None:
        for page in context.crawled_pages[:20]:
            parsed = urlparse(page.url)
            if parsed.query:
                params = parse_qs(parsed.query)
                for param in params:
                    if any(k in param.lower() for k in ['url', 'redirect', 'return', 'next', 'goto', 'redir']):
                        await self._test_open_redirect(page.url, param)

    async def _test_open_redirect(self, url: str, param: str) -> None:
        for payload in self.PAYLOADS[:2]:
            try:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                params[param] = payload

                from urllib.parse import urlencode, urlunparse
                test_url = urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path,
                    parsed.params, urlencode(params, doseq=True), ''
                ))

                response = await self.make_request(test_url, allow_redirects=False)

                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location', '')
                    if 'evil.com' in location:
                        self.add_finding(
                            title="Open Redirect Vulnerability",
                            description=f"Parameter '{param}' allows arbitrary redirects",
                            severity=Severity.MEDIUM,
                            url=url,
                            cwe_id="CWE-601",
                            parameter=param
                        )
                        return
            except:
                pass
