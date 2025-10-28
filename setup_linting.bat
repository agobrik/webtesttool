@echo off
chcp 65001 >nul
color 0A
cls

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║          WebTestool - Code Linting Setup                          ║
echo ║          Install and configure code quality tools                 ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

echo [1/5] Installing linting tools...
pip install black isort flake8 mypy pylint bandit ruff pre-commit --quiet

if errorlevel 1 (
    echo ❌ Failed to install linting tools
    pause
    exit /b 1
)

echo ✅ Linting tools installed
echo.

echo [2/5] Installing additional flake8 plugins...
pip install flake8-bugbear flake8-comprehensions flake8-simplify --quiet

if errorlevel 1 (
    echo ⚠️  Some flake8 plugins failed to install (non-critical)
) else (
    echo ✅ Flake8 plugins installed
)
echo.

echo [3/5] Installing pre-commit hooks...
pre-commit install

if errorlevel 1 (
    echo ❌ Failed to install pre-commit hooks
) else (
    echo ✅ Pre-commit hooks installed
)
echo.

echo [4/5] Running initial code formatting...
echo.

echo Running Black (formatter)...
black . --line-length=100 --exclude "/(\.git|\.venv|venv|build|dist)/" --quiet 2>nul
if not errorlevel 1 echo ✅ Black formatting complete

echo.
echo Running isort (import sorter)...
isort . --profile=black --line-length=100 --quiet 2>nul
if not errorlevel 1 echo ✅ isort complete

echo.

echo [5/5] Running linters...
echo.

echo Running Flake8...
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
if not errorlevel 1 echo ✅ Flake8 critical checks passed

echo.
echo Running Ruff...
ruff check . --fix --quiet 2>nul
if not errorlevel 1 echo ✅ Ruff checks passed

echo.
echo ════════════════════════════════════════════════════════════════════
echo ✅ Code linting setup complete!
echo ════════════════════════════════════════════════════════════════════
echo.

echo 📖 Available commands:
echo.
echo   black .                     - Format code
echo   isort .                     - Sort imports
echo   flake8 .                    - Check code style
echo   mypy .                      - Type checking
echo   pylint <file>               - Detailed analysis
echo   bandit -r .                 - Security checks
echo   ruff check .                - Fast linting
echo   pre-commit run --all-files  - Run all checks
echo.

echo ℹ️  Pre-commit hooks are now active!
echo    They will run automatically on git commit.
echo.

pause
