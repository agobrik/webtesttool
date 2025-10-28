@echo off
echo ================================================================================
echo Installing Missing Dependencies
echo ================================================================================
echo.

echo [1/2] Installing missing Python packages...
echo.
pip install beautifulsoup4 pyyaml dnspython

echo.
echo [2/2] Installing Playwright browsers (Chromium)...
echo This may take a few minutes...
echo.
python -m playwright install chromium

echo.
echo ================================================================================
echo Installation Complete!
echo ================================================================================
echo.
echo Running verification...
python verify_installation.py

pause
