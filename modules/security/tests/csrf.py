"""
Cross-Site Request Forgery (CSRF) Testing
"""

from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest
from loguru import logger


class CSRFTest(BaseSecurityTest):
    """Test for CSRF vulnerabilities"""

    name = "csrf"
    description = "Tests for Cross-Site Request Forgery (CSRF) vulnerabilities"
    config_key = "csrf"

    CSRF_TOKEN_NAMES = ['csrf', 'csrf_token', 'token', '_token', 'xsrf', 'authenticity_token']

    async def run_test(self, context: TestContext) -> None:
        """Run CSRF tests"""

        logger.info("Testing for CSRF vulnerabilities")

        for page in context.crawled_pages:
            for form in page.forms:
                method = form.get('method', 'GET').upper()

                # CSRF is primarily a concern for state-changing requests (POST, PUT, DELETE)
                if method in ['POST', 'PUT', 'DELETE']:
                    await self._test_form_csrf(form, page.url, context)

    async def _test_form_csrf(self, form: dict, page_url: str, context: TestContext) -> None:
        """Test a form for CSRF protection"""

        inputs = form.get('inputs', [])
        has_csrf_token = False

        # Check if form has CSRF token
        for inp in inputs:
            name = inp.get('name', '').lower()
            if any(token_name in name for token_name in self.CSRF_TOKEN_NAMES):
                has_csrf_token = True
                break

        if not has_csrf_token:
            # Check for CSRF header requirement
            action_url = form.get('action') or page_url

            try:
                # Try to submit form without CSRF token
                data = {inp['name']: 'test' for inp in inputs if inp.get('name')}
                method = form.get('method', 'POST').upper()

                response = await self.make_request(action_url, method=method, data=data)

                # If request succeeds (not 403/401), likely vulnerable
                if response.status_code not in [401, 403]:
                    self.add_finding(
                        title="Missing CSRF Protection",
                        description=f"Form at {page_url} does not appear to have CSRF protection. "
                                  "State-changing operations should be protected against CSRF attacks.",
                        severity=Severity.HIGH,
                        url=page_url,
                        evidence=[
                            self.create_evidence(
                                "form",
                                f"Action: {action_url}\nMethod: {method}",
                                "Form without CSRF token"
                            )
                        ],
                        recommendations=[
                            self.create_recommendation(
                                "Implement CSRF Tokens",
                                "Add CSRF tokens to all state-changing forms and validate them on the server.",
                                references=["https://owasp.org/www-community/attacks/csrf"],
                                code_example="<input type='hidden' name='csrf_token' value='{{ csrf_token }}'>"
                            ),
                            self.create_recommendation(
                                "Set SameSite Cookie Attribute",
                                "Set SameSite=Strict or Lax on session cookies.",
                                code_example="Set-Cookie: session=xxx; SameSite=Strict; Secure; HttpOnly"
                            )
                        ],
                        cwe_id="CWE-352",
                        owasp_category="A01:2021-Broken Access Control"
                    )

            except Exception as e:
                logger.debug(f"Error testing CSRF: {str(e)}")
