# Code Quality Guide

This document describes the code quality tools and practices used in WebTestool.

## Quick Start

### Setup (First Time)

```bash
# Install all linting tools and setup pre-commit hooks
setup_linting.bat
```

### Run Checks

```bash
# Run all quality checks
run_linting.bat

# Or run individual tools
black .                      # Format code
isort .                      # Sort imports
flake8 .                     # Lint code
mypy .                       # Type check
bandit -r .                  # Security check
ruff check .                 # Fast lint
pre-commit run --all-files   # Run all pre-commit hooks
```

---

## Tools

### 1. Black - Code Formatter

**Purpose:** Automatic code formatting for consistent style

**Configuration:** `pyproject.toml` → `[tool.black]`

**Usage:**
```bash
# Check formatting
black --check .

# Format code
black .

# Format specific file
black path/to/file.py
```

**Settings:**
- Line length: 100 characters
- Target Python: 3.10+

---

### 2. isort - Import Sorter

**Purpose:** Sort and organize imports

**Configuration:** `pyproject.toml` → `[tool.isort]`

**Usage:**
```bash
# Check import order
isort --check-only .

# Sort imports
isort .

# Sort specific file
isort path/to/file.py
```

**Import Order:**
1. Future imports
2. Standard library
3. Third-party packages
4. First-party (our modules)
5. Local folder imports

---

### 3. Flake8 - Linter

**Purpose:** Check code style and find errors

**Configuration:** `.flake8`

**Usage:**
```bash
# Lint all files
flake8 .

# Lint specific file
flake8 path/to/file.py

# Show statistics
flake8 . --statistics --count
```

**Plugins:**
- `flake8-bugbear` - Find likely bugs
- `flake8-comprehensions` - Better comprehensions
- `flake8-simplify` - Simplify code

**Key Rules:**
- Max line length: 100
- Max complexity: 15
- Docstring convention: Google style

---

### 4. Ruff - Fast Linter

**Purpose:** Extremely fast Python linter (Rust-based)

**Configuration:** `pyproject.toml` → `[tool.ruff]`

**Usage:**
```bash
# Check code
ruff check .

# Auto-fix issues
ruff check . --fix

# Check specific file
ruff check path/to/file.py
```

**Advantages:**
- 10-100x faster than Flake8
- Auto-fixes many issues
- Replaces multiple tools

---

### 5. MyPy - Type Checker

**Purpose:** Static type checking

**Configuration:** `pyproject.toml` → `[tool.mypy]`

**Usage:**
```bash
# Type check all files
mypy .

# Type check specific file
mypy path/to/file.py

# Strict mode
mypy . --strict
```

**Type Hints Example:**
```python
def calculate_score(findings: List[Finding], weights: Dict[str, float]) -> float:
    """Calculate security score with type hints"""
    total: float = 0.0
    for finding in findings:
        total += weights.get(finding.severity, 1.0)
    return total
```

---

### 6. Pylint - Code Analysis

**Purpose:** Detailed code analysis and suggestions

**Configuration:** `pyproject.toml` → `[tool.pylint]`

**Usage:**
```bash
# Analyze code
pylint core/ modules/ utils/

# Analyze specific file
pylint path/to/file.py

# Generate report
pylint core/ --output-format=text > pylint_report.txt
```

**Features:**
- Code smell detection
- Refactoring suggestions
- Best practices enforcement

---

### 7. Bandit - Security Linter

**Purpose:** Find security issues

**Configuration:** `pyproject.toml` → `[tool.bandit]`

**Usage:**
```bash
# Security scan
bandit -r .

# Medium/High severity only
bandit -r . -ll

# Generate report
bandit -r . -f json -o bandit_report.json
```

**Checks:**
- Hardcoded passwords
- SQL injection risks
- Shell injection
- Weak cryptography
- Insecure deserialization

---

### 8. Pre-commit - Git Hooks

**Purpose:** Run checks automatically before commit

**Configuration:** `.pre-commit-config.yaml`

