"""
WebTestool Desktop Application
Modern, user-friendly desktop GUI for WebTestool
"""

import flet as ft
import asyncio
import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core import ConfigManager, TestEngine


class WebTestoolApp:
    '''Main Desktop Application'''
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "WebTestool - Web Testing Framework"
        self.page.window.width = 1400
        self.page.window.height = 900
        self.page.window.min_width = 1200
        self.page.window.min_height = 700
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        
        # State
        self.current_page = "dashboard"
        self.scan_running = False
        self.config_manager = None
        
        # UI Components
        self.content_area = ft.Container()
        self.nav_rail = None
        
        # Initialize
        self.setup_ui()


def main(page: ft.Page):
    '''Main entry point'''
    app = WebTestoolApp(page)


if __name__ == "__main__":
    ft.app(target=main)
