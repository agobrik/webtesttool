@echo off
chcp 65001 >nul
color 0A
cls

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║          WebTestool - Run Code Quality Checks                     ║
echo ║          Comprehensive linting and formatting                     ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

set ERROR_COUNT=0

echo [1/6] Running Black (code formatter)...
echo ════════════════════════════════════════════════════════════════════
black --check --diff --color . --line-length=100 --exclude "/(\.git|\.venv|venv|build|dist)/"

if errorlevel 1 (
    echo.
    echo ⚠️  Code formatting issues found!
    echo    Run: black . --line-length=100
    set /a ERROR_COUNT+=1
) else (
    echo ✅ Code is properly formatted
)
echo.
echo.

echo [2/6] Running isort (import sorter)...
echo ════════════════════════════════════════════════════════════════════
isort --check-only --diff --color . --profile=black --line-length=100

if errorlevel 1 (
    echo.
    echo ⚠️  Import sorting issues found!
    echo    Run: isort . --profile=black --line-length=100
    set /a ERROR_COUNT+=1
) else (
    echo ✅ Imports are properly sorted
)
echo.
echo.

echo [3/6] Running Flake8 (linter)...
echo ════════════════════════════════════════════════════════════════════
flake8 . --count --statistics --show-source

if errorlevel 1 (
    echo.
    echo ⚠️  Flake8 issues found!
    set /a ERROR_COUNT+=1
) else (
    echo ✅ No Flake8 issues
)
echo.
echo.

echo [4/6] Running Ruff (fast linter)...
echo ════════════════════════════════════════════════════════════════════
ruff check . --output-format=text

if errorlevel 1 (
    echo.
    echo ⚠️  Ruff issues found!
    echo    Run: ruff check . --fix
    set /a ERROR_COUNT+=1
) else (
    echo ✅ No Ruff issues
)
echo.
echo.

echo [5/6] Running Bandit (security linter)...
echo ════════════════════════════════════════════════════════════════════
bandit -r . -f txt --exclude ./venv,./env,./tests --quiet -ll

if errorlevel 1 (
    echo.
    echo ⚠️  Security issues found!
    set /a ERROR_COUNT+=1
) else (
    echo ✅ No security issues
)
echo.
echo.

echo [6/6] Running MyPy (type checker)...
echo ════════════════════════════════════════════════════════════════════
mypy . --ignore-missing-imports --check-untyped-defs --exclude "/(tests|venv|env)/"

if errorlevel 1 (
    echo.
    echo ⚠️  Type checking issues found!
    set /a ERROR_COUNT+=1
) else (
    echo ✅ Type checking passed
)
echo.
echo.

echo ════════════════════════════════════════════════════════════════════
echo                        SUMMARY
echo ════════════════════════════════════════════════════════════════════
echo.

if %ERROR_COUNT%==0 (
    echo ✅ All checks passed!
    echo    Your code meets quality standards.
) else (
    echo ⚠️  Found issues in %ERROR_COUNT% check(s)
    echo.
    echo 📝 Quick fixes:
    echo    • Format code:      black . --line-length=100
    echo    • Sort imports:     isort . --profile=black --line-length=100
    echo    • Auto-fix linting: ruff check . --fix
    echo.
)

echo.
pause
