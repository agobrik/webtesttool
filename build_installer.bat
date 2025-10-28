@echo off
REM WebTestool Installer Builder
REM Creates Windows installer using Inno Setup

echo ========================================
echo WebTestool Installer Builder
echo ========================================
echo.

REM Check if dist\WebTestool exists
if not exist "dist\WebTestool\WebTestool.exe" (
    echo ERROR: Application not built yet!
    echo Please run build_desktop.bat first
    pause
    exit /b 1
)

REM Check if Inno Setup is installed
set INNO_SETUP="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %INNO_SETUP% (
    echo.
    echo Inno Setup not found!
    echo.
    echo Please install Inno Setup 6 from: https://jrsoftware.org/isdl.php
    echo.
    echo After installation, run this script again.
    echo.
    pause
    exit /b 1
)

echo [1/2] Building installer with Inno Setup...
%INNO_SETUP% installer_windows.iss

if errorlevel 1 (
    echo.
    echo ERROR: Installer build failed!
    pause
    exit /b 1
)

echo.
echo [2/2] Installer created successfully!
echo.
echo ========================================
echo Installer location: installer_output\WebTestool-2.0.0-Setup.exe
echo ========================================
echo.
echo You can now distribute this installer to users.
echo.

pause
