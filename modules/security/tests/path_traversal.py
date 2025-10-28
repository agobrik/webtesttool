"""Path Traversal Testing"""

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest
from loguru import logger


class PathTraversalTest(BaseSecurityTest):
    name = "path_traversal"
    description = "Tests for path traversal vulnerabilities"
    config_key = "path_traversal"

    PAYLOADS = [
        '../../../etc/passwd',
        '..\\..\\..\\windows\\win.ini',
        '....//....//....//etc/passwd',
        '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',
    ]

    async def run_test(self, context: TestContext) -> None:
        for page in context.crawled_pages[:10]:
            for form in page.forms:
                for inp in form.get('inputs', []):
                    if any(k in inp.get('name', '').lower() for k in ['file', 'path', 'dir', 'folder']):
                        await self._test_lfi(form, page.url, inp['name'])

    async def _test_lfi(self, form: dict, page_url: str, param: str) -> None:
        url = form.get('action') or page_url
        for payload in self.PAYLOADS[:2]:
            try:
                data = {inp['name']: payload if inp['name'] == param else 'test'
                       for inp in form.get('inputs', []) if inp.get('name')}
                response = await self.make_request(url, method=form.get('method', 'GET'), data=data)

                if 'root:' in response.text or '[extensions]' in response.text:
                    self.add_finding(
                        title="Path Traversal Vulnerability",
                        description=f"LFI/Path traversal in '{param}'",
                        severity=Severity.HIGH,
                        url=url,
                        cwe_id="CWE-22"
                    )
            except:
                pass
