"""Information Disclosure Testing"""

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest
import re


class InfoDisclosureTest(BaseSecurityTest):
    name = "info_disclosure"
    description = "Tests for information disclosure vulnerabilities"
    config_key = "info_disclosure"

    async def run_test(self, context: TestContext) -> None:
        response = await self.make_request(context.target_url)

        # Check Server header
        server = response.headers.get('Server', '')
        if server and server not in ['nginx', 'Apache']:
            self.add_finding(
                title="Server Version Disclosure",
                description=f"Server version exposed: {server}",
                severity=Severity.LOW,
                url=context.target_url,
                cwe_id="CWE-200"
            )

        # Check for comments with sensitive info
        comments = re.findall(r'<!--(.*?)-->', response.text, re.DOTALL)
        for comment in comments:
            if any(keyword in comment.lower() for keyword in ['password', 'api key', 'secret', 'todo', 'fixme']):
                self.add_finding(
                    title="Sensitive Information in HTML Comments",
                    description="HTML comments contain potentially sensitive information",
                    severity=Severity.LOW,
                    url=context.target_url,
                    cwe_id="CWE-615"
                )
                break

        # Check error pages
        error_response = await self.make_request(context.target_url + '/nonexistent-page-test-404')
        if any(tech in error_response.text.lower() for tech in ['apache', 'nginx', 'iis', 'php', 'python', 'java']):
            self.add_finding(
                title="Technology Stack Disclosure in Error Pages",
                description="Error pages reveal technology stack information",
                severity=Severity.INFO,
                url=context.target_url,
                cwe_id="CWE-209"
            )
