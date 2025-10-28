"""Accessibility Testing Module"""

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from core.module_loader import BaseTestModule
from core.models import Category, ModuleResult, TestResult, TestStatus, Finding, Severity, TestContext


class AccessibilityModule(BaseTestModule):
    """Accessibility Testing Module (WCAG 2.1)"""

    name = "accessibility"
    description = "Accessibility testing based on WCAG 2.1 guidelines"
    category = Category.ACCESSIBILITY
    version = "1.0.0"

    async def run(self, context: TestContext) -> ModuleResult:
        module_result = ModuleResult(name=self.name, category=self.category, status=TestStatus.RUNNING)
        test_result = TestResult(name="wcag_compliance", description="WCAG 2.1 compliance check",
                                category=self.category, status=TestStatus.RUNNING)

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(context.target_url)
                soup = BeautifulSoup(response.text, 'lxml')

                # Check for lang attribute
                html_tag = soup.find('html')
                if not html_tag or not html_tag.get('lang'):
                    test_result.add_finding(Finding(
                        title="Missing Language Attribute",
                        description="<html> tag missing lang attribute",
                        severity=Severity.MEDIUM, category=self.category, url=context.target_url
                    ))

                # Images without alt text
                images = soup.find_all('img')
                for img in images:
                    if not img.get('alt'):
                        test_result.add_finding(Finding(
                            title="Image Missing Alt Text",
                            description=f"Image missing alt: {img.get('src', 'unknown')}",
                            severity=Severity.HIGH, category=self.category, url=context.target_url
                        ))

                # Form inputs without labels
                inputs = soup.find_all(['input', 'textarea', 'select'])
                for inp in inputs:
                    inp_id = inp.get('id')
                    inp_name = inp.get('name')
                    # Check if there's a label for this input
                    if inp_id:
                        label = soup.find('label', {'for': inp_id})
                        if not label and not inp.get('aria-label'):
                            test_result.add_finding(Finding(
                                title="Form Input Without Label",
                                description=f"Input '{inp_name or inp_id}' has no associated label",
                                severity=Severity.HIGH, category=self.category, url=context.target_url
                            ))

                # Check heading hierarchy
                headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if headings:
                    prev_level = 0
                    for heading in headings:
                        level = int(heading.name[1])
                        if level > prev_level + 1:
                            test_result.add_finding(Finding(
                                title="Skipped Heading Level",
                                description=f"Heading hierarchy skips from h{prev_level} to h{level}",
                                severity=Severity.MEDIUM, category=self.category, url=context.target_url
                            ))
                        prev_level = level

                # Links with empty text
                links = soup.find_all('a')
                for link in links:
                    if not link.get_text(strip=True) and not link.get('aria-label'):
                        test_result.add_finding(Finding(
                            title="Empty Link Text",
                            description=f"Link has no text: {link.get('href', 'unknown')}",
                            severity=Severity.HIGH, category=self.category, url=context.target_url
                        ))

                # ARIA landmarks
                landmarks = soup.find_all(attrs={"role": True})
                if not landmarks and not soup.find_all(['header', 'nav', 'main', 'footer', 'aside']):
                    test_result.add_finding(Finding(
                        title="No ARIA Landmarks",
                        description="Page lacks ARIA landmarks or HTML5 semantic elements",
                        severity=Severity.MEDIUM, category=self.category, url=context.target_url
                    ))

        except Exception as e:
            logger.error(f"Accessibility test error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        module_result.add_test_result(test_result)
        module_result.mark_completed(TestStatus.PASSED)
        return module_result
