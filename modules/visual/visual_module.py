"""
Visual Regression Testing Module
Takes screenshots and compares them with baselines
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict
from loguru import logger

from core.module_loader import BaseTestModule
from core.models import (
    Category, ModuleResult, TestResult, TestStatus,
    Finding, Severity, TestContext
)


class VisualModule(BaseTestModule):
    """Visual Regression Testing Module"""

    name = "visual"
    description = "Visual regression testing with screenshot comparison"
    category = Category.VISUAL
    version = "1.0.0"

    async def run(self, context: TestContext) -> ModuleResult:
        """Run visual regression tests"""

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
            logger.error("Playwright not installed")
            module_result.mark_completed(TestStatus.ERROR)
            return module_result

        # Screenshot comparison enabled?
        if not module_config.get('screenshot_comparison', True):
            module_result.mark_completed(TestStatus.SKIPPED)
            return module_result

        test_result = TestResult(
            name="visual_regression_test",
            description="Visual regression testing with screenshots",
            category=self.category,
            status=TestStatus.RUNNING
        )

        baseline_dir = module_config.get('baseline_dir', 'baselines/')
        screenshots_dir = 'screenshots/'
        threshold = module_config.get('threshold', 0.1)

        # Create directories
        os.makedirs(baseline_dir, exist_ok=True)
        os.makedirs(screenshots_dir, exist_ok=True)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Test main page and important pages
            test_urls = [context.target_url] + [p.url for p in context.crawled_pages[:5]]

            for url in test_urls:
                try:
                    await page.goto(url, wait_until='networkidle', timeout=30000)

                    # Generate filename from URL
                    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
                    screenshot_name = f"{url_hash}.png"

                    baseline_path = os.path.join(baseline_dir, screenshot_name)
                    current_path = os.path.join(screenshots_dir, screenshot_name)

                    # Take screenshot
                    await page.screenshot(path=current_path, full_page=True)

                    # Compare with baseline if exists
                    if os.path.exists(baseline_path):
                        difference = await self._compare_screenshots(baseline_path, current_path, threshold)

                        if difference > threshold:
                            test_result.add_finding(Finding(
                                title="Visual Regression Detected",
                                description=f"Page has visual changes: {difference*100:.1f}% different from baseline",
                                severity=Severity.MEDIUM,
                                category=self.category,
                                url=url,
                                metadata={
                                    'difference_percentage': difference * 100,
                                    'baseline': baseline_path,
                                    'current': current_path
                                }
                            ))

                    else:
                        # No baseline, save current as baseline
                        import shutil
                        shutil.copy(current_path, baseline_path)
                        logger.info(f"Created baseline for {url}")

                except Exception as e:
                    logger.error(f"Visual test error for {url}: {str(e)}")

            # Test responsive design
            await self._test_responsive_design(page, context.target_url, test_result)

            await browser.close()

        test_result.mark_completed(TestStatus.PASSED)
        module_result.add_test_result(test_result)
        module_result.mark_completed(TestStatus.PASSED)
        return module_result

    async def _compare_screenshots(self, baseline_path: str, current_path: str, threshold: float) -> float:
        """
        Compare two screenshots

        Returns:
            Difference percentage (0.0 to 1.0)
        """
        try:
            from PIL import Image
            import numpy as np

            # Load images
            baseline = Image.open(baseline_path)
            current = Image.open(current_path)

            # Ensure same size
            if baseline.size != current.size:
                current = current.resize(baseline.size)

            # Convert to arrays
            baseline_arr = np.array(baseline)
            current_arr = np.array(current)

            # Calculate difference
            diff = np.abs(baseline_arr.astype(float) - current_arr.astype(float))
            total_diff = np.sum(diff)
            max_diff = baseline_arr.size * 255

            difference = total_diff / max_diff

            return difference

        except Exception as e:
            logger.error(f"Screenshot comparison error: {str(e)}")
            return 0.0

    async def _test_responsive_design(self, page, url: str, test_result: TestResult):
        """Test responsive design at different viewports"""

        viewports = [
            {'name': 'Mobile', 'width': 375, 'height': 667},
            {'name': 'Tablet', 'width': 768, 'height': 1024},
            {'name': 'Desktop', 'width': 1920, 'height': 1080}
        ]

        try:
            for viewport in viewports:
                await page.set_viewport_size({'width': viewport['width'], 'height': viewport['height']})
                await page.goto(url, wait_until='networkidle', timeout=30000)

                # Check for horizontal scrollbars (bad on mobile)
                if viewport['name'] == 'Mobile':
                    scroll_width = await page.evaluate('document.documentElement.scrollWidth')
                    viewport_width = viewport['width']

                    if scroll_width > viewport_width + 10:  # 10px tolerance
                        test_result.add_finding(Finding(
                            title="Horizontal Scroll on Mobile",
                            description=f"Page causes horizontal scrolling on mobile ({scroll_width}px > {viewport_width}px)",
                            severity=Severity.MEDIUM,
                            category=self.category,
                            url=url
                        ))

                # Check for layout shifts
                layout_shift = await page.evaluate('''
                    () => {
                        let cumulativeLayoutShift = 0;
                        const observer = new PerformanceObserver((list) => {
                            for (const entry of list.getEntries()) {
                                if (!entry.hadRecentInput) {
                                    cumulativeLayoutShift += entry.value;
                                }
                            }
                        });
                        observer.observe({type: 'layout-shift', buffered: true});
                        return cumulativeLayoutShift;
                    }
                ''')

                if layout_shift > 0.1:  # CLS threshold
                    test_result.add_finding(Finding(
                        title="Cumulative Layout Shift Detected",
                        description=f"High layout shift score on {viewport['name']}: {layout_shift:.3f}",
                        severity=Severity.LOW,
                        category=self.category,
                        url=url,
                        metadata={'viewport': viewport['name'], 'cls_score': layout_shift}
                    ))

        except Exception as e:
            logger.error(f"Responsive design test error: {str(e)}")
