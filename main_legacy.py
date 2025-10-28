"""
WebTestool - Main Entry Point
Comprehensive Web Testing Framework
"""

import asyncio
import sys
import io
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

import click
from loguru import logger

from core import ConfigManager, TestEngine
from core.notifier import Notifier
from reporters import ReportGenerator


@click.command()
@click.option('--url', required=True, help='Target URL to scan')
@click.option('--config', default=None, help='Path to custom configuration file')
@click.option('--profile', default='full', type=click.Choice(['full', 'quick', 'security', 'performance']),
              help='Test profile to use')
@click.option('--output', default='reports/', help='Output directory for reports')
@click.option('--tests', default=None, help='Comma-separated list of test modules to run')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def main(url: str, config: str, profile: str, output: str, tests: str, verbose: bool):
    """
    WebTestool - Comprehensive Web Testing Framework

    Examples:
        python main.py --url https://example.com
        python main.py --url https://example.com --profile security
        python main.py --url https://example.com --tests security,performance
        python main.py --url https://example.com --config custom_config.yaml
    """

    click.echo(click.style("\n" + "="*70, fg='cyan', bold=True))
    click.echo(click.style("    WebTestool - Comprehensive Web Testing Framework", fg='cyan', bold=True))
    click.echo(click.style("="*70 + "\n", fg='cyan', bold=True))

    # Load configuration
    config_manager = ConfigManager(config)

    # Override URL
    config_manager.set('target.url', url)

    # Override output directory
    config_manager.set('reporting.output_dir', output)

    # Set logging level
    if verbose:
        config_manager.set('logging.level', 'DEBUG')

    # Handle test profile
    if profile == 'quick':
        # Disable crawler for quick scan
        config_manager.set('crawler.enabled', False)
        config_manager.set('crawler.max_pages', 10)
    elif profile == 'security':
        # Only enable security module
        for module in ['performance', 'seo', 'accessibility']:
            config_manager.set(f'modules.{module}.enabled', False)
    elif profile == 'performance':
        # Only enable performance module
        for module in ['security', 'seo', 'accessibility']:
            config_manager.set(f'modules.{module}.enabled', False)

    # Handle specific tests
    if tests:
        # Disable all modules first
        for module in ['security', 'performance', 'seo', 'accessibility']:
            config_manager.set(f'modules.{module}.enabled', False)

        # Enable specified modules
        for test_module in tests.split(','):
            test_module = test_module.strip()
            config_manager.set(f'modules.{test_module}.enabled', True)
            click.echo(f"Enabled module: {test_module}")

    # Validate configuration
    is_valid, errors = config_manager.validate()
    if not is_valid:
        click.echo(click.style("Configuration validation failed:", fg='red', bold=True))
        for error in errors:
            click.echo(click.style(f"  ✗ {error}", fg='red'))
        sys.exit(1)

    # Create and run engine
    try:
        engine = TestEngine(config_manager)

        # Run scan
        click.echo(click.style(f"\nStarting scan of {url}...\n", fg='green', bold=True))

        scan_result = asyncio.run(engine.run())

        # Generate reports
        click.echo(click.style("\nGenerating reports...", fg='cyan', bold=True))
        report_generator = ReportGenerator(config_manager)
        report_paths = report_generator.generate_reports(scan_result)

        # Send notifications if enabled
        if config_manager.get('notifications.enabled', False):
            try:
                click.echo(click.style("\nSending notifications...", fg='cyan', bold=True))
                notifier = Notifier(config_manager)
                asyncio.run(notifier.send_scan_complete(scan_result))
                click.echo(click.style("✓ Notifications sent successfully", fg='green'))
            except Exception as e:
                click.echo(click.style(f"⚠ Failed to send notifications: {str(e)}", fg='yellow'))
                if verbose:
                    import traceback
                    traceback.print_exc()

        # Display results
        click.echo(click.style("\n" + "=" * 80, fg='green'))
        click.echo(click.style("SCAN COMPLETE", fg='green', bold=True))
        click.echo(click.style("=" * 80 + "\n", fg='green'))

        summary = scan_result.summary

        click.echo(f"Total Findings: {click.style(str(summary.get('total_findings', 0)), fg='yellow', bold=True)}")
        click.echo(f"  Critical: {click.style(str(summary.get('critical_findings', 0)), fg='red', bold=True)}")
        click.echo(f"  High:     {click.style(str(summary.get('high_findings', 0)), fg='red')}")
        click.echo(f"  Medium:   {click.style(str(summary.get('medium_findings', 0)), fg='yellow')}")
        click.echo(f"  Low:      {click.style(str(summary.get('low_findings', 0)), fg='green')}")

        click.echo(f"\nReports generated:")
        for path in report_paths:
            click.echo(f"  📄 {path}")

        # Exit code based on findings
        if summary.get('critical_findings', 0) > 0 or summary.get('high_findings', 0) > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        click.echo(click.style("\n\nScan interrupted by user", fg='yellow'))
        sys.exit(130)
    except Exception as e:
        click.echo(click.style(f"\n\nError: {str(e)}", fg='red', bold=True))
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
