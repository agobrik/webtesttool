"""
Progress Tracking for WebTestool
Provides real-time progress bars and statistics display
"""

from typing import Dict, Optional, Callable
from datetime import datetime
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    TaskID
)
from rich.table import Table
from rich.panel import Panel
from loguru import logger


class ProgressTracker:
    """
    Real-time progress tracking with Rich library

    Features:
    - Multiple progress bars
    - Real-time statistics
    - ETA calculation
    - Task completion tracking
    - Beautiful console output

    Example:
        tracker = ProgressTracker()
        tracker.start()

        # Add task
        task_id = tracker.add_task("Crawling pages", total=100)

        # Update progress
        for i in range(100):
            tracker.update_task("Crawling pages", advance=1)

        tracker.stop()
    """

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize progress tracker

        Args:
            console: Rich Console instance (creates new if None)
        """
        self.console = console or Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            expand=False
        )

        self.tasks: Dict[str, TaskID] = {}
        self.stats = {
            'pages_crawled': 0,
            'tests_completed': 0,
            'findings_total': 0,
            'findings_critical': 0,
            'findings_high': 0,
            'findings_medium': 0,
            'findings_low': 0,
            'errors': 0
        }

        self.start_time: Optional[datetime] = None
        self.is_running = False

    def start(self):
        """Start progress tracking"""
        self.progress.start()
        self.start_time = datetime.now()
        self.is_running = True
        logger.debug("Progress tracking started")

    def stop(self):
        """Stop progress tracking"""
        if self.is_running:
            self.progress.stop()
            self.is_running = False
            logger.debug("Progress tracking stopped")

    def add_task(
        self,
        name: str,
        total: int,
        description: Optional[str] = None
    ) -> TaskID:
        """
        Add a new progress task

        Args:
            name: Unique task name
            total: Total number of items to process
            description: Task description (uses name if None)

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
        description: Optional[str] = None
    ):
        """
        Update task progress

        Args:
            name: Task name
            advance: Amount to advance (default: 1)
            description: New description (optional)
        """
        if name in self.tasks:
            task_id = self.tasks[name]

            if description:
                self.progress.update(task_id, advance=advance, description=description)
            else:
                self.progress.update(task_id, advance=advance)

    def complete_task(self, name: str):
        """
        Mark task as completed

        Args:
            name: Task name
        """
        if name in self.tasks:
            task_id = self.tasks[name]
            task = self.progress.tasks[task_id]

            if task.total:
                remaining = task.total - task.completed
                if remaining > 0:
                    self.progress.update(task_id, advance=remaining)

            logger.debug(f"Completed task: {name}")

    def remove_task(self, name: str):
        """
        Remove task from progress

        Args:
            name: Task name
        """
        if name in self.tasks:
            task_id = self.tasks[name]
            self.progress.remove_task(task_id)
            del self.tasks[name]
            logger.debug(f"Removed task: {name}")

    def update_stat(self, stat: str, value: int):
        """
        Update statistics

        Args:
            stat: Statistic name
            value: New value
        """
        if stat in self.stats:
            self.stats[stat] = value

    def increment_stat(self, stat: str, amount: int = 1):
        """
        Increment statistics

        Args:
            stat: Statistic name
            amount: Amount to increment (default: 1)
        """
        if stat in self.stats:
            self.stats[stat] += amount

    def get_stats(self) -> Dict[str, int]:
        """
        Get current statistics

        Returns:
            Dictionary of statistics
        """
        return self.stats.copy()

    def generate_summary_table(self) -> Table:
        """
        Generate summary table

        Returns:
            Rich Table with statistics
        """
        table = Table(title="Scan Statistics", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="green", justify="right", width=15)

        # Calculate elapsed time
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
        else:
            elapsed_str = "N/A"

        # Add rows
        table.add_row("Elapsed Time", elapsed_str)
        table.add_row("Pages Crawled", str(self.stats['pages_crawled']))
        table.add_row("Tests Completed", str(self.stats['tests_completed']))
        table.add_row("", "")  # Separator

        # Findings with colors
        table.add_row(
            "Total Findings",
            f"[yellow]{self.stats['findings_total']}[/yellow]"
        )
        table.add_row(
            "  Critical",
            f"[red bold]{self.stats['findings_critical']}[/red bold]"
        )
        table.add_row(
            "  High",
            f"[red]{self.stats['findings_high']}[/red]"
        )
        table.add_row(
            "  Medium",
            f"[yellow]{self.stats['findings_medium']}[/yellow]"
        )
        table.add_row(
            "  Low",
            f"[green]{self.stats['findings_low']}[/green]"
        )

        if self.stats['errors'] > 0:
            table.add_row("", "")  # Separator
            table.add_row("Errors", f"[red]{self.stats['errors']}[/red]")

        return table

    def display_summary(self):
        """Display summary table"""
        if self.is_running:
            self.progress.stop()

        table = self.generate_summary_table()
        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n")

    def display_header(self, title: str, subtitle: Optional[str] = None):
        """
        Display header panel

        Args:
            title: Main title
            subtitle: Optional subtitle
        """
        if subtitle:
            content = f"[bold cyan]{title}[/bold cyan]\n{subtitle}"
        else:
            content = f"[bold cyan]{title}[/bold cyan]"

        panel = Panel(
            content,
            style="cyan",
            border_style="bright_blue"
        )
        self.console.print(panel)

    def display_message(
        self,
        message: str,
        style: str = "info",
        title: Optional[str] = None
    ):
        """
        Display styled message

        Args:
            message: Message to display
            style: Message style (info, success, warning, error)
            title: Optional title
        """
        styles = {
            'info': ('blue', '💡'),
            'success': ('green', '✅'),
            'warning': ('yellow', '⚠️'),
            'error': ('red', '❌')
        }

        color, icon = styles.get(style, ('blue', 'ℹ️'))

        if title:
            text = f"[{color}]{icon} {title}[/{color}]\n{message}"
        else:
            text = f"[{color}]{icon} {message}[/{color}]"

        self.console.print(text)


