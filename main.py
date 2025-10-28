"""
WebTestool - Main Entry Point
Comprehensive Web Testing Framework
Version 2.0 - Optimized
"""

import asyncio
import sys
import io
from pathlib import Path
from typing import Optional

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
from rich.console import Console

# Core imports
from core import ConfigManager, TestEngine
from core.notifier import Notifier
from core.exceptions import (
    ConfigurationError, ValidationError, NetworkError,
    format_error_message
)
from core.progress import create_progress_tracker
from core.error_handler import ErrorHandler

# Utilities
from utils.sanitizers import sanitize_url
from utils.cache import get_cache
from database import get_db_manager

# Reporters
from reporters import ReportGenerator, generate_pdf_report, generate_excel_report

console = Console()


@click.command()
@click.option('--url', default=None, help='Target URL to scan')
@click.option('--config', default=None, help='Path to custom configuration file')
@click.option('--profile', default='full',
              type=click.Choice(['full', 'quick', 'security', 'performance']),
              help='Test profile to use')
@click.option('--output', default='reports/', help='Output directory for reports')
@click.option('--tests', default=None, help='Comma-separated list of test modules to run')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--interactive', '-i', is_flag=True, help='Interactive configuration wizard')
@click.option('--allow-private-ips', is_flag=True, help='Allow scanning private IP addresses')
@click.option('--cache/--no-cache', default=True, help='Enable/disable caching')
@click.option('--pdf', is_flag=True, help='Generate PDF report')
@click.option('--excel', is_flag=True, help='Generate Excel report')
@click.option('--save-db', is_flag=True, help='Save results to database')
def main(
    url: Optional[str],
    config: Optional[str],
    profile: str,
    output: str,
    tests: Optional[str],
    verbose: bool,
    interactive: bool,
    allow_private_ips: bool,
    cache: bool,
    pdf: bool,
    excel: bool,
    save_db: bool
):
    """
    WebTestool - Comprehensive Web Testing Framework

    Examples:
        # Interactive mode
        python main.py --interactive

        # Quick scan
        python main.py --url https://example.com --profile quick

        # Security audit with PDF report
        python main.py --url https://example.com --profile security --pdf

        # Full scan with all report formats
        python main.py --url https://example.com --pdf --excel --save-db

        # Custom configuration
        python main.py --url https://example.com --config config/templates/ecommerce.yaml

        # Specific modules only
        python main.py --url https://example.com --tests security,performance
    """

    console.print()
    console.print("="*70, style="cyan bold")
    console.print("    WebTestool v2.0 - Comprehensive Web Testing Framework", style="cyan bold")
    console.print("="*70, style="cyan bold")
    console.print()

    try:
        # Interactive mode
        if interactive:
            return run_interactive_mode()

        # URL is required if not in interactive mode
        if not url:
            console.print("[red]Error: URL is required (use --url or --interactive)[/red]")
            console.print("\nTip: Use --help for usage information")
            sys.exit(1)

        # Sanitize URL
        try:
            url = sanitize_url(url, allow_private=allow_private_ips)
            console.print(f"[green]✓[/green] Target URL validated: {url}")
        except ValidationError as e:
            console.print(f"[red]✗ Invalid URL: {e.message}[/red]")
            if e.suggestion:
                console.print(f"[yellow]💡 {e.suggestion}[/yellow]")
            sys.exit(1)

        # Load configuration
        config_manager = load_configuration(config, url, profile, output, tests, verbose, cache)

        # Initialize cache
        if cache:
            cache_manager = get_cache()
            console.print("[green]✓[/green] Cache enabled")

        # Initialize database
        db_manager = None
        if save_db:
            db_manager = get_db_manager()
            console.print("[green]✓[/green] Database initialized")

        # Create progress tracker
        progress = create_progress_tracker()

        # Create and run engine with progress tracking
        engine = TestEngine(config_manager)

        # Run scan with progress
        console.print(f"\n[bold green]Starting scan of {url}...[/bold green]\n")

        progress.start()
        try:
            scan_result = asyncio.run(engine.run())
        finally:
            progress.stop()

        console.print("\n[bold cyan]Generating reports...[/bold cyan]")

        # Generate reports
        report_paths = generate_all_reports(
            scan_result,
            config_manager,
            output_dir=output,
            generate_pdf=pdf,
            generate_excel=excel
        )

        # Save to database
        if save_db and db_manager:
            try:
                db_id = db_manager.save_scan_result(scan_result)
                console.print(f"[green]✓[/green] Results saved to database (ID: {db_id})")
            except Exception as e:
                console.print(f"[yellow]⚠ Failed to save to database: {e}[/yellow]")

        # Send notifications
        send_notifications(config_manager, scan_result, verbose)

        # Display results
        display_results(scan_result, report_paths)

        # Exit based on findings
        summary = scan_result.summary
        if summary.get('critical_findings', 0) > 0 or summary.get('high_findings', 0) > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠ Scan interrupted by user[/yellow]")
        console.print("[cyan]Tip: Results up to this point have been processed.[/cyan]")
        sys.exit(130)

    except (ConfigurationError, ValidationError, NetworkError) as e:
        # Use ErrorHandler for structured error display
        console.print()
        ErrorHandler.handle_exception(e, verbose=verbose)
        sys.exit(1)

    except Exception as e:
        # Use ErrorHandler for all exceptions
        console.print()
        ErrorHandler.handle_exception(e, verbose=verbose)
        sys.exit(1)


