@echo off
REM WebTestool Desktop App Builder for Windows
REM Builds standalone executable using PyInstaller

echo ========================================
echo WebTestool Desktop App Builder
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

echo [1/5] Checking/Installing PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
) else (
    echo PyInstaller already installed
)

echo.
echo [2/5] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "dist\WebTestool" rmdir /s /q "dist\WebTestool"

echo.
echo [3/5] Building executable with PyInstaller...
pyinstaller webtestool.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [4/5] Creating data directories...
if not exist "dist\WebTestool\data" mkdir "dist\WebTestool\data"
if not exist "dist\WebTestool\logs" mkdir "dist\WebTestool\logs"
if not exist "dist\WebTestool\reports" mkdir "dist\WebTestool\reports"

echo.
echo [5/5] Build completed successfully!
echo.
echo ========================================
echo Executable location: dist\WebTestool\WebTestool.exe
echo ========================================
echo.
echo You can now:
echo 1. Run: dist\WebTestool\WebTestool.exe
echo 2. Create installer: build_installer.bat
echo 3. Zip for distribution: compress the dist\WebTestool folder
echo.

pause
