# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for WebTestool Desktop Application
Builds a standalone executable with all dependencies
"""

import sys
from pathlib import Path

block_cipher = None

# Get project root
project_root = Path('.').absolute()

# Data files to include
datas = [
    ('config', 'config'),
    ('payloads', 'payloads'),
    ('README.md', '.'),
    ('AUTHENTICATION_GUIDE.md', '.'),
    ('DESKTOP_APP_BUILD.md', '.'),
    ('LICENSE', '.'),
]

# Hidden imports that PyInstaller might miss - ESSENTIAL ONLY
hiddenimports = [
    # Desktop UI
    'flet',
    'flet.core',
    'flet.cli',

    # Browser automation
    'playwright',
    'playwright.sync_api',
    'playwright.async_api',

    # HTTP clients
    'httpx',
    'aiohttp',

    # HTML parsing
    'bs4',
    'lxml',

    # Configuration & validation
    'pydantic',
    'pydantic_core',
    'pydantic_settings',

    # Logging & UI
    'loguru',
    'rich',
    'click',

    # Reporting - minimal
    'reportlab',
    'openpyxl',

    # Security
    'cryptography',

    # Utilities
    'colorama',
    'aiofiles',
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test',
        'tests',
        'pytest',
        'unittest',
        '_pytest',
        'setuptools',
        'pip',
        'wheel',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WebTestool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if Path('assets/icon.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WebTestool',
)

# Platform-specific configurations
if sys.platform == 'darwin':  # macOS
    app = BUNDLE(
        coll,
        name='WebTestool.app',
        icon='assets/icon.icns' if Path('assets/icon.icns').exists() else None,
        bundle_identifier='com.webtestool.app',
        info_plist={
            'CFBundleShortVersionString': '2.0.0',
            'CFBundleVersion': '2.0.0',
            'NSHighResolutionCapable': True,
        },
    )
