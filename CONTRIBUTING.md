# Contributing to WebTestool

Thank you for your interest in contributing to WebTestool! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Our Standards

- **Be respectful** of differing opinions and experiences
- **Be collaborative** and help others learn
- **Be inclusive** and welcoming to all contributors
- **Be patient** with newcomers and their questions

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- pip (Python package manager)
- Virtual environment tool (venv, virtualenv, or conda)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/webtestool.git
cd webtestool
```

3. Add upstream remote:

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/webtestool.git
```

## 💻 Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install Playwright browsers
python -m playwright install
```

### 3. Install Pre-commit Hooks

```bash
pre-commit install
```

### 4. Verify Installation

```bash
python main.py --help
pytest tests/unit/
```

## 🔨 Making Changes

### Branch Naming Convention

Use descriptive branch names with prefixes:

- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Urgent fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or changes

Example: `feature/add-graphql-support`

### Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**

```
feat(security): add GraphQL injection detection

Implement GraphQL-specific security tests to detect
injection vulnerabilities in GraphQL queries.

Closes #123
```

## 📏 Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line Length**: 100 characters (not 79)
- **Quotes**: Use double quotes for strings
- **Imports**: Organize with isort
- **Type Hints**: Required for all functions

### Code Formatting

We use **Black** for automatic formatting:

```bash
black .
```

### Import Organization

Use **isort** for import sorting:

```bash
isort .
```

### Type Checking

Use **mypy** for type checking:

```bash
mypy . --ignore-missing-imports
```

### Linting

Multiple linters are used:

```bash
# flake8
flake8 .

# pylint
pylint core/ modules/ reporters/ utils/

# ruff
ruff check .
```

### Documentation

- **Docstrings**: Use Google style
- **Comments**: Explain "why", not "what"
- **Type Hints**: Required for all public functions

**Example:**

```python
def scan_url(url: str, depth: int = 3, timeout: float = 30.0) -> ScanResult:
    """
    Scan a URL for security vulnerabilities.

    This function performs a comprehensive security scan of the provided URL,
    checking for common vulnerabilities like XSS, SQL injection, and CSRF.

    Args:
        url: The target URL to scan
        depth: Maximum crawl depth (default: 3)
        timeout: Request timeout in seconds (default: 30.0)

    Returns:
        ScanResult object containing all findings

    Raises:
        ValidationError: If URL is invalid
        NetworkError: If target is unreachable

    Example:
        >>> result = scan_url("https://example.com", depth=2)
        >>> print(result.summary)
    """
    pass
```

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=. --cov-report=html

# Specific test
pytest tests/unit/test_config.py::test_config_validation
```

### Writing Tests

- **File naming**: `test_*.py` or `*_test.py`
- **Function naming**: `test_<description>`
- **Use fixtures**: Leverage pytest fixtures
- **Use parametrize**: For multiple test cases
- **Mock external calls**: Use unittest.mock or pytest-mock

**Example:**

```python
import pytest
from core.config import ConfigManager

class TestConfigManager:
    """Tests for ConfigManager class"""

    @pytest.fixture
    def config_manager(self):
        """Create a ConfigManager instance"""
        return ConfigManager()

    def test_load_default_config(self, config_manager):
        """Test loading default configuration"""
        assert config_manager.get('target.url') is None

    @pytest.mark.parametrize("key,expected", [
        ('modules.security.enabled', True),
        ('modules.performance.enabled', True),
        ('crawler.max_depth', 3),
    ])
    def test_default_values(self, config_manager, key, expected):
        """Test default configuration values"""
        assert config_manager.get(key) == expected
```

### Test Coverage

- **Target**: 80% minimum
- **Critical paths**: 100% coverage
- **New code**: Must include tests

## 🔄 Pull Request Process

### Before Submitting

1. **Update your branch**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks**:
   ```bash
   # Format code
   black .
   isort .

   # Run linters
   flake8 .
   mypy .

   # Run tests
   pytest
   ```

3. **Update documentation** if needed

4. **Add tests** for new features

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No merge conflicts

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
Describe testing performed

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code reviewed
- [ ] Tests passing
- [ ] Documentation updated
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **At least one reviewer** approval required
3. **Reviewer feedback** addressed
4. **Squash and merge** (preferred)

## 📦 Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Steps

1. Update version in `setup.py` and `__init__.py`
2. Update `RELEASE_NOTES.md`
3. Create release PR
4. Tag release: `git tag v1.2.3`
5. Push tag: `git push origin v1.2.3`
6. GitHub Actions will auto-publish

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Use latest version
3. Verify it's reproducible

### Bug Report Template

```markdown
## Bug Description
Clear description

## Steps to Reproduce
1. Step 1
2. Step 2
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 10]
- Python: [e.g., 3.11]
- Version: [e.g., 2.0.0]

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches considered

## Additional Context
Any other relevant information
```

## 📞 Getting Help

- **GitHub Issues**: For bugs and features
- **Discussions**: For questions and ideas
- **Discord**: [Join our community](#)
- **Email**: [support@example.com](#)

## 🏆 Recognition

Contributors will be:
- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- Acknowledged in documentation

Thank you for contributing to WebTestool! 🎉
