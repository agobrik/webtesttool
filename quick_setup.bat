@echo off
echo ================================================================================
echo WebTestool - Quick Setup Script
echo ================================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)

echo.
echo [2/4] Installing Playwright browsers...
python -m playwright install chromium
if errorlevel 1 (
    echo [WARNING] Failed to install Playwright browsers
)

echo.
echo [3/4] Creating required directories...
if not exist "logs" mkdir logs
if not exist "reports" mkdir reports
if not exist "data" mkdir data
if not exist ".cache" mkdir .cache

echo.
echo [4/4] Running verification...
python verify_installation.py

echo.
echo ================================================================================
echo Setup Complete!
echo ================================================================================
echo.
echo Quick Start:
echo   python main.py --url https://example.com --profile quick
echo.
echo For help:
echo   python main.py --help
echo.

pause
