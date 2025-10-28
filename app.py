"""
WebTestool Desktop Application
Professional, Fast, and User-Friendly Interface
"""

import flet as ft
import asyncio
import os
import json
import sys
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent))
from core import ConfigManager, TestEngine
from reporters import ReportGenerator
from cli.login_dialog import LoginDialog, SessionManager


class WebTestoolApp:
    """Main Desktop Application - Completely Redesigned"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "WebTestool - Professional Web Testing"
        self.page.window_width = 1400
        self.page.window_height = 900
        self.page.window_min_width = 1200
        self.page.window_min_height = 700
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0

        # State
        self.current_view = "dashboard"
        self.scan_running = False
        self.show_login_form = False  # Authentication form visibility

        # UI
        self.content = ft.Container(expand=True)
        self.setup_ui()

    def setup_ui(self):
        """Setup main UI with navigation"""
        nav = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icons.DASHBOARD,
                    label="Dashboard"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PLAY_CIRCLE_OUTLINE,
                    selected_icon=ft.Icons.PLAY_CIRCLE,
                    label="New Scan"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ARTICLE_OUTLINED,
                    selected_icon=ft.Icons.ARTICLE,
                    label="Reports"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.MONITOR_HEART_OUTLINED,
                    selected_icon=ft.Icons.MONITOR_HEART,
                    label="Health"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Settings"
                ),
            ],
            on_change=self.nav_change,
            bgcolor=ft.Colors.BLUE_GREY_50,
        )

        self.page.add(
            ft.Row([
                nav,
                ft.VerticalDivider(width=1),
                self.content
            ], expand=True, spacing=0)
        )

        self.show_dashboard()

    def nav_change(self, e):
        views = [self.show_dashboard, self.show_scan, self.show_reports,
                 self.show_health, self.show_settings]
        if 0 <= e.control.selected_index < len(views):
            views[e.control.selected_index]()

    def show_dashboard(self):
        """Dashboard with COMPLETE SCAN button"""

        # Get real stats from reports
        reports_dir = Path("reports")
        scan_count = len(list(reports_dir.glob("scan_*"))) if reports_dir.exists() else 0

        stats = ft.Row([
            self.stat_card("Total Scans", str(scan_count), ft.Icons.SCIENCE, ft.Colors.BLUE),
            self.stat_card("Last 24h", "0", ft.Icons.SCHEDULE, ft.Colors.PURPLE),
            self.stat_card("Critical", "0", ft.Icons.ERROR, ft.Colors.RED),
            self.stat_card("Status", "Ready", ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN),
        ], spacing=15)

        self.content.content = ft.Container(
            content=ft.Column([
                ft.Text("WebTestool Dashboard", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Text("Professional Web Security & Performance Testing", size=14, color=ft.Colors.GREY_700),
                ft.Container(height=30),
                stats,
                ft.Container(height=40),

                # MAIN FEATURE: COMPLETE SCAN BUTTON
                ft.Container(
                    content=ft.Column([
                        ft.Text("🚀 Quick Actions", size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(height=15),
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.SECURITY, size=48, color=ft.Colors.BLUE),
                                    ft.Container(height=10),
                                    ft.Text("COMPLETE AUDIT", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Container(height=5),
                                    ft.Text("All tests in one click", size=12, color=ft.Colors.GREY_600),
                                    ft.Text("Security + Performance + SEO", size=11, color=ft.Colors.GREY_500),
                                    ft.Container(height=15),
                                    ft.ElevatedButton(
                                        "START COMPLETE SCAN",
                                        icon=ft.Icons.ROCKET_LAUNCH,
                                        on_click=lambda _: self.quick_complete_scan(),
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.WHITE,
                                            bgcolor=ft.Colors.BLUE,
                                        ),
                                        height=50,
                                        expand=True,
                                    ),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                bgcolor=ft.Colors.BLUE_50,
                                padding=25,
                                border_radius=10,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.TUNE, size=48, color=ft.Colors.GREEN),
                                    ft.Container(height=10),
                                    ft.Text("CUSTOM SCAN", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Container(height=5),
                                    ft.Text("Choose specific tests", size=12, color=ft.Colors.GREY_600),
                                    ft.Text("Advanced configuration", size=11, color=ft.Colors.GREY_500),
                                    ft.Container(height=15),
                                    ft.ElevatedButton(
                                        "CONFIGURE & SCAN",
                                        icon=ft.Icons.SETTINGS,
                                        on_click=lambda _: self.show_scan(),
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.WHITE,
                                            bgcolor=ft.Colors.GREEN,
                                        ),
                                        height=50,
                                        expand=True,
                                    ),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                bgcolor=ft.Colors.GREEN_50,
                                padding=25,
                                border_radius=10,
                                expand=True,
                            ),
                        ], spacing=20),
                    ]),
                    padding=20,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                ),
            ], scroll=ft.ScrollMode.AUTO),
            padding=30,
        )
        self.page.update()

    def quick_complete_scan(self):
        """Quick complete scan - INLINE VERSION (NO OVERLAY - DIRECT CONTENT REPLACEMENT)"""
        print("="*50)
        print("INLINE DIALOG: Replacing page content...")
        print("="*50)

        # Create URL input
        url_input = ft.TextField(
            label="Website URL to Scan",
            hint_text="https://example.com",
            value="",
            width=600,
            autofocus=True,
            text_size=18,
            height=60,
        )

        def start_scan_click(e):
            """Start the complete scan"""
            url = url_input.value.strip()
            if not url:
                url_input.error_text = "⚠️ Please enter a valid URL!"
                self.page.update()
                return

            print(f"✓ Starting complete scan for: {url}")
            # Show progress screen (NOT dashboard)
            self.show_scan_progress(url)
            # Start the scan in background
            self.run_complete_scan(url)

        def cancel_click(e):
            """Cancel - go back to dashboard"""
            print("✗ User cancelled")
            self.show_dashboard()

        # CREATE INLINE DIALOG (replaces page content completely)
        inline_dialog = ft.Container(
            content=ft.Column([
                ft.Container(height=30),

                # Back to Dashboard
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=24,
                        tooltip="Back to Dashboard",
                        on_click=cancel_click,
                    ),
                    ft.Text("Complete Website Audit", size=28, weight=ft.FontWeight.BOLD),
                ]),

                ft.Container(height=20),

                # Main content card
                ft.Container(
                    content=ft.Column([
                        # Icon header
                        ft.Icon(ft.Icons.ROCKET_LAUNCH, color=ft.Colors.BLUE, size=64),
                        ft.Container(height=20),

                        # Title
                        ft.Text("Start Complete Scan", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=10),
                        ft.Text("Run all security, performance, and SEO tests in one go",
                               size=14, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER),

                        ft.Container(height=30),

                        # URL Input
                        ft.Text("Enter Website URL:", size=16, weight=ft.FontWeight.W_500),
                        ft.Container(height=10),
                        url_input,

                        ft.Container(height=30),

                        # Test List
                        ft.Container(
                            content=ft.Column([
                                ft.Text("✓ Tests Included:", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(height=15),
                                ft.Row([ft.Icon(ft.Icons.SECURITY, color=ft.Colors.RED, size=24),
                                       ft.Text("Security Tests (14 tests)", size=14)], spacing=10),
                                ft.Row([ft.Icon(ft.Icons.SPEED, color=ft.Colors.ORANGE, size=24),
                                       ft.Text("Performance Tests (3 tests)", size=14)], spacing=10),
                                ft.Row([ft.Icon(ft.Icons.SEARCH, color=ft.Colors.GREEN, size=24),
                                       ft.Text("SEO Analysis (4 tests)", size=14)], spacing=10),
                                ft.Row([ft.Icon(ft.Icons.ACCESSIBILITY, color=ft.Colors.BLUE, size=24),
                                       ft.Text("Accessibility Tests (WCAG)", size=14)], spacing=10),
                                ft.Row([ft.Icon(ft.Icons.DNS, color=ft.Colors.PURPLE, size=24),
                                       ft.Text("Infrastructure Tests", size=14)], spacing=10),
                            ], spacing=12),
                            bgcolor=ft.Colors.BLUE_50,
                            padding=20,
                            border_radius=10,
                        ),

                        ft.Container(height=20),

                        # Time estimate
                        ft.Row([
                            ft.Icon(ft.Icons.SCHEDULE, color=ft.Colors.ORANGE, size=20),
                            ft.Text("⏱️ Estimated time: 30-90 seconds", size=14, italic=True),
                        ], alignment=ft.MainAxisAlignment.CENTER),

                        ft.Container(height=30),

                        # Action buttons
                        ft.Row([
                            ft.OutlinedButton(
                                "Cancel",
                                icon=ft.Icons.CLOSE,
                                on_click=cancel_click,
                                height=50,
                                expand=1,
                            ),
                            ft.ElevatedButton(
                                "START SCAN",
                                icon=ft.Icons.PLAY_ARROW,
                                on_click=start_scan_click,
                                bgcolor=ft.Colors.BLUE,
                                color=ft.Colors.WHITE,
                                height=50,
                                expand=2,
                            ),
                        ], spacing=15),

                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
                    padding=40,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=15,
                    border=ft.border.all(2, ft.Colors.BLUE_200),
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
                ),

            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True,
        )

        # REPLACE CONTENT DIRECTLY - NO DIALOG/OVERLAY
        print("REPLACING self.content.content with inline dialog...")
        self.content.content = inline_dialog
        self.page.update()
        print("✓ Inline dialog is now VISIBLE (replaced page content)")

    def show_scan_progress(self, url):
        """Show scan progress screen (INLINE - visible to user)"""
        print(f"Showing progress screen for: {url}")

        # Progress screen content
        progress_screen = ft.Container(
            content=ft.Column([
                ft.Container(height=50),

                # Header with back button
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=24,
                        tooltip="Back to Dashboard",
                        on_click=lambda _: self.show_dashboard(),
                    ),
                    ft.Text("Scanning in Progress", size=28, weight=ft.FontWeight.BOLD),
                ]),

                ft.Container(height=30),

                # Main progress card
                ft.Container(
                    content=ft.Column([
                        # Animated spinner
                        ft.ProgressRing(width=80, height=80, color=ft.Colors.BLUE),

                        ft.Container(height=30),

                        # URL being scanned
                        ft.Text("🌐 Scanning Website", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=10),
                        ft.Text(url, size=16, color=ft.Colors.BLUE, text_align=ft.TextAlign.CENTER),

                        ft.Container(height=30),

                        # Status info
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.ROCKET_LAUNCH, color=ft.Colors.BLUE, size=20),
                                    ft.Text("Complete Security Audit Running", size=14, weight=ft.FontWeight.W_500),
                                ], spacing=10),
                                ft.Container(height=15),
                                ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=18),
                                    ft.Text("Security Tests (14 tests)", size=13),
                                ], spacing=10),
                                ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=18),
                                    ft.Text("Performance Tests (3 tests)", size=13),
                                ], spacing=10),
                                ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=18),
                                    ft.Text("SEO Analysis (4 tests)", size=13),
                                ], spacing=10),
                                ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=18),
                                    ft.Text("Accessibility Tests", size=13),
                                ], spacing=10),
                                ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=18),
                                    ft.Text("Infrastructure Tests", size=13),
                                ], spacing=10),
                            ], spacing=8),
                            bgcolor=ft.Colors.GREEN_50,
                            padding=20,
                            border_radius=10,
                        ),

                        ft.Container(height=25),

                        # Time estimate
                        ft.Row([
                            ft.Icon(ft.Icons.SCHEDULE, color=ft.Colors.ORANGE, size=20),
                            ft.Text("⏱️ Estimated time: 30-90 seconds", size=14, italic=True, color=ft.Colors.GREY_700),
                        ], alignment=ft.MainAxisAlignment.CENTER),

                        ft.Container(height=20),

                        ft.Text("💡 Please wait while we analyze the website...",
                               size=13, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),

                        ft.Container(height=25),

                        # Back button
                        ft.ElevatedButton(
                            "Go to Dashboard",
                            icon=ft.Icons.DASHBOARD,
                            on_click=lambda _: self.show_dashboard(),
                            height=45,
                        ),

                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    padding=40,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=15,
                    border=ft.border.all(2, ft.Colors.BLUE_200),
                    shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLUE_GREY_100),
                ),

            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True,
        )

        # Replace page content with progress screen
        self.content.content = progress_screen
        self.page.update()
        print("✓ Progress screen is now visible!")

    def close_test_dialog(self):
        """Close test dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def quick_complete_scan_ORIGINAL(self):
        """ORIGINAL - Quick complete scan dialog"""
        print("DEBUG: quick_complete_scan() called!")  # DEBUG

        url_input = ft.TextField(
            label="Website URL",
            hint_text="https://example.com",
            prefix_icon=ft.Icons.LINK,
            autofocus=True,
            width=500,
        )

        def start_scan(e):
            if not url_input.value:
                return
            dialog.open = False
            self.page.update()
            self.run_complete_scan(url_input.value)

        dialog = ft.AlertDialog(
            title=ft.Text("🚀 Complete Website Audit", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Enter the website URL you want to test:"),
                    ft.Container(height=10),
                    url_input,
                    ft.Container(height=10),
                    ft.Text("This will run ALL tests:", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text("✓ Security Tests (14 tests)", size=11),
                    ft.Text("✓ Performance Tests (3 tests)", size=11),
                    ft.Text("✓ SEO Analysis (4 tests)", size=11),
                    ft.Text("✓ Accessibility Tests (WCAG)", size=11),
                    ft.Text("✓ Infrastructure Tests", size=11),
                    ft.Container(height=5),
                    ft.Text("⏱️ Estimated time: 30-60 seconds", size=11, color=ft.Colors.GREY_600),
                ], tight=True),
                width=500,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.close_dialog(dialog)),
                ft.ElevatedButton(
                    "START SCAN",
                    icon=ft.Icons.PLAY_ARROW,
                    on_click=start_scan,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        print("DEBUG: Setting page dialog...")  # DEBUG
        self.page.dialog = dialog
        print("DEBUG: Opening dialog...")  # DEBUG
        dialog.open = True
        print("DEBUG: Updating page...")  # DEBUG
        self.page.update()
        print("DEBUG: Dialog should be visible now!")  # DEBUG

    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    def run_complete_scan(self, url):
        """Run complete scan in background"""
        progress_dialog = ft.AlertDialog(
            title=ft.Text("🔄 Kapsamlı Tarama Başladı", size=18),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"Taranan Site: {url}", size=12),
                    ft.Container(height=15),
                    ft.ProgressRing(),
                    ft.Container(height=15),
                    ft.Text("TÜM testler çalışıyor...", size=11, color=ft.Colors.GREY_600),
                    ft.Text("Security + Performance + SEO + Accessibility", size=10, color=ft.Colors.GREY_500),
                    ft.Text("Süre: 30-90 saniye", size=10, color=ft.Colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
                width=400,
            ),
            modal=True,
        )

        self.page.dialog = progress_dialog
        progress_dialog.open = True
        self.page.update()

        # Run scan in background thread
        def scan_thread():
            try:
                # Load full scan config
                template_path = Path("config/templates/full.yaml")
                if template_path.exists():
                    config = ConfigManager(str(template_path))
                else:
                    config = ConfigManager()

                # Set URL and scan ALL pages
                config.set('target.url', url)
                config.set('crawler.max_pages', 1000)  # Scan ALL pages
                config.set('crawler.max_depth', 10)

                # Run scan
                engine = TestEngine(config)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(engine.run())
                loop.close()

                # ENSURE reports are generated
                try:
                    report_generator = ReportGenerator(config)
                    report_paths = report_generator.generate_reports(result)
                except Exception as report_error:
                    print(f"Report generation error: {report_error}")
                    report_paths = []

                # Show success
                summary = result.summary
                self.show_scan_complete(url, summary, report_paths)
            except Exception as ex:
                import traceback
                print(f"Scan error: {ex}")
                print(traceback.format_exc())
                self.show_scan_error(str(ex))
            finally:
                progress_dialog.open = False
                self.page.update()

        threading.Thread(target=scan_thread, daemon=True).start()

    def show_scan_complete(self, url, summary, report_paths):
        """Show scan complete screen (INLINE)"""
        print(f"✅ Scan completed for {url}")
        print(f"Findings: {summary}")

        # Completion screen
        completion_screen = ft.Container(
            content=ft.Column([
                ft.Container(height=40),

                # Success icon and title
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=80),
                ft.Container(height=20),
                ft.Text("✅ Scan Complete!", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN, text_align=ft.TextAlign.CENTER),

                ft.Container(height=30),

                # Results card
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"🌐 {url}", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),

                        ft.Container(height=25),

                        # Summary badges
                        ft.Row([
                            self.result_badge("Total", str(summary.get('total_findings', 0)), ft.Colors.BLUE),
                            self.result_badge("Critical", str(summary.get('critical_findings', 0)), ft.Colors.RED),
                            self.result_badge("High", str(summary.get('high_findings', 0)), ft.Colors.ORANGE),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),

                        ft.Container(height=20),

                        ft.Row([
                            self.result_badge("Medium", str(summary.get('medium_findings', 0)), ft.Colors.YELLOW_700),
                            self.result_badge("Low", str(summary.get('low_findings', 0)), ft.Colors.GREEN),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),

                        ft.Container(height=30),

                        # Report info
                        ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN, size=20),
                            ft.Text("📄 Reports generated successfully!", size=14, weight=ft.FontWeight.W_500),
                        ], alignment=ft.MainAxisAlignment.CENTER),

                        ft.Container(height=10),

                        ft.Text("You can view detailed reports in the Reports tab",
                               size=13, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),

                        ft.Container(height=30),

                        # Action buttons
                        ft.Row([
                            ft.ElevatedButton(
                                "View Reports",
                                icon=ft.Icons.ARTICLE,
                                on_click=lambda _: self.show_reports(),
                                bgcolor=ft.Colors.BLUE,
                                color=ft.Colors.WHITE,
                                height=50,
                                expand=True,
                            ),
                            ft.OutlinedButton(
                                "Dashboard",
                                icon=ft.Icons.DASHBOARD,
                                on_click=lambda _: self.show_dashboard(),
                                height=50,
                                expand=True,
                            ),
                        ], spacing=15),

                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=15,
                    border=ft.border.all(2, ft.Colors.GREEN_200),
                    shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.GREEN_100),
                ),

            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True,
        )

        # Replace content with completion screen
        self.content.content = completion_screen
        self.page.update()
        print("✓ Completion screen displayed!")

    def show_scan_error(self, error):
        """Show scan error screen (INLINE)"""
        print(f"❌ Scan error: {error}")

        # Error screen
        error_screen = ft.Container(
            content=ft.Column([
                ft.Container(height=80),

                # Error icon
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED, size=80),
                ft.Container(height=20),
                ft.Text("❌ Scan Failed", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.RED, text_align=ft.TextAlign.CENTER),

                ft.Container(height=30),

                # Error details card
                ft.Container(
                    content=ft.Column([
                        ft.Text("Error Details:", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(height=15),
                        ft.Text(str(error), size=14, color=ft.Colors.GREY_700),

                        ft.Container(height=30),

                        # Action buttons
                        ft.Row([
                            ft.ElevatedButton(
                                "Try Again",
                                icon=ft.Icons.REFRESH,
                                on_click=lambda _: self.quick_complete_scan(),
                                bgcolor=ft.Colors.BLUE,
                                color=ft.Colors.WHITE,
                                height=50,
                                expand=True,
                            ),
                            ft.OutlinedButton(
                                "Dashboard",
                                icon=ft.Icons.DASHBOARD,
                                on_click=lambda _: self.show_dashboard(),
                                height=50,
                                expand=True,
                            ),
                        ], spacing=15),

                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=15,
                    border=ft.border.all(2, ft.Colors.RED_200),
                    shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.RED_100),
                    width=600,
                ),

            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30,
            expand=True,
        )

        # Replace content with error screen
        self.content.content = error_screen
        self.page.update()

    def show_scan(self):
        """Custom scan configuration"""
        url_field = ft.TextField(
            label="Target URL",
            hint_text="https://example.com",
            prefix_icon=ft.Icons.LINK,
            width=600,
        )

        profile = ft.Dropdown(
            label="Tarama Profili (Profile)",
            width=600,
            value="full",
            options=[
                ft.dropdown.Option("quick", "⚡ Hızlı Tarama (Temel Testler - 5 dk)"),
                ft.dropdown.Option("security", "🔒 Güvenlik Taraması (Security Focus - 10 dk)"),
                ft.dropdown.Option("performance", "🚀 Performans Testi (Speed & Load - 8 dk)"),
                ft.dropdown.Option("full", "🎯 TAM TARAMA (Hepsi - 15 dk) - ÖNERİLEN"),
            ],
        )

        progress = ft.ProgressBar(width=600, visible=False)
        status = ft.Text("", color=ft.Colors.BLUE_700, visible=False)
        results = ft.Container(visible=False)

        async def run_scan(e):
            if not url_field.value:
                self.show_snack("Please enter a URL", ft.Colors.RED)
                return

            e.control.disabled = True
            progress.visible = True
            status.visible = True
            status.value = f"Scanning {url_field.value}..."
            self.page.update()

            try:
                template_path = Path(f"config/templates/{profile.value}.yaml")
                if template_path.exists():
                    config = ConfigManager(str(template_path))
                else:
                    config = ConfigManager()

                config.set('target.url', url_field.value)
                config.set('crawler.max_pages', 1000)  # TÜM sayfaları tara
                config.set('crawler.max_depth', 10)

                engine = TestEngine(config)
                result = await engine.run()

                # Generate reports
                report_generator = ReportGenerator(config)
                report_paths = report_generator.generate_reports(result)

                summary = result.summary
                results.content = ft.Container(
                    content=ft.Column([
                        ft.Text("✅ Scan Complete!", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                        ft.Container(height=10),
                        ft.Row([
                            self.result_card("Total", str(summary.get('total_findings', 0)), ft.Colors.BLUE),
                            self.result_card("Critical", str(summary.get('critical_findings', 0)), ft.Colors.RED),
                            self.result_card("High", str(summary.get('high_findings', 0)), ft.Colors.ORANGE),
                        ]),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "View Reports",
                            icon=ft.Icons.ARTICLE,
                            on_click=lambda _: self.show_reports(),
                        ),
                    ]),
                    bgcolor=ft.Colors.GREEN_50,
                    padding=20,
                    border_radius=10,
                )
                results.visible = True
                status.value = "✅ Completed successfully!"
                status.color = ft.Colors.GREEN
                self.show_snack("Scan completed! Reports generated.", ft.Colors.GREEN)
            except Exception as ex:
                status.value = f"❌ Error: {str(ex)}"
                status.color = ft.Colors.RED
                self.show_snack(f"Scan failed: {str(ex)}", ft.Colors.RED)

            progress.visible = False
            e.control.disabled = False
            self.page.update()

        async def start_scan_click(e):
            await run_scan(e)

        start_btn = ft.ElevatedButton(
            "START SCAN",
            icon=ft.Icons.PLAY_ARROW,
            on_click=start_scan_click,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE),
            height=50,
        )

        self.content.content = ft.Container(
            content=ft.Column([
                ft.Text("Custom Scan Configuration", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Text("Configure your scan parameters", size=14, color=ft.Colors.GREY_700),
                ft.Container(height=30),
                url_field,
                ft.Container(height=10),
                profile,
                ft.Container(height=10),
                ft.Text("ℹ️ Tüm sayfalar otomatik taranacak (max 1000 sayfa)", size=12, color=ft.Colors.BLUE_700),
                ft.Container(height=20),
                start_btn,
                ft.Container(height=20),
                progress,
                status,
                results,
            ], scroll=ft.ScrollMode.AUTO),
            padding=30,
        )
        self.page.update()

    def show_reports(self):
        """View scan reports"""
        reports_dir = Path("reports")
        items = ft.Column([], spacing=10)

        if reports_dir.exists():
            dirs = sorted(reports_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
            for d in dirs[:20]:  # Show last 20
                json_file = d / "report.json"
                html_file = d / "report.html"
                if json_file.exists():
                    try:
                        data = json.loads(json_file.read_text())
                        url = data.get('scan_info', {}).get('target_url', 'Unknown')
                        findings = data.get('summary', {}).get('total_findings', 0)
                        critical = data.get('summary', {}).get('critical_findings', 0)
                        date = d.name.replace('scan_', '')

                        items.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ARTICLE, color=ft.Colors.BLUE, size=32),
                                    ft.Column([
                                        ft.Text(url, weight=ft.FontWeight.BOLD, size=14),
                                        ft.Row([
                                            ft.Text(f"🔴 {critical} Critical", size=11, color=ft.Colors.RED),
                                            ft.Text(f"📊 {findings} Total", size=11, color=ft.Colors.GREY_600),
                                            ft.Text(f"📅 {date}", size=11, color=ft.Colors.GREY_500),
                                        ], spacing=15),
                                    ], spacing=5, expand=True),
                                    ft.IconButton(
                                        icon=ft.Icons.OPEN_IN_BROWSER,
                                        tooltip="Open HTML Report",
                                        on_click=lambda _, p=str(html_file): os.system(f'start "" "{p}"'),
                                    ),
                                ]),
                                padding=15,
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                border_radius=5,
                                bgcolor=ft.Colors.WHITE,
                            )
                        )
                    except:
                        pass

        if not items.controls:
            items.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=64, color=ft.Colors.GREY_400),
                        ft.Container(height=15),
                        ft.Text("No reports yet", size=16, color=ft.Colors.GREY_600),
                        ft.Text("Run a scan to generate reports", size=12, color=ft.Colors.GREY_500),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "Start Scan",
                            icon=ft.Icons.PLAY_ARROW,
                            on_click=lambda _: self.show_dashboard(),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            )

        self.content.content = ft.Container(
            content=ft.Column([
                ft.Text("Scan Reports", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Text("View and manage your scan reports", size=14, color=ft.Colors.GREY_700),
                ft.Container(height=20),
                items,
            ], scroll=ft.ScrollMode.AUTO),
            padding=30,
        )
        self.page.update()

    def show_health(self):
        """Health monitoring page - ULTRA SIMPLIFIED"""
        status_text = ft.Text("Kontrol ediliyor...", size=14)
        status_icon = ft.Icon(ft.Icons.REFRESH, color=ft.Colors.GREY, size=48)
        metrics_text = ft.Text("", size=12)

        start_button = ft.ElevatedButton(
            "Health API'yi BAŞLAT",
            icon=ft.Icons.PLAY_ARROW,
            visible=False,
            height=50,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN,
            ),
        )

        refresh_button = ft.OutlinedButton(
            "Yenile / Kontrol Et",
            icon=ft.Icons.REFRESH,
            height=50,
        )

        def check_health():
            """Check health in background"""
            status_text.value = "Kontrol ediliyor..."
            status_icon.name = ft.Icons.REFRESH
            status_icon.color = ft.Colors.GREY
            self.page.update()

            def check_thread():
                try:
                    import requests
                    response = requests.get("http://localhost:8081/health", timeout=2)
                    if response.status_code == 200:
                        data = response.json()

                        # SUCCESS
                        status_text.value = "✅ SİSTEM ÇALIŞIYOR"
                        status_icon.name = ft.Icons.CHECK_CIRCLE
                        status_icon.color = ft.Colors.GREEN

                        checks = data.get('checks', {})
                        healthy_count = sum(1 for v in checks.values() if v.get('status') == 'healthy')
                        metrics_text.value = f"✓ {healthy_count} sistem kontrolü TAMAM"

                        start_button.visible = False
                    else:
                        raise Exception("Error")
                except:
                    # NOT RUNNING
                    status_text.value = "⚠️ Health API Çalışmıyor"
                    status_icon.name = ft.Icons.ERROR_OUTLINE
                    status_icon.color = ft.Colors.ORANGE
                    metrics_text.value = "API'yi başlatmak için butona tıklayın"
                    start_button.visible = True

                self.page.update()

            threading.Thread(target=check_thread, daemon=True).start()

        def start_api_click(e):
            """Start the API"""
            try:
                subprocess.Popen([sys.executable, "api/health.py"],
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
                status_text.value = "🟡 Başlatılıyor... (3 saniye bekleyin)"
                status_icon.name = ft.Icons.HOURGLASS_EMPTY
                status_icon.color = ft.Colors.ORANGE
                start_button.visible = False
                self.page.update()

                # Wait 3 seconds then check
                def wait_and_check():
                    import time
                    time.sleep(3)
                    check_health()

                threading.Thread(target=wait_and_check, daemon=True).start()
            except Exception as ex:
                self.show_snack(f"Hata: {str(ex)}", ft.Colors.RED)

        start_button.on_click = start_api_click
        refresh_button.on_click = lambda _: check_health()

        self.content.content = ft.Container(
            content=ft.Column([
                ft.Text("Sistem Sağlığı (System Health)", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Text("Health monitoring API durumu", size=14, color=ft.Colors.GREY_700),
                ft.Container(height=40),

                # Big status box
                ft.Container(
                    content=ft.Column([
                        status_icon,
                        ft.Container(height=15),
                        status_text,
                        ft.Container(height=10),
                        metrics_text,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.GREY_50,
                    padding=40,
                    border_radius=15,
                    border=ft.border.all(2, ft.Colors.GREY_300),
                ),

                ft.Container(height=30),

                # Buttons
                ft.Row([
                    start_button,
                    refresh_button,
                ], spacing=15),

                ft.Container(height=30),

                # Help text
                ft.Container(
                    content=ft.Column([
                        ft.Text("💡 Health API Nedir?", size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(height=5),
                        ft.Text("• Sistem sağlığını izleyen arka plan servisi", size=12),
                        ft.Text("• Database, cache, disk gibi bileşenleri kontrol eder", size=12),
                        ft.Text("• İsteğe bağlı - tarama için gerekli değil", size=12),
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=10,
                ),
            ], scroll=ft.ScrollMode.AUTO),
            padding=30,
        )

        # Auto-check on load
        check_health()
        self.page.update()

    def show_settings(self):
        """Settings page"""
        theme_switch = ft.Switch(
            label="Dark Mode",
            value=self.page.theme_mode == ft.ThemeMode.DARK,
            on_change=lambda e: self.toggle_theme(e.control.value),
        )

        # Session manager
        session_manager = SessionManager(self.page)
        saved_sessions = session_manager.get_saved_sessions()

        # Login form fields
        login_url_field = ft.TextField(
            label="Login URL",
            hint_text="https://example.com/login",
            prefix_icon=ft.Icons.LINK,
        )

        username_field = ft.TextField(
            label="Username/Email",
            hint_text="user@example.com",
            prefix_icon=ft.Icons.PERSON,
        )

        password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
        )

        status_text = ft.Text("", size=14)
        progress_ring = ft.ProgressRing(visible=False, width=20, height=20)

        def toggle_login_form(e):
            """Toggle login form visibility"""
            self.show_login_form = not self.show_login_form
            self.show_settings()

        def perform_login(e, interactive=False):
            """Perform login"""
            # Validate
            if not login_url_field.value:
                status_text.value = "❌ Login URL is required"
                status_text.color = ft.Colors.RED
                self.page.update()
                return

            if not username_field.value:
                status_text.value = "❌ Username is required"
                status_text.color = ft.Colors.RED
                self.page.update()
                return

            if not password_field.value:
                status_text.value = "❌ Password is required"
                status_text.color = ft.Colors.RED
                self.page.update()
                return

            # Run login in background thread
            def run_async_login():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    from core.login_automation import LoginAutomation

                    config = {
                        'login_url': login_url_field.value,
                        'username': username_field.value,
                        'password': password_field.value,
                    }

                    login_automation = LoginAutomation(config)

                    if interactive:
                        success = loop.run_until_complete(login_automation.interactive_login(headless=False))
                    else:
                        # Show progress
                        progress_ring.visible = True
                        status_text.value = "🔄 Logging in..."
                        status_text.color = ft.Colors.BLUE
                        self.page.update()

                        success = loop.run_until_complete(login_automation.perform_login(headless=True))

                    if success:
                        status_text.value = "✅ Login successful! Session saved"
                        status_text.color = ft.Colors.GREEN
                        self.page.update()
                        asyncio.sleep(1)
                        self.show_login_form = False
                        self.show_settings()
                    else:
                        status_text.value = "❌ Login failed. Try interactive mode."
                        status_text.color = ft.Colors.RED
                        self.page.update()

                except Exception as ex:
                    logger.error(f"Login error: {str(ex)}")
                    status_text.value = f"❌ Error: {str(ex)}"
                    status_text.color = ft.Colors.RED
                    self.page.update()
                finally:
                    progress_ring.visible = False
                    self.page.update()
                    loop.close()

            threading.Thread(target=run_async_login, daemon=True).start()

        def refresh_sessions(e):
            """Refresh the settings page to show updated sessions"""
            self.show_settings()

        self.content.content = ft.Container(
            content=ft.Column([
                ft.Text("Settings", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(height=30),

                # Authentication Section
                ft.Row([
                    ft.Icon(ft.Icons.LOCK, size=24, color=ft.Colors.BLUE),
                    ft.Text("Authentication & Login", size=18, weight=ft.FontWeight.BOLD),
                ], spacing=10),
                ft.Container(height=10),
                ft.Text(
                    "Configure login credentials to scan protected/authenticated websites",
                    size=12,
                    color=ft.Colors.GREY_700
                ),
                ft.Container(height=15),

                # Login buttons
                ft.Row([
                    ft.ElevatedButton(
                        "Hide Login Form" if self.show_login_form else "Configure Login",
                        icon=ft.Icons.EXPAND_LESS if self.show_login_form else ft.Icons.LOGIN,
                        on_click=toggle_login_form,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE,
                        ),
                    ),
                    ft.OutlinedButton(
                        "View Authentication Guide",
                        icon=ft.Icons.HELP_OUTLINE,
                        on_click=lambda _: self.open_file("AUTHENTICATION_GUIDE.md"),
                    ),
                ], spacing=10),

                ft.Container(height=15),

                # Login Form (visible when show_login_form[0] is True)
                ft.Container(
                    content=ft.Column([
                        ft.Text("Login Configuration", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        login_url_field,
                        username_field,
                        password_field,
                        ft.Container(height=15),
                        ft.Row([progress_ring, status_text], spacing=10),
                        ft.Container(height=15),
                        ft.Row([
                            ft.ElevatedButton(
                                "Automatic Login",
                                icon=ft.Icons.AUTO_MODE,
                                on_click=lambda e: perform_login(e, interactive=False),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.GREEN,
                                ),
                            ),
                            ft.ElevatedButton(
                                "Interactive Login",
                                icon=ft.Icons.BROWSER_UPDATED,
                                on_click=lambda e: perform_login(e, interactive=True),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.ORANGE,
                                ),
                            ),
                        ], spacing=10),
                    ]),
                    bgcolor=ft.Colors.BLUE_50,
                    padding=20,
                    border_radius=10,
                    border=ft.border.all(2, ft.Colors.BLUE_200),
                    visible=self.show_login_form,
                ),

                ft.Container(height=20),

                # Saved Sessions
                ft.Row([
                    ft.Text("Saved Login Sessions", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"({len(saved_sessions)})", size=14, color=ft.Colors.GREY_600),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Refresh",
                        on_click=refresh_sessions,
                    ),
                ], spacing=5),
                ft.Container(height=5),

                # Session list or empty state
                session_manager.create_session_manager_ui() if saved_sessions else ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=40, color=ft.Colors.GREY_400),
                        ft.Text("No saved sessions", size=14, color=ft.Colors.GREY_600),
                        ft.Text("Click 'Configure Login' to create a session", size=12, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=30,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                ),

                ft.Container(height=30),
                ft.Divider(),
                ft.Container(height=20),

                # Appearance Section
                ft.Text("Appearance", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                theme_switch,

                ft.Container(height=30),
                ft.Text("System Information", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Text(f"Version: 2.0", size=12),
                ft.Text(f"Python: {sys.version.split()[0]}", size=12),
                ft.Text(f"Working Directory: {os.getcwd()}", size=12),

                ft.Container(height=30),
                ft.Text("Documentation", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Row([
                    ft.ElevatedButton(
                        "User Guide",
                        icon=ft.Icons.BOOK,
                        on_click=lambda _: self.open_file("SISTEM_KULLANIM_REHBERI.md"),
                    ),
                    ft.ElevatedButton(
                        "Authentication Guide",
                        icon=ft.Icons.SECURITY,
                        on_click=lambda _: self.open_file("AUTHENTICATION_GUIDE.md"),
                    ),
                ], spacing=10),
            ], scroll=ft.ScrollMode.AUTO),
            padding=30,
        )
        self.page.update()

    def open_file(self, filename):
        """Open a file with default application"""
        try:
            if sys.platform == 'win32':
                os.system(f'start {filename}')
            elif sys.platform == 'darwin':
                os.system(f'open {filename}')
            else:
                os.system(f'xdg-open {filename}')
        except Exception as e:
            logger.error(f"Error opening file: {str(e)}")

    def on_login_complete(self, login_automation):
        """Callback when login completes"""
        self.show_snack("✅ Login successful! Session saved", ft.Colors.GREEN)
        # Refresh settings to show new session
        self.show_settings()

    def toggle_theme(self, is_dark):
        self.page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        self.page.update()

    def show_snack(self, message, color):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()

    def stat_card(self, title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=32),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=12, color=ft.Colors.GREY_700),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_200),
            expand=True,
        )

    def result_card(self, title, value, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(title, size=12),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            border=ft.border.all(2, color),
            border_radius=10,
            expand=True,
        )

    def result_badge(self, title, value, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(title, size=10),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            padding=10,
            bgcolor=f"{color}15",  # 15% opacity
            border_radius=5,
            expand=True,
        )


def main(page: ft.Page):
    app = WebTestoolApp(page)


if __name__ == "__main__":
    ft.app(target=main)
