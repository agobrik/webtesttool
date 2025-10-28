@echo off
echo ================================================
echo WebTestool Installation Script (Windows)
echo ================================================
echo.

echo [1/4] Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.11 or higher.
    pause
    exit /b 1
)
echo.

echo [2/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo.

echo [3/4] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.

echo [4/4] Installing Playwright browsers...
python -m playwright install chromium firefox
echo.

echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo To activate the environment, run:
echo    venv\Scripts\activate.bat
echo.
echo To run a scan:
echo    python main.py --url https://example.com
echo.
echo See USAGE_GUIDE.md for more information.
echo.
pause
