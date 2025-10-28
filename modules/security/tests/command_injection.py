"""Command Injection Testing"""

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest
from loguru import logger
import time


class CommandInjectionTest(BaseSecurityTest):
    """Test for command injection vulnerabilities"""

    name = "command_injection"
    description = "Tests for OS command injection vulnerabilities"
    config_key = "command_injection"

    CMD_PAYLOADS = [
        '; whoami',
        '| whoami',
        '& whoami',
        '`whoami`',
        '$(whoami)',
        '; sleep 5',
        '| ping -c 5 127.0.0.1',
        '& timeout 5',
    ]

    async def run_test(self, context: TestContext) -> None:
        """Run command injection tests"""

        for page in context.crawled_pages[:10]:
            for form in page.forms:
                # Look for inputs that might execute commands
                for inp in form.get('inputs', []):
                    name = inp.get('name', '').lower()
                    if any(k in name for k in ['file', 'path', 'cmd', 'command', 'exec', 'system']):
                        await self._test_command_injection(form, page.url, inp['name'])

    async def _test_command_injection(self, form: dict, page_url: str, param_name: str) -> None:
        """Test for command injection"""

        url = form.get('action') or page_url
        method = form.get('method', 'POST').upper()

        for payload in self.CMD_PAYLOADS[:3]:
            try:
                start_time = time.time()

                data = {inp['name']: payload if inp['name'] == param_name else 'test'
                       for inp in form.get('inputs', []) if inp.get('name')}

                response = await self.make_request(url, method=method, data=data)
                elapsed = time.time() - start_time

                # Check for command execution indicators
                if 'whoami' in payload and any(user in response.text.lower()
                                              for user in ['root', 'admin', 'www-data', 'apache']):
                    self.add_finding(
                        title="OS Command Injection Vulnerability",
                        description=f"Command injection detected in '{param_name}'. Commands are executed on server.",
                        severity=Severity.CRITICAL,
                        url=url,
                        cwe_id="CWE-78",
                        owasp_category="A03:2021-Injection"
                    )

                # Time-based detection
                elif 'sleep' in payload and elapsed > 4:
                    self.add_finding(
                        title="Possible Command Injection (Time-based)",
                        description=f"Time-based command injection detected. Server delayed {elapsed:.2f}s.",
                        severity=Severity.HIGH,
                        url=url,
                        cwe_id="CWE-78"
                    )

            except Exception as e:
                logger.debug(f"Error testing command injection: {str(e)}")
