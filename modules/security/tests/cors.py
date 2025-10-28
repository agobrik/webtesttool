"""CORS Misconfiguration Testing"""

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest


class CORSTest(BaseSecurityTest):
    name = "cors"
    description = "Tests for CORS misconfigurations"
    config_key = "cors"

    async def run_test(self, context: TestContext) -> None:
        malicious_origins = ['http://evil.com', 'null']

        for origin in malicious_origins:
            response = await self.make_request(
                context.target_url,
                headers={'Origin': origin}
            )

            acao = response.headers.get('Access-Control-Allow-Origin', '')
            acac = response.headers.get('Access-Control-Allow-Credentials', '')

            if acao == origin or acao == '*':
                severity = Severity.HIGH if acac.lower() == 'true' else Severity.MEDIUM

                self.add_finding(
                    title="CORS Misconfiguration",
                    description=f"Server reflects Origin header or uses wildcard with credentials={acac}",
                    severity=severity,
                    url=context.target_url,
                    cwe_id="CWE-942"
                )
                break
