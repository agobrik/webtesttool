"""
Error Handler - Centralized error handling with user-friendly messages
Provides beautiful CLI error display using Rich
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .exceptions import (
    WebTestoolError,
    ConfigurationError,
    NetworkError,
    AuthenticationError,
    ValidationError,
    ModuleError,
    ScanError,
    ReportGenerationError,
    DatabaseError,
    RateLimitError,
    TimeoutError,
    ErrorSeverity
)

console = Console()


class ErrorHandler:
    """
    Centralized error handling
    Converts technical errors into user-friendly messages
    """

    @staticmethod
    def handle_exception(e: Exception, verbose: bool = False):
        """
        Handle exception and display user-friendly message

        Args:
            e: Exception to handle
            verbose: Show detailed information
        """
        if isinstance(e, KeyboardInterrupt):
            ErrorHandler._handle_keyboard_interrupt()
            return

        if isinstance(e, ConfigurationError):
            ErrorHandler._handle_config_error(e, verbose)

        elif isinstance(e, NetworkError):
            ErrorHandler._handle_network_error(e, verbose)

        elif isinstance(e, AuthenticationError):
            ErrorHandler._handle_auth_error(e, verbose)

        elif isinstance(e, ValidationError):
            ErrorHandler._handle_validation_error(e, verbose)

        elif isinstance(e, RateLimitError):
            ErrorHandler._handle_rate_limit_error(e, verbose)

        elif isinstance(e, TimeoutError):
            ErrorHandler._handle_timeout_error(e, verbose)

        elif isinstance(e, ScanError):
            ErrorHandler._handle_scan_error(e, verbose)

        elif isinstance(e, ModuleError):
            ErrorHandler._handle_module_error(e, verbose)

        elif isinstance(e, ReportGenerationError):
            ErrorHandler._handle_report_error(e, verbose)

        elif isinstance(e, DatabaseError):
            ErrorHandler._handle_database_error(e, verbose)

        elif isinstance(e, WebTestoolError):
            ErrorHandler._handle_generic_error(e, verbose)

        else:
            ErrorHandler._handle_unknown_error(e, verbose)

    @staticmethod
    def _handle_keyboard_interrupt():
        """Handle Ctrl+C gracefully"""
        console.print("\n[yellow]⚠️  Scan interrupted by user[/yellow]")
        console.print("[dim]Cleaning up...[/dim]")

    @staticmethod
    def _handle_config_error(e: ConfigurationError, verbose: bool):
        """Handle configuration errors"""
        severity_colors = {
            ErrorSeverity.LOW: "blue",
            ErrorSeverity.MEDIUM: "yellow",
            ErrorSeverity.HIGH: "red",
            ErrorSeverity.CRITICAL: "red"
        }

        color = severity_colors.get(e.severity, "red")

        content = [
            f"[bold {color}]⚙️  Configuration Error[/bold {color}]\n",
            f"[white]{e.message}[/white]\n"
        ]

        # Details
        if e.details:
            content.append("[dim]Details:[/dim]")
            for key, value in e.details.items():
                content.append(f"  • {key}: [cyan]{value}[/cyan]")
            content.append("")

        # Suggestion
        if e.suggestion:
            content.append("[yellow]💡 Suggestion:[/yellow]")
            content.append(f"   {e.suggestion}")

        console.print(Panel(
            "\n".join(content),
            title=f"[{color}]Error[/{color}]",
            border_style=color,
            expand=False
        ))

        if verbose and e.original_error:
            console.print(f"\n[dim]Original error: {e.original_error}[/dim]")

    @staticmethod
    def _handle_network_error(e: NetworkError, verbose: bool):
        """Handle network errors"""
        content = [
            "[bold red]🌐 Network Error[/bold red]\n",
            f"[white]{e.message}[/white]\n"
        ]

        # Details
        if e.details:
            if 'url' in e.details:
                content.append(f"[dim]URL:[/dim] [cyan]{e.details['url']}[/cyan]")
            if 'timeout' in e.details:
                content.append(f"[dim]Timeout:[/dim] {e.details['timeout']}s")
            content.append("")

        # Suggestion
        if e.suggestion:
            content.append("[yellow]💡 Suggestion:[/yellow]")
            content.append(f"   {e.suggestion}")

        console.print(Panel(
            "\n".join(content),
            title="[red]Network Error[/red]",
            border_style="red",
            expand=False
        ))

        if verbose and e.original_error:
            console.print(f"\n[dim]Original error: {e.original_error}[/dim]")

    @staticmethod
    def _handle_auth_error(e: AuthenticationError, verbose: bool):
        """Handle authentication errors"""
        content = [
            "[bold red]🔐 Authentication Failed[/bold red]\n",
            f"[white]{e.message}[/white]\n"
        ]

        # Details
        if e.details:
            content.append("[dim]Details:[/dim]")
            for key, value in e.details.items():
                # Don't show passwords!
                if 'password' in key.lower():
                    value = "***"
                content.append(f"  • {key}: [cyan]{value}[/cyan]")
            content.append("")

        # Suggestion
        if e.suggestion:
            content.append("[yellow]💡 Suggestion:[/yellow]")
            content.append(f"   {e.suggestion}")

        console.print(Panel(
            "\n".join(content),
            title="[red]Authentication Error[/red]",
            border_style="red",
            expand=False
        ))

    @staticmethod
    def _handle_validation_error(e: ValidationError, verbose: bool):
        """Handle validation errors"""
        content = [
            "[bold yellow]⚠️  Validation Error[/bold yellow]\n",
            f"[white]{e.message}[/white]\n"
        ]

        # Details
        if e.details:
            if 'field' in e.details:
                content.append(f"[dim]Field:[/dim] [cyan]{e.details['field']}[/cyan]")
            if 'value' in e.details:
                content.append(f"[dim]Value:[/dim] [cyan]{e.details['value']}[/cyan]")
            content.append("")

        # Suggestion
        if e.suggestion:
            content.append("[yellow]💡 Suggestion:[/yellow]")
            content.append(f"   {e.suggestion}")

        console.print(Panel(
            "\n".join(content),
            title="[yellow]Validation Error[/yellow]",
            border_style="yellow",
            expand=False
        ))

    @staticmethod
    def _handle_rate_limit_error(e: RateLimitError, verbose: bool):
        """Handle rate limit errors"""
        retry_after = e.details.get('retry_after', 60)

        content = [
            "[bold yellow]⏱️  Rate Limit Exceeded[/bold yellow]\n",
            f"[white]{e.message}[/white]\n",
            f"[cyan]Please wait {retry_after} seconds before retrying[/cyan]\n"
        ]

        # Suggestion
        if e.suggestion:
            content.append("[yellow]💡 Tip:[/yellow]")
            content.append(f"   {e.suggestion}")

        console.print(Panel(
            "\n".join(content),
            title="[yellow]Rate Limit[/yellow]",
            border_style="yellow",
            expand=False
        ))

    @staticmethod
    def _handle_timeout_error(e: TimeoutError, verbose: bool):
        """Handle timeout errors"""
        timeout = e.details.get('timeout', 'unknown')

        content = [
            "[bold yellow]⏰ Timeout Error[/bold yellow]\n",
            f"[white]{e.message}[/white]\n",
            f"[dim]Timeout:[/dim] {timeout}s\n"
        ]

        # Suggestion
        if e.suggestion:
            content.append("[yellow]💡 Suggestion:[/yellow]")
            content.append(f"   {e.suggestion}")

        console.print(Panel(
            "\n".join(content),
            title="[yellow]Timeout[/yellow]",
            border_style="yellow",
            expand=False
        ))

    @staticmethod
    def _handle_scan_error(e: ScanError, verbose: bool):
        """Handle scan errors"""
        content = [
            "[bold red]🔍 Scan Error[/bold red]\n",
            f"[white]{e.message}[/white]\n"
        ]

        # Details
        if e.details:
            if 'url' in e.details:
                content.append(f"[dim]URL:[/dim] [cyan]{e.details['url']}[/cyan]")
            content.append("")

        # Suggestion
        if e.suggestion:
            content.append("[yellow]💡 Suggestion:[/yellow]")
            content.append(f"   {e.suggestion}")

        console.print(Panel(
            "\n".join(content),
            title="[red]Scan Error[/red]",
            border_style="red",
            expand=False
        ))

    @staticmethod
    def _handle_module_error(e: ModuleError, verbose: bool):
        """Handle module errors"""
        module_name = e.details.get('module', 'Unknown')

        content = [
            "[bold red]🧪 Module Error[/bold red]\n",
            f"[dim]Module:[/dim] [cyan]{module_name}[/cyan]",
            f"[white]{e.message}[/white]\n"
        ]

        # Suggestion
        if e.suggestion:
            content.append("[yellow]💡 Suggestion:[/yellow]")
            content.append(f"   {e.suggestion}")

        console.print(Panel(
            "\n".join(content),
            title="[red]Module Error[/red]",
            border_style="red",
            expand=False
        ))

    @staticmethod
    def _handle_report_error(e: ReportGenerationError, verbose: bool):
        """Handle report generation errors"""
        report_format = e.details.get('format', 'unknown')

        content = [
            "[bold red]📊 Report Generation Error[/bold red]\n",
            f"[dim]Format:[/dim] [cyan]{report_format}[/cyan]",
            f"[white]{e.message}[/white]\n"
        ]

        # Suggestion
        if e.suggestion:
            content.append("[yellow]💡 Suggestion:[/yellow]")
            content.append(f"   {e.suggestion}")

        console.print(Panel(
            "\n".join(content),
            title="[red]Report Error[/red]",
            border_style="red",
            expand=False
        ))

    @staticmethod
    def _handle_database_error(e: DatabaseError, verbose: bool):
        """Handle database errors"""
        content = [
            "[bold red]💾 Database Error[/bold red]\n",
            f"[white]{e.message}[/white]\n"
        ]

        # Suggestion
        if e.suggestion:
            content.append("[yellow]💡 Suggestion:[/yellow]")
            content.append(f"   {e.suggestion}")

        console.print(Panel(
            "\n".join(content),
            title="[red]Database Error[/red]",
            border_style="red",
            expand=False
        ))

    @staticmethod
    def _handle_generic_error(e: WebTestoolError, verbose: bool):
        """Handle generic WebTestool errors"""
        severity_colors = {
            ErrorSeverity.LOW: "blue",
            ErrorSeverity.MEDIUM: "yellow",
            ErrorSeverity.HIGH: "red",
            ErrorSeverity.CRITICAL: "red"
        }

        color = severity_colors.get(e.severity, "red")

        content = [
            f"[bold {color}]❌ {e.__class__.__name__}[/bold {color}]\n",
            f"[white]{e.message}[/white]\n"
        ]

        # Details
        if e.details:
            content.append("[dim]Details:[/dim]")
            for key, value in e.details.items():
                content.append(f"  • {key}: [cyan]{value}[/cyan]")
            content.append("")

        # Suggestion
        if e.suggestion:
            content.append("[yellow]💡 Suggestion:[/yellow]")
            content.append(f"   {e.suggestion}")

        console.print(Panel(
            "\n".join(content),
            title=f"[{color}]Error[/{color}]",
            border_style=color,
            expand=False
        ))

        if verbose and e.original_error:
            console.print(f"\n[dim]Original error: {e.original_error}[/dim]")

    @staticmethod
    def _handle_unknown_error(e: Exception, verbose: bool):
        """Handle unknown errors"""
        content = [
            "[bold red]❌ Unexpected Error[/bold red]\n",
            f"[white]{str(e)}[/white]\n",
            "[yellow]💡 This might be a bug. Please report it.[/yellow]"
        ]

        console.print(Panel(
            "\n".join(content),
            title="[red]Unexpected Error[/red]",
            border_style="red",
            expand=False
        ))

        if verbose:
            import traceback
            console.print("\n[dim]Traceback:[/dim]")
            console.print(f"[dim]{traceback.format_exc()}[/dim]")

    @staticmethod
    def display_error_summary(errors: list):
        """
        Display summary of multiple errors

        Args:
            errors: List of errors
        """
        if not errors:
            return

        table = Table(title="Error Summary", show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan", width=20)
        table.add_column("Message", style="white", width=50)
        table.add_column("Severity", style="yellow", width=10)

        for error in errors:
            if isinstance(error, WebTestoolError):
                table.add_row(
                    error.__class__.__name__,
                    error.message[:50] + "..." if len(error.message) > 50 else error.message,
                    error.severity.value.upper()
                )
            else:
                table.add_row(
                    error.__class__.__name__,
                    str(error)[:50] + "..." if len(str(error)) > 50 else str(error),
                    "UNKNOWN"
                )

        console.print(table)
