"""Main Report Generator"""

import os
from pathlib import Path
from datetime import datetime
from typing import List
from loguru import logger

from core.models import ScanResult
from core.config import ConfigManager


class ReportGenerator:
    """Main report generator that coordinates different output formats"""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.output_dir = config.config.reporting.output_dir

    def generate_reports(self, scan_result: ScanResult) -> List[str]:
        """
        Generate reports in all enabled formats

        Args:
            scan_result: Scan result to generate reports from

        Returns:
            List of generated report file paths
        """
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Extract site name from URL
        from urllib.parse import urlparse
        parsed_url = urlparse(scan_result.target_url)
        site_name = parsed_url.netloc.replace(':', '-').replace('.', '-')
        if not site_name:
            site_name = "unknown-site"

        # Determine which tests were executed
        executed_modules = []
        if scan_result.module_results:
            # Get unique module categories
            categories = set()
            for module in scan_result.module_results:
                if hasattr(module, 'category'):
                    categories.add(module.category.value if hasattr(module.category, 'value') else str(module.category))
            executed_modules = sorted(list(categories))[:3]  # Max 3 categories

        # Create test name part
        if executed_modules:
            test_name = '-'.join(executed_modules)
        else:
            test_name = "fullscan"

        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Create directory name: site-test-datetime
        scan_dir_name = f"{site_name}-{test_name}-{timestamp}"
        scan_dir = os.path.join(self.output_dir, scan_dir_name)
        os.makedirs(scan_dir, exist_ok=True)

        generated_reports = []
        formats = self.config.config.reporting.formats

        # HTML Report
        if formats.get('html', {}).get('enabled', True):
            from .html_reporter import HTMLReporter
            reporter = HTMLReporter(self.config)
            html_path = os.path.join(scan_dir, "report.html")
            reporter.generate(scan_result, html_path)
            generated_reports.append(html_path)
            logger.info(f"Generated HTML report: {html_path}")

        # JSON Report
        if formats.get('json', {}).get('enabled', True):
            from .json_reporter import JSONReporter
            reporter = JSONReporter(self.config)
            json_path = os.path.join(scan_dir, "report.json")
            reporter.generate(scan_result, json_path)
            generated_reports.append(json_path)
            logger.info(f"Generated JSON report: {json_path}")

        # Summary text file
        summary_path = os.path.join(scan_dir, "summary.txt")
        self._generate_summary(scan_result, summary_path)
        generated_reports.append(summary_path)

        logger.info(f"All reports generated in: {scan_dir}")
        return generated_reports

    def _generate_summary(self, scan_result: ScanResult, output_path: str) -> None:
        """Generate text summary"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SCAN SUMMARY\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Target URL: {scan_result.target_url}\n")
            f.write(f"Scan Date: {scan_result.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {scan_result.duration:.2f} seconds\n\n")

            summary = scan_result.summary
            f.write("Statistics:\n")
            f.write(f"  URLs Crawled: {summary.get('urls_crawled', 0)}\n")
            f.write(f"  Modules Executed: {summary.get('total_modules', 0)}\n")
            f.write(f"  Total Tests: {summary.get('total_tests', 0)}\n\n")

            f.write("Findings by Severity:\n")
            f.write(f"  Critical: {summary.get('critical_findings', 0)}\n")
            f.write(f"  High:     {summary.get('high_findings', 0)}\n")
            f.write(f"  Medium:   {summary.get('medium_findings', 0)}\n")
            f.write(f"  Low:      {summary.get('low_findings', 0)}\n")
            f.write(f"  Info:     {summary.get('info_findings', 0)}\n")
            f.write(f"\n  TOTAL:    {summary.get('total_findings', 0)}\n\n")

            f.write("Module Results:\n")
            for module_result in scan_result.module_results:
                status_icon = "✓" if module_result.status.value == "passed" else "✗"
                f.write(f"  {status_icon} {module_result.name}: "
                       f"{module_result.summary.get('total_findings', 0)} findings\n")

            f.write("\n" + "=" * 80 + "\n")

        logger.info(f"Generated summary: {output_path}")
