# WebTestool Usage Guide

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install
```

### 2. Basic Usage

```bash
# Simple scan
python main.py --url https://example.com

# Quick scan (limited crawling)
python main.py --url https://example.com --profile quick

# Security-only scan
python main.py --url https://example.com --profile security

# Specific tests
python main.py --url https://example.com --tests security,performance

# Verbose output
python main.py --url https://example.com --verbose

# Custom output directory
python main.py --url https://example.com --output ./my-reports
```

## Test Profiles

### Full Profile (default)
- Crawls entire website (up to configured limits)
- Runs all enabled test modules
- Generates comprehensive reports

### Quick Profile
- Limited crawling (10 pages max)
- Faster execution
- Suitable for quick checks

### Security Profile
- Focuses only on security testing
- SQL Injection, XSS, CSRF, etc.
- Disables other modules

### Performance Profile
- Load testing
- Response time analysis
- Resource optimization checks

## Configuration

### Using Custom Configuration

Create a `custom_config.yaml`:

```yaml
target:
  url: "https://example.com"
  auth:
    type: "bearer"
    token: "your-api-token"

crawler:
  max_depth: 10
  max_pages: 500

modules:
  security:
    enabled: true
    sql_injection:
      enabled: true
      test_types: ["union", "boolean", "time", "error"]
    xss:
      enabled: true
  performance:
    enabled: true
```

Run with custom config:
```bash
python main.py --url https://example.com --config custom_config.yaml
```

## Test Modules

### Security Module
Tests for:
- SQL Injection (Union, Boolean-based, Time-based, Error-based)
- Cross-Site Scripting (Reflected, Stored, DOM-based)
- Cross-Site Request Forgery (CSRF)
- XML External Entity (XXE)
- Server-Side Request Forgery (SSRF)
- Command Injection
- Path Traversal
- Security Headers
- SSL/TLS Configuration
- CORS Misconfiguration
- Cookie Security
- Information Disclosure
- Clickjacking
- Open Redirect

### Performance Module
Tests for:
- Response Time Analysis
- Load Testing
- Stress Testing
- Resource Compression
- Caching Configuration
- Page Size Optimization

### SEO Module
Tests for:
- Meta Tags (Title, Description, Keywords)
- Structured Data (Schema.org)
- Open Graph Tags
- Heading Structure
- Image Alt Text
- Canonical URLs
- Mobile-Friendliness
- XML Sitemap

### Accessibility Module
Tests for:
- WCAG 2.1 Compliance
- Image Alt Text
- Form Labels
- Heading Hierarchy
- ARIA Attributes
- Keyboard Navigation
- Color Contrast
- Semantic HTML

## Authentication

### Basic Authentication

```yaml
target:
  auth:
    type: "basic"
    username: "user"
    password: "pass"
```

### Bearer Token

```yaml
target:
  auth:
    type: "bearer"
    token: "your-jwt-token"
```

### Custom Headers

```yaml
target:
  headers:
    Authorization: "Bearer xxx"
    X-API-Key: "your-key"
```

## Reports

WebTestool generates multiple report formats:

- **HTML**: Interactive, detailed report with styling
- **JSON**: Machine-readable format for CI/CD integration
- **TXT**: Summary text file

Reports are saved in the configured output directory with timestamps.

## Advanced Usage

### Python API

```python
import asyncio
from core import ConfigManager, TestEngine
from reporters import ReportGenerator

async def scan():
    config = ConfigManager()
    config.set('target.url', 'https://example.com')

    engine = TestEngine(config)
    result = await engine.run()

    reporter = ReportGenerator(config)
    reporter.generate_reports(result)

asyncio.run(scan())
```

### Custom Test Module

Create your own test module:

```python
from core.module_loader import BaseTestModule
from core.models import Category, ModuleResult, TestStatus

class CustomModule(BaseTestModule):
    name = "custom"
    description = "My custom tests"
    category = Category.SECURITY

    async def run(self, context):
        module_result = ModuleResult(
            name=self.name,
            category=self.category,
            status=TestStatus.RUNNING
        )

        # Your test logic here

        module_result.mark_completed(TestStatus.PASSED)
        return module_result
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Security Scan

on: [push]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install

      - name: Run WebTestool
        run: |
          python main.py --url ${{ secrets.TARGET_URL }} --profile security

      - name: Upload Reports
        uses: actions/upload-artifact@v2
        with:
          name: security-reports
          path: reports/
```

## Best Practices

1. **Always get authorization** before scanning websites you don't own
2. **Use rate limiting** to avoid overwhelming target servers
3. **Review false positives** - not all findings may be actual vulnerabilities
4. **Test in staging** before production
5. **Customize configuration** for your specific needs
6. **Regular scans** - integrate into your CI/CD pipeline

## Troubleshooting

### Scan is too slow
- Reduce `crawler.max_pages`
- Increase `crawler.crawl_delay`
- Use `--profile quick`

### Too many false positives
- Disable `aggressive_mode` in security module
- Review and customize test payloads

### SSL Certificate Errors
- For testing environments, SSL verification is disabled
- For production, ensure valid certificates

## Legal Notice

**IMPORTANT**: Only scan websites you own or have explicit permission to test. Unauthorized scanning may be illegal.

## Support

For issues and questions:
- GitHub Issues: [Report Issue]
- Documentation: README.md
