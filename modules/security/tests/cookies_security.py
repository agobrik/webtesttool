"""Cookie Security Testing"""

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest


class CookiesSecurityTest(BaseSecurityTest):
    name = "cookies_security"
    description = "Tests cookie security attributes"
    config_key = "cookies_security"

    async def run_test(self, context: TestContext) -> None:
        response = await self.make_request(context.target_url)

        for cookie in response.cookies.jar:
            issues = []

            if not cookie.secure:
                issues.append("Missing Secure flag")
            if not cookie.has_nonstandard_attr('HttpOnly'):
                issues.append("Missing HttpOnly flag")
            if not cookie.has_nonstandard_attr('SameSite'):
                issues.append("Missing SameSite attribute")

            if issues:
                self.add_finding(
                    title=f"Insecure Cookie: {cookie.name}",
                    description=f"Cookie has security issues: {', '.join(issues)}",
                    severity=Severity.MEDIUM,
                    url=context.target_url,
                    cwe_id="CWE-614",
                    cookie_name=cookie.name
                )
