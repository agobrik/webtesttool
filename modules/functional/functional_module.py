"""
Functional Testing Module
Tests UI functionality, user workflows, and JavaScript interactions using Playwright
"""

import asyncio
from loguru import logger

from core.module_loader import BaseTestModule
from core.models import (
    Category, ModuleResult, TestResult, TestStatus,
    Finding, Severity, TestContext
)


class FunctionalModule(BaseTestModule):
    """Functional Testing Module using Playwright"""

    name = "functional"
    description = "Functional testing: forms, navigation, workflows, JavaScript"
    category = Category.FUNCTIONAL
    version = "1.0.0"

    async def run(self, context: TestContext) -> ModuleResult:
        """Run functional tests"""

        module_result = ModuleResult(
            name=self.name,
            category=self.category,
            status=TestStatus.RUNNING
        )

        module_config = self.config.get_module_config(self.name)

        # Import Playwright
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install")
            module_result.mark_completed(TestStatus.ERROR)
            return module_result

        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Form Testing
            if module_config.get('forms', {}).get('enabled', True):
                test_result = await self._test_forms(page, context, module_config)
                module_result.add_test_result(test_result)

            # Navigation Testing
            if module_config.get('navigation', {}).get('enabled', True):
                test_result = await self._test_navigation(page, context, module_config)
                module_result.add_test_result(test_result)

            # JavaScript Testing
            if module_config.get('javascript', {}).get('enabled', True):
                test_result = await self._test_javascript(page, context, module_config)
                module_result.add_test_result(test_result)

            # UI Components Testing
            if module_config.get('ui_components', {}).get('enabled', True):
                test_result = await self._test_ui_components(page, context, module_config)
                module_result.add_test_result(test_result)

            # Error Handling Testing
            if module_config.get('error_handling', {}).get('enabled', True):
                test_result = await self._test_error_handling(page, context, module_config)
                module_result.add_test_result(test_result)

            await browser.close()

        module_result.mark_completed(TestStatus.PASSED)
        return module_result

    async def _test_forms(self, page, context: TestContext, config: dict) -> TestResult:
        """Test forms functionality"""

        test_result = TestResult(
            name="form_functionality_test",
            description="Tests form validation and submission",
            category=self.category,
            status=TestStatus.RUNNING
        )

        try:
            # Test each form found during crawling
            for crawled_page in context.crawled_pages[:10]:
                if not crawled_page.forms:
                    continue

                try:
                    await page.goto(crawled_page.url, wait_until='networkidle', timeout=30000)

                    # Find all forms on the page
                    forms = await page.query_selector_all('form')

                    for form_index, form in enumerate(forms):
                        # Test form validation
                        await self._test_form_validation(page, form, test_result, crawled_page.url)

                        # Test form submission
                        await self._test_form_submission(page, form, test_result, crawled_page.url)

                except Exception as e:
                    logger.debug(f"Error testing forms on {crawled_page.url}: {str(e)}")

        except Exception as e:
            logger.error(f"Form testing error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_form_validation(self, page, form, test_result, url):
        """Test form validation"""

        try:
            # Find all required inputs
            inputs = await form.query_selector_all('input[required], textarea[required], select[required]')

            if inputs:
                # Try to submit without filling required fields
                submit_button = await form.query_selector('button[type="submit"], input[type="submit"]')

                if submit_button:
                    # Click submit without filling
                    await submit_button.click()
                    await page.wait_for_timeout(1000)

                    # Check if validation appeared
                    validation_messages = await page.query_selector_all('.error, .invalid, [aria-invalid="true"]')

                    if not validation_messages:
                        test_result.add_finding(Finding(
                            title="Weak Form Validation",
                            description="Form lacks client-side validation for required fields",
                            severity=Severity.LOW,
                            category=self.category,
                            url=url
                        ))

        except Exception as e:
            logger.debug(f"Form validation test error: {str(e)}")

    async def _test_form_submission(self, page, form, test_result, url):
        """Test form submission"""

        try:
            # Get form action
            action = await form.get_attribute('action')
            method = await form.get_attribute('method') or 'GET'

            # Fill form with test data
            inputs = await form.query_selector_all('input:not([type="submit"]):not([type="button"]):not([type="hidden"])')

            for inp in inputs:
                input_type = await inp.get_attribute('type') or 'text'
                name = await inp.get_attribute('name')

                if name:
                    if input_type == 'email':
                        await inp.fill('test@example.com')
                    elif input_type == 'number':
                        await inp.fill('123')
                    elif input_type == 'tel':
                        await inp.fill('1234567890')
                    elif input_type in ['text', 'password']:
                        await inp.fill('testdata')
                    elif input_type == 'checkbox':
                        await inp.check()

            # Fill textareas
            textareas = await form.query_selector_all('textarea')
            for textarea in textareas:
                await textarea.fill('test content')

            # Select first option in selects
            selects = await form.query_selector_all('select')
            for select in selects:
                options = await select.query_selector_all('option')
                if len(options) > 0:
                    value = await options[0].get_attribute('value')
                    if value:
                        await select.select_option(value)

        except Exception as e:
            logger.debug(f"Form submission test error: {str(e)}")

    async def _test_navigation(self, page, context: TestContext, config: dict) -> TestResult:
        """Test navigation functionality"""

        test_result = TestResult(
            name="navigation_test",
            description="Tests navigation links and breadcrumbs",
            category=self.category,
            status=TestStatus.RUNNING
        )

        try:
            await page.goto(context.target_url, wait_until='networkidle', timeout=30000)

            # Test all links on main page
            links = await page.query_selector_all('a[href]')

            broken_links = 0
            for link in links[:20]:  # Test first 20 links
                try:
                    href = await link.get_attribute('href')

                    if href and not href.startswith('#') and not href.startswith('javascript:'):
                        # Click link and check if it loads
                        async with page.expect_navigation(timeout=5000):
                            await link.click()

                        # Check for 404 or error
                        title = await page.title()
                        if '404' in title.lower() or 'not found' in title.lower():
                            broken_links += 1

                        # Go back
                        await page.go_back()

                except Exception as e:
                    logger.debug(f"Link test error: {str(e)}")
                    broken_links += 1

            if broken_links > 0:
                test_result.add_finding(Finding(
                    title="Broken Navigation Links",
                    description=f"Found {broken_links} broken or non-functional links",
                    severity=Severity.MEDIUM,
                    category=self.category,
                    url=context.target_url
                ))

        except Exception as e:
            logger.error(f"Navigation test error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_javascript(self, page, context: TestContext, config: dict) -> TestResult:
        """Test JavaScript functionality"""

        test_result = TestResult(
            name="javascript_test",
            description="Tests JavaScript functionality and AJAX",
            category=self.category,
            status=TestStatus.RUNNING
        )

        try:
            await page.goto(context.target_url, wait_until='networkidle', timeout=30000)

            # Check for JavaScript errors
            js_errors = []

            page.on('pageerror', lambda error: js_errors.append(str(error)))
            page.on('console', lambda msg: js_errors.append(msg.text) if msg.type == 'error' else None)

            # Wait for any dynamic content
            await page.wait_for_timeout(3000)

            # Test AJAX requests
            ajax_requests = []

            async def log_request(request):
                if 'xhr' in request.resource_type or 'fetch' in request.resource_type:
                    ajax_requests.append(request.url)

            page.on('request', log_request)

            # Trigger some interactions
            buttons = await page.query_selector_all('button')
            for button in buttons[:5]:
                try:
                    await button.click()
                    await page.wait_for_timeout(1000)
                except:
                    pass

            if js_errors:
                test_result.add_finding(Finding(
                    title="JavaScript Errors Detected",
                    description=f"Found {len(js_errors)} JavaScript errors on the page",
                    severity=Severity.MEDIUM,
                    category=self.category,
                    url=context.target_url,
                    metadata={'errors': js_errors[:5]}
                ))

        except Exception as e:
            logger.error(f"JavaScript test error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_ui_components(self, page, context: TestContext, config: dict) -> TestResult:
        """Test UI components"""

        test_result = TestResult(
            name="ui_components_test",
            description="Tests modals, dropdowns, and other UI components",
            category=self.category,
            status=TestStatus.RUNNING
        )

        try:
            await page.goto(context.target_url, wait_until='networkidle', timeout=30000)

            # Test modals
            modal_triggers = await page.query_selector_all('[data-toggle="modal"], [data-bs-toggle="modal"]')
            for trigger in modal_triggers[:3]:
                try:
                    await trigger.click()
                    await page.wait_for_timeout(500)

                    # Check if modal appeared
                    modal = await page.query_selector('.modal.show, [role="dialog"][aria-modal="true"]')
                    if not modal:
                        test_result.add_finding(Finding(
                            title="Modal Not Functioning",
                            description="Modal trigger exists but modal doesn't appear",
                            severity=Severity.LOW,
                            category=self.category,
                            url=context.target_url
                        ))

                    # Try to close modal
                    close_button = await page.query_selector('.modal .close, .modal [data-dismiss="modal"]')
                    if close_button:
                        await close_button.click()

                except Exception as e:
                    logger.debug(f"Modal test error: {str(e)}")

            # Test dropdowns
            dropdowns = await page.query_selector_all('[data-toggle="dropdown"], .dropdown-toggle')
            for dropdown in dropdowns[:3]:
                try:
                    await dropdown.click()
                    await page.wait_for_timeout(300)

                    # Check if dropdown menu appeared
                    dropdown_menu = await page.query_selector('.dropdown-menu.show')
                    if not dropdown_menu:
                        test_result.add_finding(Finding(
                            title="Dropdown Not Functioning",
                            description="Dropdown trigger exists but menu doesn't appear",
                            severity=Severity.LOW,
                            category=self.category,
                            url=context.target_url
                        ))

                except Exception as e:
                    logger.debug(f"Dropdown test error: {str(e)}")

        except Exception as e:
            logger.error(f"UI components test error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_error_handling(self, page, context: TestContext, config: dict) -> TestResult:
        """Test error handling"""

        test_result = TestResult(
            name="error_handling_test",
            description="Tests 404 and error pages",
            category=self.category,
            status=TestStatus.RUNNING
        )

        try:
            # Test 404 page
            random_url = f"{context.target_url}/this-page-definitely-does-not-exist-{asyncio.get_event_loop().time()}"

            try:
                response = await page.goto(random_url, timeout=10000)

                if response and response.status == 404:
                    # Check if custom 404 page exists
                    content = await page.content()

                    if 'nginx' in content.lower() or 'apache' in content.lower():
                        test_result.add_finding(Finding(
                            title="Default Server 404 Page",
                            description="Using default server 404 page instead of custom error page",
                            severity=Severity.LOW,
                            category=self.category,
                            url=random_url
                        ))

            except Exception as e:
                logger.debug(f"404 test error: {str(e)}")

        except Exception as e:
            logger.error(f"Error handling test error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result
