"""Clickjacking Testing"""

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest


class ClickjackingTest(BaseSecurityTest):
    name = "clickjacking"
    description = "Tests for clickjacking vulnerabilities"
    config_key = "clickjacking"

    async def run_test(self, context: TestContext) -> None:
        response = await self.make_request(context.target_url)

        x_frame = response.headers.get('X-Frame-Options', '').upper()
        csp = response.headers.get('Content-Security-Policy', '').lower()

        has_frame_protection = (
            x_frame in ['DENY', 'SAMEORIGIN'] or
            'frame-ancestors' in csp
        )

        if not has_frame_protection:
            self.add_finding(
                title="Clickjacking Vulnerability",
                description="Page can be framed, vulnerable to clickjacking attacks",
                severity=Severity.MEDIUM,
                url=context.target_url,
                recommendations=[
                    self.create_recommendation(
                        "Add Frame Protection",
                        "Set X-Frame-Options header or CSP frame-ancestors directive",
                        code_example="X-Frame-Options: DENY\nContent-Security-Policy: frame-ancestors 'self'"
                    )
                ],
                cwe_id="CWE-1021"
            )