# Callback type for progress updates
ProgressCallback = Callable[[str, int], None]


class SimpleProgressTracker:
    """
    Simplified progress tracker without Rich library
    Useful for environments where Rich is not available
    """

    def __init__(self):
        """Initialize simple progress tracker"""
        self.tasks: Dict[str, Dict] = {}
        self.stats: Dict[str, int] = {
            'pages_crawled': 0,
            'tests_completed': 0,
            'findings_total': 0
        }

    def start(self):
        """Start tracking"""
        print("Starting scan...")

    def stop(self):
        """Stop tracking"""
        print("Scan completed!")

    def add_task(self, name: str, total: int, description: Optional[str] = None):
        """Add task"""
        self.tasks[name] = {'total': total, 'completed': 0}
        print(f"Task: {description or name} (0/{total})")

    def update_task(self, name: str, advance: int = 1, description: Optional[str] = None):
        """Update task"""
        if name in self.tasks:
            self.tasks[name]['completed'] += advance
            completed = self.tasks[name]['completed']
            total = self.tasks[name]['total']
            percent = (completed / total * 100) if total > 0 else 0
            print(f"\r{name}: {completed}/{total} ({percent:.1f}%)", end='')

    def complete_task(self, name: str):
        """Complete task"""
        if name in self.tasks:
            print(f"\n✓ {name} completed")

    def update_stat(self, stat: str, value: int):
        """Update statistic"""
        if stat in self.stats:
            self.stats[stat] = value

    def increment_stat(self, stat: str, amount: int = 1):
        """Increment statistic"""
        if stat in self.stats:
            self.stats[stat] += amount

    def display_summary(self):
        """Display summary"""
        print("\n" + "=" * 60)
        print("SCAN SUMMARY")
        print("=" * 60)
        for key, value in self.stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print("=" * 60)

    def display_message(self, message: str, style: str = "info", title: Optional[str] = None):
        """Display message"""
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        icon = icons.get(style, 'ℹ️')
        if title:
            print(f"{icon} {title}")
        print(f"  {message}")


def create_progress_tracker(use_rich: bool = True) -> ProgressTracker:
    """
    Create progress tracker

    Args:
        use_rich: Use Rich library (default: True)

    Returns:
        ProgressTracker or SimpleProgressTracker
    """
    if use_rich:
        try:
            return ProgressTracker()
        except ImportError:
            logger.warning("Rich library not available, using simple tracker")
            return SimpleProgressTracker()
    else:
        return SimpleProgressTracker()
