"""
CLI Interface for Login Management
Provides command-line tools for authentication and session management
"""

import asyncio
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from loguru import logger

from core.login_automation import LoginAutomation

console = Console()


@click.group()
def login():
    """Manage authentication and login sessions"""
    pass


@login.command('configure')
@click.option('--url', prompt='Login URL', help='URL of the login page')
@click.option('--username', prompt='Username', help='Username or email')
@click.option('--password', prompt='Password', hide_input=True, help='Password')
@click.option('--auto', is_flag=True, help='Perform automatic login immediately')
@click.option('--interactive', is_flag=True, help='Open browser for manual login')
def configure_login(url, username, password, auto, interactive):
    """
    Configure login credentials

    Examples:
        # Interactive configuration
        python -m cli.login_cli login configure

        # With automatic login
        python -m cli.login_cli login configure --url https://example.com/login --username user --password pass --auto

        # With interactive browser login
        python -m cli.login_cli login configure --interactive
    """
    config = {
        'login_url': url,
        'username': username,
        'password': password,
    }

    # Save config
    config_file = Path('data/login_config.json')
    config_file.parent.mkdir(parents=True, exist_ok=True)

    import json
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    console.print("✅ [green]Login configuration saved[/green]")

    if auto:
        console.print("\n🔄 Performing automatic login...")
        login_automation = LoginAutomation(config)
        success = asyncio.run(login_automation.perform_login(headless=True))

        if success:
            console.print("✅ [green]Login successful! Session saved[/green]")
        else:
            console.print("❌ [red]Login failed. Try --interactive mode[/red]")

    elif interactive:
        console.print("\n🌐 Opening browser for manual login...")
        login_automation = LoginAutomation(config)
        success = asyncio.run(login_automation.interactive_login(headless=False))

        if success:
            console.print("✅ [green]Login successful! Session saved[/green]")
        else:
            console.print("❌ [red]Login failed[/red]")


@login.command('auto')
@click.option('--url', help='Login URL')
@click.option('--username', help='Username or email')
@click.option('--password', help='Password')
@click.option('--headless/--no-headless', default=True, help='Run browser in headless mode')
def automatic_login(url, username, password, headless):
    """
    Perform automatic login

    Examples:
        python -m cli.login_cli login auto --url https://example.com/login --username user --password pass
        python -m cli.login_cli login auto --no-headless  # With visible browser
    """
    # Load config if not provided
    if not all([url, username, password]):
        config_file = Path('data/login_config.json')
        if not config_file.exists():
            console.print("❌ [red]No login configuration found. Run 'configure' first.[/red]")
            return

        import json
        with open(config_file) as f:
            saved_config = json.load(f)

        url = url or saved_config.get('login_url')
        username = username or saved_config.get('username')
        password = password or saved_config.get('password')

    config = {
        'login_url': url,
        'username': username,
        'password': password,
    }

    console.print("🔄 [blue]Logging in...[/blue]")
    login_automation = LoginAutomation(config)
    success = asyncio.run(login_automation.perform_login(headless=headless))

    if success:
        console.print("✅ [green]Login successful! Session saved[/green]")
        console.print("\nYou can now run scans with authenticated access:")
        console.print("  python main.py --url https://example.com --use-session")
    else:
        console.print("❌ [red]Login failed. Try interactive mode:[/red]")
        console.print("  python -m cli.login_cli login interactive")


@login.command('interactive')
@click.option('--url', help='Login URL')
@click.option('--username', help='Username or email')
@click.option('--password', help='Password')
def interactive_login(url, username, password):
    """
    Open browser for manual login

    This is useful when automatic login fails or when dealing with:
    - CAPTCHA
    - 2FA/MFA
    - Complex login flows
    - OAuth providers

    Examples:
        python -m cli.login_cli login interactive
    """
    # Load config if not provided
    if not all([url, username, password]):
        config_file = Path('data/login_config.json')
        if config_file.exists():
            import json
            with open(config_file) as f:
                saved_config = json.load(f)

            url = url or saved_config.get('login_url')
            username = username or saved_config.get('username')
            password = password or saved_config.get('password')

    if not url:
        url = Prompt.ask("Login URL")

    config = {
        'login_url': url,
        'username': username or '',
        'password': password or '',
    }

    console.print("\n🌐 [blue]Opening browser - Please login manually[/blue]")
    console.print("\n" + "="*60)
    console.print("🔐 MANUAL LOGIN MODE")
    console.print("="*60)
    console.print("1. Complete the login process in the browser")
    console.print("2. The session will be saved automatically")
    console.print("="*60 + "\n")

    login_automation = LoginAutomation(config)
    success = asyncio.run(login_automation.interactive_login(headless=False))

    if success:
        console.print("✅ [green]Session saved successfully![/green]")
    else:
        console.print("❌ [red]Failed to save session[/red]")


