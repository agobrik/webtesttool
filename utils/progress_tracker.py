"""
Progress Tracker - Rich CLI progress tracking with live updates
Provides real-time feedback during scanning
"""

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    TaskProgressColumn,
    MofNCompleteColumn
)
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from typing import Dict, Optional, Any
from datetime import datetime
from loguru import logger

console = Console()


class ProgressTracker:
    """
    Rich progress tracking with live updates
    Displays:
    - Progress bars for tasks
    - Live statistics
    - Current status
    - ETA calculation
    """

    def __init__(self, enable_live_display: bool = True):
        """
        Initialize progress tracker

        Args:
            enable_live_display: Enable live dashboard (disable for CI/CD)
        """
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
            expand=True
        )

        self.tasks: Dict[str, int] = {}
        self.stats = {
            # Crawler stats
            'pages_crawled': 0,
            'pages_total': 0,
            'forms_found': 0,
            'api_endpoints': 0,

            # Test stats
            'tests_completed': 0,
            'tests_total': 0,
            'current_module': 'None',

            # Findings
            'findings_critical': 0,
            'findings_high': 0,
            'findings_medium': 0,
            'findings_low': 0,
            'findings_info': 0,

            # Current state
            'current_url': 'None',
            'current_test': 'None',
            'status': 'Initializing'
        }

        self.start_time = None
        self.layout = None
        self.live = None
        self.enable_live_display = enable_live_display

    def start(self):
        """Start progress tracking"""
        self.start_time = datetime.now()
        self.progress.start()
        logger.debug("Progress tracker started")

    def add_task(
        self,
        name: str,
        total: int,
        description: str = None
    ) -> int:
        """
        Add a new task

        Args:
            name: Task name (identifier)
            total: Total steps
            description: Display description

        Returns:
            Task ID
        """
        desc = description or name
        task_id = self.progress.add_task(desc, total=total)
        self.tasks[name] = task_id
        logger.debug(f"Added task: {name} (total: {total})")
        return task_id

    def update_task(
        self,
        name: str,
        advance: int = 1,
        description: str = None,
        total: int = None
    ):
        """
        Update task progress

        Args:
            name: Task name
            advance: Steps to advance
            description: Update description
            total: Update total (if changed)
        """
        if name in self.tasks:
            update_kwargs = {'advance': advance}

            if description:
                update_kwargs['description'] = description

            if total is not None:
                update_kwargs['total'] = total

            self.progress.update(self.tasks[name], **update_kwargs)

    def complete_task(self, name: str):
        """
        Mark task as completed

        Args:
            name: Task name
        """
        if name in self.tasks:
            task = self.progress.tasks[self.tasks[name]]
            remaining = task.total - task.completed
            if remaining > 0:
                self.progress.update(self.tasks[name], advance=remaining)
            logger.debug(f"Completed task: {name}")

    def update_stat(self, stat: str, value: Any):
        """
        Update a statistic

        Args:
            stat: Statistic name
            value: New value
        """
        if stat in self.stats:
            self.stats[stat] = value

    def increment_stat(self, stat: str, amount: int = 1):
        """
        Increment a statistic

        Args:
            stat: Statistic name
            amount: Amount to increment
        """
        if stat in self.stats:
            if isinstance(self.stats[stat], (int, float)):
                self.stats[stat] += amount

    def get_stats_table(self) -> Table:
        """
        Create statistics table

        Returns:
            Rich Table with statistics
        """
        table = Table(
            title="📊 Live Statistics",
            show_header=False,
            border_style="cyan",
            expand=True,
            padding=(0, 1)
        )

        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Value", style="green", justify="right")

        # Crawler stats
        table.add_row("", "")
        table.add_row("[bold]🔍 Crawler[/bold]", "")
        table.add_row(
            "  Pages Crawled",
            f"{self.stats['pages_crawled']}/{self.stats['pages_total']}"
            if self.stats['pages_total'] > 0
            else str(self.stats['pages_crawled'])
        )
        table.add_row("  Forms Found", str(self.stats['forms_found']))
        table.add_row("  API Endpoints", str(self.stats['api_endpoints']))

        # Test stats
        table.add_row("", "")
        table.add_row("[bold]🧪 Tests[/bold]", "")
        table.add_row(
            "  Progress",
            f"{self.stats['tests_completed']}/{self.stats['tests_total']}"
            if self.stats['tests_total'] > 0
            else "0/0"
        )
        table.add_row("  Current Module", self.stats['current_module'][:20])

        # Findings
        total_findings = sum([
            self.stats['findings_critical'],
            self.stats['findings_high'],
            self.stats['findings_medium'],
            self.stats['findings_low'],
            self.stats['findings_info']
        ])

        table.add_row("", "")
        table.add_row("[bold]🔎 Findings[/bold]", "")
        table.add_row("  🔴 Critical", str(self.stats['findings_critical']))
        table.add_row("  🟠 High", str(self.stats['findings_high']))
        table.add_row("  🟡 Medium", str(self.stats['findings_medium']))
        table.add_row("  🟢 Low", str(self.stats['findings_low']))
        table.add_row("  ℹ️  Info", str(self.stats['findings_info']))
        table.add_row("  [bold]Total[/bold]", f"[bold]{total_findings}[/bold]")

        # Time
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            table.add_row("", "")
            table.add_row("[bold]⏱️  Time[/bold]", "")
            table.add_row(
                "  Elapsed",
                f"{int(elapsed//60)}m {int(elapsed%60)}s"
            )

        return table

    def get_current_status(self) -> Panel:
        """
        Create current status panel

        Returns:
            Rich Panel with current status
        """
        # Truncate long URLs
        current_url = self.stats['current_url']
        if len(current_url) > 70:
            current_url = current_url[:67] + "..."

        content = [
            f"[yellow]Status:[/yellow] [white]{self.stats['status']}[/white]",
            f"[yellow]Current URL:[/yellow] [cyan]{current_url}[/cyan]",
            f"[yellow]Current Module:[/yellow] [blue]{self.stats['current_module']}[/blue]"
        ]

        return Panel(
            "\n".join(content),
            title="🎯 Current Status",
            border_style="yellow",
            padding=(0, 1)
        )

    def create_live_display(self) -> Layout:
        """
        Create live display layout

        Returns:
            Rich Layout
        """
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=6)
        )

        # Header
        layout["header"].update(
            Panel(
                "[bold cyan]WebTestool - Live Scan Progress[/bold cyan]",
                style="bold white on blue"
            )
        )

        # Body
        layout["body"].split_row(
            Layout(self.progress, name="progress"),
            Layout(self.get_stats_table(), name="stats", minimum_size=30)
        )

        # Footer
        layout["footer"].update(self.get_current_status())

        return layout

    def start_live_display(self):
        """Start live display"""
        if not self.enable_live_display:
            logger.debug("Live display disabled")
            return

        try:
            self.layout = self.create_live_display()
            self.live = Live(
                self.layout,
                console=console,
                screen=False,
                refresh_per_second=2,
                transient=False
            )
            self.live.start()
            logger.debug("Live display started")
        except Exception as e:
            logger.warning(f"Could not start live display: {e}")
            self.enable_live_display = False

    def update_live_display(self):
        """Update live display"""
        if not self.enable_live_display or not self.layout:
            return

        try:
            self.layout["stats"].update(self.get_stats_table())
            self.layout["footer"].update(self.get_current_status())
        except Exception as e:
            logger.warning(f"Could not update live display: {e}")

    def stop_live_display(self):
        """Stop live display"""
        if self.live:
            try:
                self.live.stop()
                logger.debug("Live display stopped")
            except Exception as e:
                logger.warning(f"Could not stop live display: {e}")

    def display_final_summary(self):
        """Display final summary after completion"""
        if not self.start_time:
            return

        elapsed = (datetime.now() - self.start_time).total_seconds()

        total_findings = sum([
            self.stats['findings_critical'],
            self.stats['findings_high'],
            self.stats['findings_medium'],
            self.stats['findings_low'],
            self.stats['findings_info']
        ])

        # Create summary table
        summary_table = Table(
            title="✅ Scan Completed",
            show_header=True,
            header_style="bold green",
            border_style="green"
        )

        summary_table.add_column("Metric", style="cyan", width=25)
        summary_table.add_column("Value", style="white", justify="right")

        summary_table.add_row("Pages Crawled", str(self.stats['pages_crawled']))
        summary_table.add_row("Forms Found", str(self.stats['forms_found']))
        summary_table.add_row("API Endpoints", str(self.stats['api_endpoints']))
        summary_table.add_row("Tests Executed", str(self.stats['tests_completed']))
        summary_table.add_row("", "")
        summary_table.add_row("[bold]Total Findings[/bold]", f"[bold]{total_findings}[/bold]")
        summary_table.add_row("  🔴 Critical", str(self.stats['findings_critical']))
        summary_table.add_row("  🟠 High", str(self.stats['findings_high']))
        summary_table.add_row("  🟡 Medium", str(self.stats['findings_medium']))
        summary_table.add_row("  🟢 Low", str(self.stats['findings_low']))
        summary_table.add_row("", "")
        summary_table.add_row(
            "[bold]Duration[/bold]",
            f"[bold]{int(elapsed//60)}m {int(elapsed%60)}s[/bold]"
        )

        console.print("\n")
        console.print(summary_table)
        console.print("\n")

    def display_simple_progress(self, message: str, current: int, total: int):
        """
        Display simple progress (for non-live mode)

        Args:
            message: Progress message
            current: Current progress
            total: Total items
        """
        if self.enable_live_display:
            return

        percentage = (current / total * 100) if total > 0 else 0
        console.print(f"[cyan]{message}[/cyan] {current}/{total} ({percentage:.1f}%)")

    def log(self, message: str, style: str = "white"):
        """
        Log a message (compatible with live display)

        Args:
            message: Message to log
            style: Rich style
        """
        if self.enable_live_display and self.live:
            # Temporarily stop live display to print message
            self.stop_live_display()
            console.print(f"[{style}]{message}[/{style}]")
            self.start_live_display()
        else:
            console.print(f"[{style}]{message}[/{style}]")

    def stop(self):
        """Stop progress tracking"""
        try:
            self.stop_live_display()
            self.progress.stop()
            logger.debug("Progress tracker stopped")
        except Exception as e:
            logger.warning(f"Error stopping progress tracker: {e}")

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
