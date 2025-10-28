"""
Example: Advanced Scan with Custom Configuration
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import ConfigManager, TestEngine
from reporters import ReportGenerator


async def main():
    # Load custom config
    config = ConfigManager('config/custom_config.yaml' if Path('config/custom_config.yaml').exists() else None)

    # Advanced configuration
    config.set('target.url', 'https://example.com')
    config.set('target.auth.type', 'basic')
    config.set('target.auth.username', 'testuser')
    config.set('target.auth.password', 'testpass')

    # Crawler settings
    config.set('crawler.max_depth', 5)
    config.set('crawler.max_pages', 100)
    config.set('crawler.concurrent_requests', 20)

    # Enable all modules
    for module in ['security', 'performance', 'seo', 'accessibility']:
        config.set(f'modules.{module}.enabled', True)

    # Security module specific settings
    config.set('modules.security.aggressive_mode', True)
    config.set('modules.security.sql_injection.enabled', True)
    config.set('modules.security.xss.enabled', True)
    config.set('modules.security.csrf.enabled', True)

    print("Starting comprehensive scan...")

    engine = TestEngine(config)
    scan_result = await engine.run()

    reporter = ReportGenerator(config)
    reports = reporter.generate_reports(scan_result)

    print(f"\n✓ Scan complete! {len(reports)} reports generated.")


if __name__ == '__main__':
    asyncio.run(main())