@login.command('verify')
def verify_session():
    """
    Verify if saved session is still valid

    Examples:
        python -m cli.login_cli login verify
    """
    console.print("🔍 [blue]Verifying session...[/blue]")

    # Find first saved session
    sessions_dir = Path('data/sessions')
    if not sessions_dir.exists():
        console.print("❌ [red]No sessions directory found[/red]")
        return

    session_files = list(sessions_dir.glob('*.json'))
    if not session_files:
        console.print("❌ [red]No saved sessions found[/red]")
        return

    # Use first session (most recent)
    session_file = sorted(session_files, key=lambda x: x.stat().st_mtime, reverse=True)[0]

    import json
    with open(session_file) as f:
        session_data = json.load(f)

    # Create minimal config for verification
    config = {
        'login_url': 'http://example.com',  # Will be overridden
    }

    login_automation = LoginAutomation(config)
    login_automation.session_file = session_file

    valid = asyncio.run(login_automation.verify_session_valid())

    if valid:
        console.print("✅ [green]Session is valid![/green]")
    else:
        console.print("❌ [red]Session expired. Please login again.[/red]")


@login.command('list')
def list_sessions():
    """
    List all saved login sessions

    Examples:
        python -m cli.login_cli login list
    """
    sessions_dir = Path('data/sessions')
    if not sessions_dir.exists():
        console.print("No saved sessions")
        return

    session_files = list(sessions_dir.glob('*.json'))
    if not session_files:
        console.print("No saved sessions")
        return

    table = Table(title="Saved Login Sessions")
    table.add_column("Session Name", style="cyan")
    table.add_column("Last Modified", style="magenta")
    table.add_column("File Size", style="green")

    for session_file in sorted(session_files, key=lambda x: x.stat().st_mtime, reverse=True):
        import datetime
        modified = datetime.datetime.fromtimestamp(session_file.stat().st_mtime)
        size = session_file.stat().st_size

        table.add_row(
            session_file.stem,
            modified.strftime('%Y-%m-%d %H:%M:%S'),
            f"{size:,} bytes"
        )

    console.print(table)
    console.print(f"\n💡 Sessions stored in: {sessions_dir.absolute()}")


@login.command('delete')
@click.argument('session_name', required=False)
@click.option('--all', is_flag=True, help='Delete all sessions')
def delete_session(session_name, all):
    """
    Delete saved login session(s)

    Examples:
        python -m cli.login_cli login delete session_name
        python -m cli.login_cli login delete --all
    """
    sessions_dir = Path('data/sessions')

    if all:
        if not Confirm.ask("❓ Delete all sessions?"):
            console.print("Cancelled")
            return

        deleted = 0
        for session_file in sessions_dir.glob('*.json'):
            session_file.unlink()
            deleted += 1

        console.print(f"✅ [green]Deleted {deleted} session(s)[/green]")
        return

    if not session_name:
        console.print("❌ [red]Please specify session name or use --all[/red]")
        return

    session_file = sessions_dir / f"{session_name}.json"
    if not session_file.exists():
        console.print(f"❌ [red]Session '{session_name}' not found[/red]")
        return

    session_file.unlink()
    console.print(f"✅ [green]Deleted session '{session_name}'[/green]")


@login.command('export-cookies')
@click.argument('output_file', default='cookies.json')
def export_cookies(output_file):
    """
    Export cookies from saved session

    Examples:
        python -m cli.login_cli login export-cookies
        python -m cli.login_cli login export-cookies my_cookies.json
    """
    sessions_dir = Path('data/sessions')
    session_files = list(sessions_dir.glob('*.json'))

    if not session_files:
        console.print("❌ [red]No saved sessions found[/red]")
        return

    # Use most recent session
    session_file = sorted(session_files, key=lambda x: x.stat().st_mtime, reverse=True)[0]

    import json
    with open(session_file) as f:
        session_data = json.load(f)

    cookies = session_data.get('cookies', [])

    output_path = Path(output_file)
    with open(output_path, 'w') as f:
        json.dump(cookies, f, indent=2)

    console.print(f"✅ [green]Exported {len(cookies)} cookies to {output_path}[/green]")


if __name__ == '__main__':
    login()