**Setup:**
```bash
# Install pre-commit
pip install pre-commit

# Setup git hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**Hooks Run on Commit:**
1. Trailing whitespace removal
2. End of file fixer
3. YAML/JSON validation
4. Black formatting
5. isort import sorting
6. Flake8 linting
7. Ruff linting
8. MyPy type checking
9. Bandit security checking

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run Black
        run: black --check .

      - name: Run Ruff
        run: ruff check .

      - name: Run MyPy
        run: mypy .

      - name: Run Bandit
        run: bandit -r .

      - name: Run Tests
        run: pytest --cov
```

---

## Best Practices

### 1. Before Committing

Always run quality checks before committing:

```bash
# Quick check
run_linting.bat

# Or use pre-commit
pre-commit run --all-files
```

### 2. Code Formatting

Let Black handle all formatting:
- Don't manually format code
- Run Black before committing
- Disable editor auto-formatting

### 3. Import Organization

Use isort for imports:
```python
# Good
from typing import List, Dict
import os
import sys

import httpx
from playwright.async_api import async_playwright

from core.models import ScanResult
from utils.cache import CacheManager

from .helpers import validate_url
```

### 4. Type Hints

Add type hints to all functions:
```python
# Good
def process_findings(findings: List[Finding]) -> Dict[str, int]:
    return {'total': len(findings)}

# Bad
def process_findings(findings):
    return {'total': len(findings)}
```

### 5. Docstrings

Use Google-style docstrings:
```python
def scan_website(url: str, config: Dict[str, Any]) -> ScanResult:
    """
    Scan website for security vulnerabilities.

    Args:
        url: Target website URL
        config: Scan configuration

    Returns:
        ScanResult with findings

    Raises:
        ValidationError: If URL is invalid
        NetworkError: If cannot connect
    """
    pass
```

### 6. Security

Follow Bandit recommendations:
- No hardcoded secrets
- Use parameterized queries
- Validate all inputs
- Use secure random
- Check SSL certificates

---

## Configuration Files

### pyproject.toml
Main configuration file for:
- Black
- isort
- MyPy
- Pylint
- Bandit
- Ruff
- Pytest
- Coverage

### .flake8
Flake8-specific configuration

### .pre-commit-config.yaml
Pre-commit hooks configuration

### .editorconfig
Editor settings for consistency across IDEs

---

## Troubleshooting

### Black and Flake8 Conflicts

Black and Flake8 may conflict on line length. Solution:
```ini
# .flake8
extend-ignore = E203, E501, W503
```

### MyPy Import Errors

For third-party packages without types:
```toml
# pyproject.toml
[[tool.mypy.overrides]]
module = "package_name.*"
ignore_missing_imports = true
```

### Pre-commit Hook Failures

If pre-commit hooks fail:
```bash
# Skip hooks (emergency only)
git commit --no-verify

# Fix issues
pre-commit run --all-files
```

### Slow Linting

Use Ruff instead of Flake8:
```bash
# Faster
ruff check .

# Instead of
flake8 .
```

---

## IDE Integration

### VS Code

Install extensions:
- Python
- Pylance
- Black Formatter
- Ruff
- MyPy

Settings (`.vscode/settings.json`):
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.linting.banditEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### PyCharm

1. Enable Black: `Settings → Tools → Black`
2. Enable MyPy: `Settings → Tools → Python Integrated Tools → Type Checker`
3. Enable Flake8: `Settings → Tools → External Tools`

---

## Metrics

### Code Quality Metrics

Track these metrics:
- **Test Coverage:** > 80%
- **Type Coverage:** > 70%
- **Maintainability Index:** > 70
- **Complexity:** < 15 per function
- **Security Issues:** 0 high/critical

### Tools for Metrics

```bash
# Test coverage
pytest --cov --cov-report=html

# Radon (complexity)
pip install radon
radon cc . -a

# Security score
bandit -r . -f json
```

---

## Resources

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pylint Documentation](https://pylint.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)

---

## Summary

To maintain code quality:

1. ✅ **Setup:** Run `setup_linting.bat` once
2. ✅ **Before commit:** Run `run_linting.bat`
3. ✅ **Auto-fixes:** Use `black .` and `ruff check . --fix`
4. ✅ **Pre-commit:** Hooks run automatically
5. ✅ **CI/CD:** Checks run on every push

**Remember:** Quality tools are helpers, not obstacles. They catch bugs early and make code more maintainable!
