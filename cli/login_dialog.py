"""
Login Dialog for Desktop Application
Provides UI for authentication configuration and interactive login
"""

import flet as ft
import asyncio
import threading
from pathlib import Path
from typing import Optional, Callable
from loguru import logger

from core.login_automation import LoginAutomation


class LoginDialog:
    """Login configuration and interactive login dialog"""

    def __init__(self, page: ft.Page, on_login_complete: Optional[Callable] = None):
        """
        Initialize Login Dialog

        Args:
            page: Flet page
            on_login_complete: Callback when login completes
        """
        self.page = page
        self.on_login_complete = on_login_complete
        self.dialog = None

        # Form fields
        self.login_url_field = ft.TextField(
            label="Login URL",
            hint_text="https://example.com/login",
            prefix_icon=ft.Icons.LINK,
            expand=True
        )

        self.username_field = ft.TextField(
            label="Username/Email",
            hint_text="user@example.com",
            prefix_icon=ft.Icons.PERSON,
            expand=True
        )

        self.password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            expand=True
        )

        # Advanced options
        self.username_selector_field = ft.TextField(
            label="Username Field Selector (CSS)",
            hint_text='input[name="username"]',
            value='input[name="username"], input[type="email"]',
            expand=True
        )

        self.password_selector_field = ft.TextField(
            label="Password Field Selector (CSS)",
            hint_text='input[name="password"]',
            value='input[name="password"], input[type="password"]',
            expand=True
        )

        self.submit_selector_field = ft.TextField(
            label="Submit Button Selector (CSS)",
            hint_text='button[type="submit"]',
            value='button[type="submit"], button:has-text("Login")',
            expand=True
        )

        self.success_indicator_field = ft.TextField(
            label="Success Indicator (URL or CSS selector)",
            hint_text="/dashboard or .user-menu",
            expand=True
        )

        self.show_advanced = False
        self.status_text = ft.Text("", size=14)
        self.progress_ring = ft.ProgressRing(visible=False)

    def create_dialog(self) -> ft.AlertDialog:
        """Create the login dialog"""

        advanced_section = ft.Column(
            [
                ft.Text("Advanced Options", size=16, weight=ft.FontWeight.BOLD),
                self.username_selector_field,
                self.password_selector_field,
                self.submit_selector_field,
                self.success_indicator_field,
            ],
            visible=False,
            spacing=10
        )

        def toggle_advanced(e):
            advanced_section.visible = not advanced_section.visible
            e.control.text = "Hide Advanced Options" if advanced_section.visible else "Show Advanced Options"
            self.page.update()

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("🔐 Configure Authentication"),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Configure login credentials for authenticated scanning",
                            size=13,
                            color=ft.Colors.GREY_700
                        ),
                        ft.Container(height=10),

                        # Basic fields
                        self.login_url_field,
                        self.username_field,
                        self.password_field,

                        ft.Container(height=10),

                        # Advanced toggle
                        ft.TextButton(
                            "Show Advanced Options",
                            icon=ft.Icons.SETTINGS,
                            on_click=toggle_advanced
                        ),

                        advanced_section,

                        ft.Container(height=10),

                        # Status
                        ft.Row([
                            self.progress_ring,
                            self.status_text,
                        ], spacing=10),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=10,
                ),
                width=600,
                height=500,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.ElevatedButton(
                    "Automatic Login",
                    icon=ft.Icons.AUTO_MODE,
                    on_click=self.perform_automatic_login,
                ),
                ft.ElevatedButton(
                    "Interactive Login",
                    icon=ft.Icons.BROWSER_UPDATED,
                    on_click=self.perform_interactive_login,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        return self.dialog

    def show(self):
        """Show the login dialog"""
        try:
            self.dialog = self.create_dialog()
            self.page.dialog = self.dialog
            self.dialog.open = True
            self.page.update()
        except Exception as e:
            logger.error(f"ERROR in LoginDialog.show(): {str(e)}")
            import traceback
            traceback.print_exc()

    def close_dialog(self, e=None):
        """Close the dialog"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()

    def get_login_config(self) -> dict:
        """Get login configuration from form"""
        return {
            'login_url': self.login_url_field.value,
            'username': self.username_field.value,
            'password': self.password_field.value,
            'username_selector': self.username_selector_field.value,
            'password_selector': self.password_selector_field.value,
            'submit_selector': self.submit_selector_field.value,
            'success_indicator': self.success_indicator_field.value,
        }

    def validate_fields(self) -> bool:
        """Validate required fields"""
        if not self.login_url_field.value:
            self.show_status("❌ Login URL is required", ft.Colors.RED)
            return False

        if not self.username_field.value:
            self.show_status("❌ Username is required", ft.Colors.RED)
            return False

        if not self.password_field.value:
            self.show_status("❌ Password is required", ft.Colors.RED)
            return False

        return True

    def show_status(self, message: str, color=None):
        """Show status message"""
        self.status_text.value = message
        if color:
            self.status_text.color = color
        self.page.update()

    def perform_automatic_login(self, e):
        """Perform automatic login"""
        if not self.validate_fields():
            return

        # Run async login in background thread
        def run_async_login():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._do_automatic_login())
            finally:
                loop.close()

        threading.Thread(target=run_async_login, daemon=True).start()

    async def _do_automatic_login(self):
        """Async automatic login"""
        try:
            self.progress_ring.visible = True
            self.show_status("🔄 Logging in automatically...", ft.Colors.BLUE)

            config = self.get_login_config()
            login_automation = LoginAutomation(config)

            success = await login_automation.perform_login(headless=True)

            if success:
                self.show_status("✅ Login successful! Session saved", ft.Colors.GREEN)
                await asyncio.sleep(2)
                self.close_dialog()

                if self.on_login_complete:
                    self.on_login_complete(login_automation)
            else:
                self.show_status("❌ Login failed. Try interactive mode.", ft.Colors.RED)

        except Exception as ex:
            logger.error(f"Login error: {str(ex)}")
            self.show_status(f"❌ Error: {str(ex)}", ft.Colors.RED)
        finally:
            self.progress_ring.visible = False
            self.page.update()

    def perform_interactive_login(self, e):
        """Perform interactive login"""
        if not self.validate_fields():
            return

        # Run async login in background thread
        def run_async_login():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._do_interactive_login())
            finally:
                loop.close()

        threading.Thread(target=run_async_login, daemon=True).start()

    async def _do_interactive_login(self):
        """Async interactive login"""
        try:
            self.progress_ring.visible = True
            self.show_status("🌐 Opening browser - Please login manually...", ft.Colors.BLUE)

            config = self.get_login_config()
            login_automation = LoginAutomation(config)

            # Close dialog before opening browser
            self.close_dialog()

            success = await login_automation.interactive_login(headless=False)

            if success:
                # Show success message
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Login successful! Session saved"),
                    bgcolor=ft.Colors.GREEN
                )
                self.page.snack_bar.open = True

                if self.on_login_complete:
                    self.on_login_complete(login_automation)
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("❌ Login failed. Please try again."),
                    bgcolor=ft.Colors.RED
                )
                self.page.snack_bar.open = True

        except Exception as ex:
            logger.error(f"Interactive login error: {str(ex)}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ Error: {str(ex)}"),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
        finally:
            self.progress_ring.visible = False
            self.page.update()


class SessionManager:
    """Manage saved login sessions"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.sessions_dir = Path("data/sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def get_saved_sessions(self) -> list:
        """Get list of saved sessions"""
        sessions = []
        for session_file in self.sessions_dir.glob("*.json"):
            sessions.append({
                'name': session_file.stem,
                'file': session_file,
                'modified': session_file.stat().st_mtime
            })
        return sorted(sessions, key=lambda x: x['modified'], reverse=True)

    def create_session_manager_ui(self) -> ft.Column:
        """Create session manager UI"""
        sessions = self.get_saved_sessions()

        if not sessions:
            return ft.Column([
                ft.Text("No saved sessions", size=14, color=ft.Colors.GREY_600),
                ft.Text("Use the Login button to create a session", size=12, color=ft.Colors.GREY_500),
            ])

        session_cards = []
        for session in sessions:
            import datetime
            modified = datetime.datetime.fromtimestamp(session['modified'])

            card = ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=40, color=ft.Colors.BLUE),
                        ft.Column([
                            ft.Text(session['name'], weight=ft.FontWeight.BOLD),
                            ft.Text(f"Last used: {modified.strftime('%Y-%m-%d %H:%M')}", size=12, color=ft.Colors.GREY_600),
                        ], spacing=2, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED,
                            tooltip="Delete session",
                            on_click=lambda e, s=session: self.delete_session(s)
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15,
                ),
            )
            session_cards.append(card)

        return ft.Column([
            ft.Text("Saved Login Sessions", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Column(session_cards, spacing=10),
        ])

    def delete_session(self, session: dict):
        """Delete a session"""
        try:
            session['file'].unlink()
            logger.info(f"Deleted session: {session['name']}")

            # Show snackbar
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Session '{session['name']}' deleted"),
                bgcolor=ft.Colors.ORANGE
            )
            self.page.snack_bar.open = True
            self.page.update()

        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
