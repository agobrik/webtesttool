"""
Interactive CLI Mode
User-friendly wizard for WebTestool configuration
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import yaml

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import inquirer
    from inquirer import errors
    INQUIRER_AVAILABLE = True
except ImportError:
    INQUIRER_AVAILABLE = False
    print("⚠️  inquirer not available, falling back to simple mode")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()


class InteractiveCLI:
    """
    Interactive command-line interface wizard

    Features:
    - User-friendly prompts
    - Configuration builder
    - Profile selection
    - Module customization
    - Config file generation
    """

    PROFILES = {
        'quick': {
            'name': 'Quick Scan',
            'description': 'Fast scan (10 pages, all tests, 1-3 minutes)',
            'config': {
                'crawler': {'max_pages': 10, 'max_depth': 2},
                'modules': {'security': True, 'performance': True, 'seo': True}
            }
        },
        'security': {
            'name': 'Security Audit',
            'description': 'Comprehensive security testing (5-15 minutes)',
            'config': {
                'crawler': {'max_pages': 500, 'max_depth': 5},
                'modules': {'security': True, 'performance': False, 'seo': False}
            }
        },
        'performance': {
            'name': 'Performance Test',
            'description': 'Load testing and optimization (3-8 minutes)',
            'config': {
                'crawler': {'max_pages': 100, 'max_depth': 3},
                'modules': {'security': False, 'performance': True, 'seo': False}
            }
        },
        'full': {
            'name': 'Full Scan',
            'description': 'Complete testing (15-45 minutes)',
            'config': {
                'crawler': {'max_pages': 1000, 'max_depth': 10},
                'modules': {'security': True, 'performance': True, 'seo': True, 'accessibility': True}
            }
        },
        'custom': {
            'name': 'Custom Configuration',
            'description': 'Customize all settings',
            'config': {}
        }
    }

    def __init__(self):
        """Initialize interactive CLI"""
        self.config = {}
        self.use_inquirer = INQUIRER_AVAILABLE

    def run(self) -> Dict:
        """
        Run interactive wizard

        Returns:
            Configuration dictionary
        """
        console.print(Panel.fit(
            "[bold cyan]WebTestool Interactive Setup[/bold cyan]\n"
            "Answer a few questions to configure your scan",
            border_style="cyan"
        ))

        # Step 1: Target URL
        self._ask_target_url()

        # Step 2: Profile selection
        self._ask_profile()

        # Step 3: Authentication (if needed)
        self._ask_authentication()

        # Step 4: Advanced options
        if self._ask_advanced():
            self._ask_advanced_options()

        # Step 5: Save configuration
        self._ask_save_config()

        # Step 6: Display summary
        self._display_summary()

        return self.config

    def _ask_target_url(self):
        """Ask for target URL"""
        console.print("\n[bold]1. Target URL[/bold]")

        if self.use_inquirer:
            questions = [
                inquirer.Text(
                    'url',
                    message="Enter target URL (e.g., https://example.com)",
                    validate=lambda _, x: x.startswith('http')
                )
            ]
            answers = inquirer.prompt(questions)
            url = answers['url'] if answers else None
        else:
            url = Prompt.ask(
                "Enter target URL",
                default="https://example.com"
            )

        if not url:
            console.print("[red]❌ URL is required[/red]")
            sys.exit(1)

        self.config['target'] = {'url': url}

    def _ask_profile(self):
        """Ask for scan profile"""
        console.print("\n[bold]2. Scan Profile[/bold]")

        # Display profiles
        table = Table(title="Available Profiles")
        table.add_column("Profile", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Duration", style="yellow")

        durations = {
            'quick': '1-3 min',
            'security': '5-15 min',
            'performance': '3-8 min',
            'full': '15-45 min',
            'custom': 'Variable'
        }

        for key, profile in self.PROFILES.items():
            table.add_row(
                profile['name'],
                profile['description'],
                durations.get(key, 'N/A')
            )

        console.print(table)

        if self.use_inquirer:
            questions = [
                inquirer.List(
                    'profile',
                    message="Select scan profile",
                    choices=[p['name'] for p in self.PROFILES.values()]
                )
            ]
            answers = inquirer.prompt(questions)
            selected_name = answers['profile'] if answers else 'Quick Scan'
        else:
            selected_name = Prompt.ask(
                "Select profile",
                choices=[p['name'] for p in self.PROFILES.values()],
                default="Quick Scan"
            )

        # Find profile key
        profile_key = None
        for key, profile in self.PROFILES.items():
            if profile['name'] == selected_name:
                profile_key = key
                break

        if profile_key and profile_key != 'custom':
            # Apply profile config
            profile_config = self.PROFILES[profile_key]['config']
            self.config.update(profile_config)
        else:
            # Custom profile - ask for modules
            self._ask_custom_modules()

    def _ask_custom_modules(self):
        """Ask for custom module selection"""
        console.print("\n[bold]Custom Module Selection[/bold]")

        modules = {
            'security': 'Security Testing (SQL injection, XSS, etc.)',
            'performance': 'Performance Testing (Load test, speed)',
            'seo': 'SEO Analysis (Meta tags, structure)',
            'accessibility': 'Accessibility (WCAG 2.1)',
            'api': 'API Testing (REST, GraphQL)',
            'functional': 'Functional Testing (Forms, navigation)'
        }

        if self.use_inquirer:
            questions = [
                inquirer.Checkbox(
                    'modules',
                    message="Select modules to enable (Space to select, Enter to confirm)",
                    choices=[(desc, key) for key, desc in modules.items()],
                    default=['security', 'performance']
                )
            ]
            answers = inquirer.prompt(questions)
            selected = answers['modules'] if answers else ['security']
        else:
            console.print("Available modules:")
            for key, desc in modules.items():
                console.print(f"  • {desc}")

            selected_str = Prompt.ask(
                "\nEnter modules (comma-separated)",
                default="security,performance"
            )
            selected = [s.strip() for s in selected_str.split(',')]

        self.config['modules'] = {
            key: {'enabled': key in selected}
            for key in modules.keys()
        }

    def _ask_authentication(self):
        """Ask for authentication"""
        console.print("\n[bold]3. Authentication[/bold]")

        if self.use_inquirer:
            questions = [
                inquirer.Confirm(
                    'needs_auth',
                    message="Does the site require authentication?",
                    default=False
                )
            ]
            answers = inquirer.prompt(questions)
            needs_auth = answers['needs_auth'] if answers else False
        else:
            needs_auth = Confirm.ask(
                "Does the site require authentication?",
                default=False
            )

        if needs_auth:
            self._configure_authentication()

    def _configure_authentication(self):
        """Configure authentication"""
        auth_types = {
            'basic': 'Basic Authentication (username/password)',
            'bearer': 'Bearer Token (JWT)',
            'custom': 'Custom Headers'
        }

        if self.use_inquirer:
            questions = [
                inquirer.List(
                    'auth_type',
                    message="Select authentication type",
                    choices=[(desc, key) for key, desc in auth_types.items()]
                )
            ]
            answers = inquirer.prompt(questions)
            auth_type = answers['auth_type'] if answers else 'basic'
        else:
            console.print("Authentication types:")
            for key, desc in auth_types.items():
                console.print(f"  • {desc}")

            auth_type = Prompt.ask(
                "Select type",
                choices=list(auth_types.keys()),
                default="basic"
            )

        if 'target' not in self.config:
            self.config['target'] = {}

        if auth_type == 'basic':
            username = Prompt.ask("Username")
            password = Prompt.ask("Password", password=True)

            self.config['target']['auth'] = {
                'type': 'basic',
                'username': username,
                'password': f'{{{{ SECRET:target:password }}}}'  # Store securely
            }

            # Store in keyring
            try:
                from utils.secrets_manager import get_secrets_manager
                manager = get_secrets_manager()
                manager.store_credential('target', username, password)
                console.print("[green]✓ Credentials stored securely[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not store securely: {e}[/yellow]")

        elif auth_type == 'bearer':
            token = Prompt.ask("Bearer Token", password=True)

            self.config['target']['auth'] = {
                'type': 'bearer',
                'token': f'{{{{ SECRET:target:token }}}}'
            }

            # Store token
            try:
                from utils.secrets_manager import get_secrets_manager
                manager = get_secrets_manager()
                manager.store_credential('target', 'bearer_token', token)
                console.print("[green]✓ Token stored securely[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not store securely: {e}[/yellow]")

        elif auth_type == 'custom':
            console.print("Enter custom headers (key=value, one per line, empty line to finish):")
            headers = {}
            while True:
                line = Prompt.ask("Header", default="")
                if not line:
                    break

                if '=' in line:
                    key, value = line.split('=', 1)
                    headers[key.strip()] = value.strip()

            self.config['target']['headers'] = headers

    def _ask_advanced(self) -> bool:
        """Ask if user wants advanced options"""
        console.print("\n[bold]4. Advanced Options[/bold]")

        if self.use_inquirer:
            questions = [
                inquirer.Confirm(
                    'advanced',
                    message="Configure advanced options?",
                    default=False
                )
            ]
            answers = inquirer.prompt(questions)
            return answers['advanced'] if answers else False
        else:
            return Confirm.ask(
                "Configure advanced options?",
                default=False
            )

    def _ask_advanced_options(self):
        """Ask for advanced options"""
        # Max pages
        max_pages = Prompt.ask(
            "Maximum pages to crawl",
            default="100"
        )

        # Max depth
        max_depth = Prompt.ask(
            "Maximum crawl depth",
            default="5"
        )

        # Crawl delay
        crawl_delay = Prompt.ask(
            "Delay between requests (seconds)",
            default="0.5"
        )

        if 'crawler' not in self.config:
            self.config['crawler'] = {}

        self.config['crawler'].update({
            'max_pages': int(max_pages),
            'max_depth': int(max_depth),
            'crawl_delay': float(crawl_delay)
        })

    def _ask_save_config(self):
        """Ask to save configuration"""
        console.print("\n[bold]5. Save Configuration[/bold]")

        if self.use_inquirer:
            questions = [
                inquirer.Confirm(
                    'save',
                    message="Save configuration to file?",
                    default=True
                )
            ]
            answers = inquirer.prompt(questions)
            save = answers['save'] if answers else False
        else:
            save = Confirm.ask(
                "Save configuration to file?",
                default=True
            )

        if save:
            # Generate filename
            if 'target' in self.config and 'url' in self.config['target']:
                from urllib.parse import urlparse
                parsed = urlparse(self.config['target']['url'])
                default_name = f"config_{parsed.hostname}.yaml"
            else:
                default_name = "config_custom.yaml"

            filename = Prompt.ask(
                "Configuration filename",
                default=default_name
            )

            # Ensure .yaml extension
            if not filename.endswith('.yaml') and not filename.endswith('.yml'):
                filename += '.yaml'

            # Save config
            config_dir = Path('config')
            config_dir.mkdir(exist_ok=True)

            config_path = config_dir / filename

            try:
                with open(config_path, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)

                console.print(f"[green]✓ Configuration saved to {config_path}[/green]")
                self.config['_config_file'] = str(config_path)

            except Exception as e:
                console.print(f"[red]❌ Failed to save config: {e}[/red]")

    def _display_summary(self):
        """Display configuration summary"""
        console.print("\n" + "=" * 70)
        console.print(Panel.fit(
            "[bold green]Configuration Complete![/bold green]",
            border_style="green"
        ))

        # Summary table
        table = Table(title="Scan Configuration Summary")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        # Target
        if 'target' in self.config:
            table.add_row("Target URL", self.config['target'].get('url', 'N/A'))

            if 'auth' in self.config['target']:
                table.add_row("Authentication", self.config['target']['auth'].get('type', 'N/A'))

        # Crawler
        if 'crawler' in self.config:
            table.add_row("Max Pages", str(self.config['crawler'].get('max_pages', 'N/A')))
            table.add_row("Max Depth", str(self.config['crawler'].get('max_depth', 'N/A')))

        # Modules
        if 'modules' in self.config:
            enabled = [k for k, v in self.config['modules'].items() if v.get('enabled', False)]
            table.add_row("Modules", ', '.join(enabled) if enabled else 'N/A')

        console.print(table)

        # Command
        if '_config_file' in self.config:
            cmd = f"python main.py --config {self.config['_config_file']}"
        else:
            cmd = f"python main.py --url {self.config['target']['url']}"

        console.print("\n[bold]Run scan with:[/bold]")
        console.print(f"[yellow]{cmd}[/yellow]\n")

        console.print("=" * 70)


def run_interactive():
    """Run interactive CLI wizard"""
    try:
        cli = InteractiveCLI()
        config = cli.run()
        return config

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Setup cancelled by user[/yellow]")
        sys.exit(130)

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_interactive()