def run_interactive_mode():
    """Run interactive configuration wizard"""
    console.print("[bold cyan]Starting interactive configuration wizard...[/bold cyan]\n")

    try:
        from cli.interactive import run_interactive
        config = run_interactive()

        # If user saved config, ask if they want to run scan now
        if '_config_file' in config:
            from rich.prompt import Confirm
            run_now = Confirm.ask("\nRun scan now with this configuration?", default=True)

            if run_now:
                # Run scan with generated config
                config_file = config['_config_file']
                console.print(f"\n[green]Running scan with {config_file}...[/green]\n")

                # Re-invoke main with config file
                from click import Context
                ctx = Context(main)
                ctx.invoke(main, url=config['target']['url'], config=config_file, interactive=False)

    except Exception as e:
        console.print()
        verbose = '--verbose' in sys.argv or '-v' in sys.argv
        ErrorHandler.handle_exception(e, verbose=verbose)
        sys.exit(1)


def load_configuration(
    config_path: Optional[str],
    url: str,
    profile: str,
    output: str,
    tests: Optional[str],
    verbose: bool,
    cache: bool
) -> ConfigManager:
    """Load and configure settings"""

    # If config file specified, load it
    if config_path:
        console.print(f"[cyan]Loading configuration from {config_path}...[/cyan]")
        config_manager = ConfigManager(config_path)
    else:
        # Try to load template based on profile
        template_path = Path(f"config/templates/{profile}.yaml")
        if template_path.exists():
            console.print(f"[cyan]Using {profile} template...[/cyan]")
            config_manager = ConfigManager(str(template_path))
        else:
            config_manager = ConfigManager()

    # Override settings
    config_manager.set('target.url', url)
    config_manager.set('reporting.output_dir', output)

    if verbose:
        config_manager.set('logging.level', 'DEBUG')

    # Cache settings
    if cache:
        config_manager.set('cache.enabled', True)

    # Handle specific tests
    if tests:
        # Disable all modules first
        for module in ['security', 'performance', 'seo', 'accessibility', 'api', 'infrastructure']:
            config_manager.set(f'modules.{module}.enabled', False)

        # Enable specified modules
        for test_module in tests.split(','):
            test_module = test_module.strip()
            config_manager.set(f'modules.{test_module}.enabled', True)
            console.print(f"[green]Enabled module: {test_module}[/green]")

    # Validate configuration
    is_valid, errors = config_manager.validate()
    if not is_valid:
        console.print("[red bold]Configuration validation failed:[/red bold]")
        for error in errors:
            console.print(f"  [red]✗ {error}[/red]")
        raise ConfigurationError(
            "Invalid configuration",
            details={'errors': errors}
        )

    console.print("[green]✓[/green] Configuration validated")

    return config_manager


