"""
Test Engine - Main orchestration engine for running tests
"""

import asyncio
from typing import Optional
from loguru import logger

from .config import ConfigManager
from .scanner import WebScanner
from .module_loader import ModuleLoader, BaseTestModule
from .models import (
    ScanResult, ModuleResult, TestContext, TestStatus
)
from utils.progress_tracker import ProgressTracker


class TestEngine:
    """
    Test Engine
    Main orchestration engine that coordinates scanning, module execution, and reporting
    """

    def __init__(self, config: ConfigManager, enable_progress_display: bool = True):
        """
        Initialize Test Engine

        Args:
            config: Configuration manager
            enable_progress_display: Enable live progress display (disable for CI/CD)
        """
        self.config = config
        self.scanner = WebScanner(config)
        self.module_loader = ModuleLoader(config)
        self.scan_result: Optional[ScanResult] = None
        self.progress = ProgressTracker(enable_live_display=enable_progress_display)

        # Setup logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        log_level = self.config.config.logging.level
        log_file = self.config.config.logging.file
        console_logging = self.config.config.logging.console

        # Remove default logger
        logger.remove()

        # Add console logger if enabled
        if console_logging:
            logger.add(
                lambda msg: print(msg, end=""),
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
                level=log_level,
                colorize=True
            )

        # Add file logger
        if log_file:
            import os
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            logger.add(
                log_file,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
                level=log_level,
                rotation=self.config.config.logging.max_size,
                retention=self.config.config.logging.backup_count
            )

    async def run(self) -> ScanResult:
        """
        Run the complete test suite

        Returns:
            ScanResult object containing all test results
        """
        # Start progress tracking
        self.progress.start()
        self.progress.update_stat('status', 'Initializing')

        logger.info("=" * 80)
        logger.info("WebTestool - Comprehensive Web Testing Framework")
        logger.info("=" * 80)

        # Initialize scan result
        self.scan_result = ScanResult(
            target_url=self.config.config.target.url,
            config=self.config.config.model_dump()
        )

        try:
            # Phase 1: Web Scanning and Discovery
            logger.info("\n[Phase 1/3] Web Scanning and Discovery")
            logger.info("-" * 80)

            self.progress.update_stat('status', 'Crawling')
            self.progress.update_stat('current_url', self.config.config.target.url)

            if self.config.config.crawler.enabled:
                # Add crawler task
                max_pages = self.config.config.crawler.max_pages
                self.progress.update_stat('pages_total', max_pages)
                self.progress.add_task('crawler', max_pages, 'Crawling website')

                # Start live display
                self.progress.start_live_display()

                crawled_pages, api_endpoints = await self.scanner.scan()
                self.scan_result.crawled_urls = [page.url for page in crawled_pages]

                # Update stats
                self.progress.update_stat('pages_crawled', len(crawled_pages))
                self.progress.update_stat('forms_found', sum(len(p.forms) for p in crawled_pages))
                self.progress.update_stat('api_endpoints', len(api_endpoints))
                self.progress.complete_task('crawler')

                logger.info(f"✓ Discovered {len(crawled_pages)} pages")
                logger.info(f"✓ Discovered {len(api_endpoints)} API endpoints")
            else:
                logger.info("Web scanning disabled, using target URL only")
                crawled_pages = []
                api_endpoints = []

            # Create test context
            context = TestContext(
                target_url=self.config.config.target.url,
                base_url=self.config.config.target.base_url or self.config.config.target.url,
                crawled_pages=crawled_pages,
                api_endpoints=api_endpoints,
                cookies=self.config.config.target.cookies,
                headers=self.config.config.target.headers
            )

            # Phase 2: Module Discovery and Loading
            logger.info("\n[Phase 2/3] Module Discovery and Loading")
            logger.info("-" * 80)

            self.progress.update_stat('status', 'Loading modules')

            self.module_loader.discover_modules()
            enabled_modules = self.module_loader.get_enabled_modules()

            logger.info(f"✓ Loaded {len(enabled_modules)} enabled test modules")
            for module in enabled_modules:
                logger.info(f"  - {module.name} ({module.category.value})")

            # Phase 3: Test Execution
            logger.info("\n[Phase 3/3] Test Execution")
            logger.info("-" * 80)

            # Update test tracking
            self.progress.update_stat('tests_total', len(enabled_modules))
            self.progress.update_stat('status', 'Running tests')
            self.progress.add_task('modules', len(enabled_modules), 'Running test modules')

            if self.config.config.advanced.parallel_execution:
                # Run modules in parallel
                tasks = [self._run_module(module, context) for module in enabled_modules]
                module_results = await asyncio.gather(*tasks, return_exceptions=True)

                # Handle exceptions
                for i, result in enumerate(module_results):
                    if isinstance(result, Exception):
                        logger.error(f"Module {enabled_modules[i].name} failed: {str(result)}")
                        # Create failed module result
                        module_result = ModuleResult(
                            name=enabled_modules[i].name,
                            category=enabled_modules[i].category,
                            status=TestStatus.ERROR
                        )
                        module_result.mark_completed(TestStatus.ERROR)
                        self.scan_result.add_module_result(module_result)
                    else:
                        self.scan_result.add_module_result(result)

                    # Update progress
                    self.progress.update_task('modules', advance=1)
                    self.progress.increment_stat('tests_completed')
                    self.progress.update_live_display()
            else:
                # Run modules sequentially
                for module in enabled_modules:
                    try:
                        module_result = await self._run_module(module, context)
                        self.scan_result.add_module_result(module_result)
                    except Exception as e:
                        logger.error(f"Module {module.name} failed: {str(e)}")
                        module_result = ModuleResult(
                            name=module.name,
                            category=module.category,
                            status=TestStatus.ERROR
                        )
                        module_result.mark_completed(TestStatus.ERROR)
                        self.scan_result.add_module_result(module_result)

                    # Update progress
                    self.progress.update_task('modules', advance=1)
                    self.progress.increment_stat('tests_completed')
                    self.progress.update_live_display()

            # Mark scan as completed
            self.scan_result.mark_completed(TestStatus.PASSED)

            # Complete tasks
            self.progress.complete_task('modules')
            self.progress.update_stat('status', 'Completed')

            # Stop live display before printing summary
            self.progress.stop_live_display()

            # Print summary
            self._print_summary()

            # Display final progress summary
            self.progress.display_final_summary()

            # Stop progress tracking
            self.progress.stop()

            return self.scan_result

        except Exception as e:
            logger.error(f"Scan failed: {str(e)}")
            if self.scan_result:
                self.scan_result.mark_completed(TestStatus.ERROR)

            # Stop progress tracking on error
            self.progress.update_stat('status', 'Failed')
            self.progress.stop_live_display()
            self.progress.stop()

            raise

    async def _run_module(self, module: BaseTestModule, context: TestContext) -> ModuleResult:
        """
        Run a single test module

        Args:
            module: Test module to run
            context: Test context

        Returns:
            ModuleResult object
        """
        logger.info(f"\n Running module: {module.name}")

        # Update progress
        self.progress.update_stat('current_module', module.name)
        self.progress.update_stat('current_test', module.name)
        self.progress.update_live_display()

        # Create module result
        module_result = ModuleResult(
            name=module.name,
            category=module.category,
            status=TestStatus.RUNNING
        )

        try:
            # Setup
            await module.setup()

            # Run tests
            result = await module.run(context)

            # Teardown
            await module.teardown()

            # Update module result
            if result:
                module_result = result

            if module_result.status == TestStatus.RUNNING:
                module_result.mark_completed(TestStatus.PASSED)

            # Update findings in progress tracker
            for finding in module_result.findings:
                severity = finding.severity.value.lower()
                stat_name = f'findings_{severity}'
                self.progress.increment_stat(stat_name, 1)

            self.progress.update_live_display()

            logger.info(f"✓ {module.name} completed: "
                        f"{module_result.summary.get('total_tests', 0)} tests, "
                        f"{module_result.summary.get('total_findings', 0)} findings")

        except Exception as e:
            logger.error(f"✗ {module.name} failed: {str(e)}")
            module_result.mark_completed(TestStatus.ERROR)

        return module_result

    def _print_summary(self) -> None:
        """Print scan summary"""
        logger.info("\n" + "=" * 80)
        logger.info("SCAN SUMMARY")
        logger.info("=" * 80)

        summary = self.scan_result.summary

        logger.info(f"\nTarget URL: {self.scan_result.target_url}")
        logger.info(f"Duration: {summary.get('duration_seconds', 0):.2f} seconds")
        logger.info(f"URLs Crawled: {summary.get('urls_crawled', 0)}")
        logger.info(f"Modules Executed: {summary.get('total_modules', 0)}")
        logger.info(f"Total Tests: {summary.get('total_tests', 0)}")

        logger.info("\nFindings by Severity:")
        logger.info(f"  🔴 Critical: {summary.get('critical_findings', 0)}")
        logger.info(f"  🟠 High:     {summary.get('high_findings', 0)}")
        logger.info(f"  🟡 Medium:   {summary.get('medium_findings', 0)}")
        logger.info(f"  🟢 Low:      {summary.get('low_findings', 0)}")
        logger.info(f"  ℹ️  Info:     {summary.get('info_findings', 0)}")
        logger.info(f"\n  Total Findings: {summary.get('total_findings', 0)}")

        logger.info("\n" + "=" * 80)

        # Print module results
        logger.info("\nModule Results:")
        for module_result in self.scan_result.module_results:
            status_icon = "✓" if module_result.status == TestStatus.PASSED else "✗"
            logger.info(f"  {status_icon} {module_result.name}: "
                        f"{module_result.summary.get('total_tests', 0)} tests, "
                        f"{module_result.summary.get('total_findings', 0)} findings")

    def get_result(self) -> Optional[ScanResult]:
        """
        Get the current scan result

        Returns:
            ScanResult object or None
        """
        return self.scan_result

    async def run_module(self, module_name: str, context: Optional[TestContext] = None) -> ModuleResult:
        """
        Run a specific module by name

        Args:
            module_name: Name of the module to run
            context: Optional test context (will create default if not provided)

        Returns:
            ModuleResult object
        """
        # Get module
        module = self.module_loader.get_module(module_name)

        if not module.enabled:
            logger.warning(f"Module {module_name} is not enabled")

        # Create context if not provided
        if context is None:
            context = TestContext(
                target_url=self.config.config.target.url,
                base_url=self.config.config.target.base_url or self.config.config.target.url
            )

        # Run module
        return await self._run_module(module, context)

    def list_modules(self) -> dict:
        """
        List all available modules

        Returns:
            Dictionary of module information
        """
        return self.module_loader.list_modules()
