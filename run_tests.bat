@echo off
echo ================================================
echo WebTestool - System Test Runner
echo ================================================
echo.

echo [1/2] Running verification tests...
python verify_installation.py
if errorlevel 1 (
    echo.
    echo ERROR: Verification failed!
    echo Please fix installation issues before running tests.
    pause
    exit /b 1
)

echo.
echo [2/2] Running system tests...
python test_system.py
if errorlevel 1 (
    echo.
    echo ERROR: Some system tests failed!
    pause
    exit /b 1
)

echo.
echo ================================================
echo All tests passed successfully!
echo ================================================
echo.
echo System is ready for use.
echo.
echo Try running:
echo    python main.py --url https://example.com --profile quick
echo.
pause