def generate_all_reports(
    scan_result,
    config_manager: ConfigManager,
    output_dir: str,
    generate_pdf: bool = False,
    generate_excel: bool = False
) -> list:
    """Generate all requested report formats"""

    report_paths = []

    try:
        # Standard HTML/JSON reports
        report_generator = ReportGenerator(config_manager)
        html_paths = report_generator.generate_reports(scan_result)
        report_paths.extend(html_paths)
    except Exception as e:
        console.print(f"[yellow]⚠ HTML/JSON report generation failed: {e}[/yellow]")

    # Convert scan_result to dict for additional reporters
    try:
        scan_data = {
            'target': scan_result.target_url,
            'date': str(scan_result.start_time),
            'duration': str(scan_result.duration),
            'summary': scan_result.summary,
            'vulnerabilities': [
                {
                    'severity': f.severity.value if hasattr(f.severity, 'value') else str(f.severity),
                    'type': f.category.value if hasattr(f.category, 'value') else str(f.category),
                    'title': f.title,
                    'description': f.description,
                    'location': f.url,
                    'remediation': ', '.join([r.description for r in f.recommendations]) if f.recommendations else ''
                }
                for f in scan_result.get_all_findings()
            ],
            'security': {
                'score': scan_result.summary.get('security_score', 0),
                'tests_performed': []
            },
            'performance': {
                'metrics': {}
            }
        }

        # PDF report
        if generate_pdf:
            try:
                pdf_path = generate_pdf_report(scan_data, output_dir=output_dir)
                report_paths.append(pdf_path)
                console.print(f"[green]✓[/green] PDF report generated")
            except Exception as e:
                console.print(f"[yellow]⚠ PDF generation failed: {e}[/yellow]")

        # Excel report
        if generate_excel:
            try:
                excel_path = generate_excel_report(scan_data, output_dir=output_dir)
                report_paths.append(excel_path)
                console.print(f"[green]✓[/green] Excel report generated")
            except Exception as e:
                console.print(f"[yellow]⚠ Excel generation failed: {e}[/yellow]")

    except Exception as e:
        console.print(f"[yellow]⚠ Additional report generation failed: {e}[/yellow]")

    return report_paths


def send_notifications(config_manager: ConfigManager, scan_result, verbose: bool):
    """Send notifications if enabled"""

    if config_manager.get('notifications.enabled', False):
        try:
            console.print("\n[cyan]Sending notifications...[/cyan]")
            notifier = Notifier(config_manager)
            asyncio.run(notifier.send_scan_complete(scan_result))
            console.print("[green]✓ Notifications sent[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠ Failed to send notifications: {e}[/yellow]")
            if verbose:
                import traceback
                traceback.print_exc()


def display_results(scan_result, report_paths: list):
    """Display scan results summary"""

    console.print()
    console.print("=" * 80, style="green")
    console.print("SCAN COMPLETE", style="green bold")
    console.print("=" * 80, style="green")
    console.print()

    summary = scan_result.summary

    console.print(f"Total Findings: [yellow bold]{summary.get('total_findings', 0)}[/yellow bold]")
    console.print(f"  Critical: [red bold]{summary.get('critical_findings', 0)}[/red bold]")
    console.print(f"  High:     [red]{summary.get('high_findings', 0)}[/red]")
    console.print(f"  Medium:   [yellow]{summary.get('medium_findings', 0)}[/yellow]")
    console.print(f"  Low:      [green]{summary.get('low_findings', 0)}[/green]")

    console.print("\nReports generated:")
    for path in report_paths:
        console.print(f"  📄 {path}")

    console.print()


if __name__ == '__main__':
    main()
