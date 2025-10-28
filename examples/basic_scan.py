"""
Example: Basic Web Scan
Demonstrates how to perform a basic security scan
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import ConfigManager, TestEngine
from reporters import ReportGenerator


async def main():
    """Run a basic scan"""

    # Create configuration
    config = ConfigManager()

    # Set target URL
    target_url = "https://example.com"  # Change to your target
    config.set('target.url', target_url)

    # Configure for quick scan
    config.set('crawler.max_pages', 20)
    config.set('crawler.max_depth', 2)

    # Enable only security and performance modules
    config.set('modules.seo.enabled', False)
    config.set('modules.accessibility.enabled', False)

    print(f"Starting scan of {target_url}...")

    # Create and run engine
    engine = TestEngine(config)
    scan_result = await engine.run()

    # Generate reports
    print("\nGenerating reports...")
    reporter = ReportGenerator(config)
    reports = reporter.generate_reports(scan_result)

    print(f"\nScan complete! Reports generated:")
    for report in reports:
        print(f"  - {report}")

    # Print summary
    summary = scan_result.summary
    print(f"\nFindings Summary:")
    print(f"  Critical: {summary.get('critical_findings', 0)}")
    print(f"  High:     {summary.get('high_findings', 0)}")
    print(f"  Medium:   {summary.get('medium_findings', 0)}")
    print(f"  Low:      {summary.get('low_findings', 0)}")


if __name__ == '__main__':
    asyncio.run(main())
