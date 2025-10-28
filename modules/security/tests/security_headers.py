"""Security Headers Testing"""

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest


class SecurityHeadersTest(BaseSecurityTest):
    name = "security_headers"
    description = "Tests for missing or misconfigured security headers"
    config_key = "security_headers"

    REQUIRED_HEADERS = {
        'X-Frame-Options': ('DENY', 'SAMEORIGIN'),
        'X-Content-Type-Options': ('nosniff',),
        'Strict-Transport-Security': None,
        'Content-Security-Policy': None,
        'X-XSS-Protection': ('1',),
        'Referrer-Policy': ('no-referrer', 'strict-origin'),
        'Permissions-Policy': None,
    }

    async def run_test(self, context: TestContext) -> None:
        response = await self.make_request(context.target_url)
        headers = {k.lower(): v for k, v in response.headers.items()}

        for header_name, expected_values in self.REQUIRED_HEADERS.items():
            header_key = header_name.lower()

            if header_key not in headers:
                severity = Severity.MEDIUM if header_name in ['Permissions-Policy', 'Referrer-Policy'] else Severity.HIGH

                self.add_finding(
                    title=f"Missing Security Header: {header_name}",
                    description=f"The {header_name} header is not set, leaving the application vulnerable.",
                    severity=severity,
                    url=context.target_url,
                    recommendations=[
                        self.create_recommendation(
                            f"Add {header_name} Header",
                            f"Configure your web server to include the {header_name} header.",
                            references=["https://owasp.org/www-project-secure-headers/"]
                        )
                    ],
                    cwe_id="CWE-16"
                )
            elif expected_values:
                header_value = headers[header_key].lower()
                if not any(exp.lower() in header_value for exp in expected_values):
                    self.add_finding(
                        title=f"Weak Security Header: {header_name}",
                        description=f"{header_name} is set but with weak value: {headers[header_key]}",
                        severity=Severity.LOW,
                        url=context.target_url,
                        cwe_id="CWE-16"
                    )
