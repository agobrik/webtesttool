# WebTestool Quick Start Guide

## 🚀 Quick Installation (5 Minutes)

### Windows

```bash
# 1. Clone or download the repository
cd C:\Projects\testool

# 2. Run installation script
install.bat

# 3. Verify installation
python verify_installation.py

# 4. Run your first scan
python main.py --url https://example.com --profile quick
```

### Linux / macOS

```bash
# 1. Clone or download the repository
cd /path/to/testool

# 2. Run installation script
chmod +x install.sh
./install.sh

# 3. Verify installation
python3 verify_installation.py

# 4. Run your first scan
python3 main.py --url https://example.com --profile quick
```

## 📋 Manual Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium firefox

# Verify installation
python verify_installation.py
```

## 🎯 Your First Scan

### Example 1: Quick Security Scan

```bash
python main.py --url https://example.com --profile security
```

**What it does:**
- Crawls up to 10 pages
- Runs security tests only
- Generates HTML and JSON reports
- Takes about 2-5 minutes

### Example 2: Full Comprehensive Scan

```bash
python main.py --url https://example.com
```

**What it does:**
- Crawls up to 1000 pages
- Runs all test modules
- Tests security, performance, SEO, accessibility
- Takes 10-30 minutes (depending on site size)

### Example 3: Specific Tests Only

```bash
python main.py --url https://example.com --tests security,performance
```

**What it does:**
- Runs only security and performance tests
- Skips SEO and accessibility
- Faster execution

### Example 4: With Authentication

Create a custom config file `myconfig.yaml`:

```yaml
target:
  url: "https://myapp.com"
  auth:
    type: "basic"
    username: "testuser"
    password: "testpass"
```

Run:
```bash
python main.py --url https://myapp.com --config myconfig.yaml
```

## 📊 Understanding Results

After scan completes, find your reports in `reports/scan_YYYYMMDD_HHMMSS/`:

- **report.html** - Interactive HTML report (open in browser)
- **report.json** - Machine-readable JSON
- **summary.txt** - Quick text summary

### Report Shows:
- Total findings by severity (Critical, High, Medium, Low)
- Detailed vulnerability descriptions
- URLs affected
- CWE/OWASP classifications
- Remediation recommendations

## 🔧 Common Commands

```bash
# Quick scan (fast, limited pages)
python main.py --url https://example.com --profile quick

# Security-only scan
python main.py --url https://example.com --profile security

# Performance-only scan
python main.py --url https://example.com --profile performance

# Verbose output
python main.py --url https://example.com --verbose

# Custom output directory
python main.py --url https://example.com --output ./my-reports

# Specific tests
python main.py --url https://example.com --tests security,seo

# With custom config
python main.py --url https://example.com --config custom.yaml
```

## 📖 Test Profiles

| Profile | Tests | Crawl Limit | Duration |
|---------|-------|-------------|----------|
| `quick` | All enabled | 10 pages | 30-60s |
| `full` | All enabled | 1000 pages | 10-30m |
| `security` | Security only | 1000 pages | 5-15m |
| `performance` | Performance only | 100 pages | 2-5m |

## 🎨 What Gets Tested?

### Security (30+ tests)
✓ SQL Injection
✓ XSS (Cross-Site Scripting)
✓ CSRF
✓ Command Injection
✓ Path Traversal
✓ Security Headers
✓ SSL/TLS
✓ CORS
✓ And more...

### Performance
✓ Response Times
✓ Load Testing
✓ Resource Compression
✓ Caching

### SEO
✓ Meta Tags
✓ Headings Structure
✓ Images Alt Text
✓ Open Graph
✓ Mobile-Friendly

### Accessibility
✓ WCAG 2.1 Compliance
✓ ARIA Attributes
✓ Form Labels
✓ Keyboard Navigation

## ⚙️ Configuration

### Basic Configuration

Create `config/custom_config.yaml`:

```yaml
target:
  url: "https://yoursite.com"

crawler:
  max_pages: 100
  max_depth: 3

modules:
  security:
    enabled: true
  performance:
    enabled: true
  seo:
    enabled: false
  accessibility:
    enabled: false
```

### With Authentication

```yaml
target:
  url: "https://yoursite.com"
  auth:
    type: "bearer"  # or "basic", "digest"
    token: "your-api-token"
  headers:
    X-API-Key: "your-key"
```

## 🐛 Troubleshooting

### Issue: Python not found
```bash
# Windows - Install Python 3.11+ from python.org
# Linux: sudo apt install python3.11
# Mac: brew install python@3.11
```

### Issue: Playwright browsers not installed
```bash
python -m playwright install
```

### Issue: Permission denied (Linux/Mac)
```bash
chmod +x install.sh
```

### Issue: Scan too slow
```bash
# Use quick profile
python main.py --url https://example.com --profile quick

# Or limit pages in config
crawler:
  max_pages: 20
```

### Issue: Too many false positives
```yaml
# Disable aggressive mode in config
modules:
  security:
    aggressive_mode: false
```

## 📝 Next Steps

1. **Read Full Documentation**
   - USAGE_GUIDE.md - Detailed usage
   - ARCHITECTURE.md - Technical details
   - PROJECT_SUMMARY.md - Feature overview

2. **Customize Configuration**
   - Edit `config/default_config.yaml`
   - Create your own profiles

3. **Integrate with CI/CD**
   - See USAGE_GUIDE.md for GitHub Actions example

4. **Programmatic Usage**
   - Check `examples/basic_scan.py`
   - Check `examples/advanced_scan.py`

## ⚠️ Important Notes

### Legal & Ethical
- **ONLY** test websites you own or have explicit permission to test
- Unauthorized testing may be **illegal**
- Always get written authorization

### Performance
- Default scans can be intensive
- Use `--profile quick` for initial tests
- Consider rate limiting for production sites

### Results
- Review findings for false positives
- Not all findings are exploitable
- Use professional judgment

## 🎓 Example Session

```bash
# 1. Verify installation
python verify_installation.py

# 2. Run quick test
python main.py --url https://example.com --profile quick

# 3. Review report
# Open: reports/scan_YYYYMMDD_HHMMSS/report.html

# 4. Run full scan if satisfied
python main.py --url https://example.com

# 5. Check results in browser
# Reports saved in: reports/scan_YYYYMMDD_HHMMSS/
```

## 💡 Pro Tips

1. **Start with quick profile** to validate setup
2. **Review reports in HTML** for best experience
3. **Use specific tests** for faster feedback
4. **Check logs** if something fails
5. **Save configurations** for repeated scans

## 📞 Getting Help

- Run: `python main.py --help`
- Check: USAGE_GUIDE.md
- Test system: `python test_system.py`
- Verify installation: `python verify_installation.py`

## 🎉 You're Ready!

```bash
# Start testing now!
python main.py --url https://your-website.com --profile quick
```

**Happy Testing! 🔒🚀**
