# 🚀 WebTestool - Comprehensive Automated Web Testing Framework

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

An enterprise-grade, fully automated web testing framework that performs extensive security, performance, SEO, accessibility, API, and infrastructure testing on any website.

**🎯 One Tool. Complete Coverage. Professional Results.**

## 🌟 Features

### Security Testing (30+ Tests)
- SQL Injection (all types: Union, Boolean, Time-based, Error-based)
- Cross-Site Scripting (Reflected, Stored, DOM-based)
- Cross-Site Request Forgery (CSRF)
- XML External Entity (XXE)
- Server-Side Request Forgery (SSRF)
- Command Injection
- Path Traversal
- Insecure Deserialization
- Security Headers Analysis
- SSL/TLS Configuration
- Authentication Bypass
- Session Management
- Cookie Security
- CORS Misconfiguration
- API Security
- And many more...

### Performance Testing
- Load Testing (concurrent users simulation)
- Stress Testing (breaking point analysis)
- Response Time Analysis
- Time to First Byte (TTFB)
- Resource Loading Performance
- Memory Leak Detection
- CPU Usage Monitoring
- Network Waterfall Analysis
- Cache Efficiency
- CDN Performance

### Functional Testing
- Form Validation (all input types)
- Navigation Flow
- User Workflows (E2E scenarios)
- JavaScript Functionality
- AJAX Request Validation
- File Upload/Download
- Search Functionality
- Pagination
- Sorting & Filtering
- Modal Dialogs
- Drag & Drop
- Error Handling

### API Testing
- REST API Endpoints
- GraphQL Queries/Mutations
- SOAP Services
- WebSocket Connections
- Request/Response Validation
- Schema Validation
- Rate Limiting
- Authentication Methods
- Error Codes
- Data Integrity

### Compatibility Testing
- Multi-Browser (Chrome, Firefox, Safari, Edge)
- Responsive Design (Mobile, Tablet, Desktop)
- Different Screen Resolutions
- Touch vs Mouse Events
- OS Compatibility
- Browser Version Testing

### Accessibility Testing (WCAG 2.1 AAA)
- Semantic HTML Structure
- ARIA Attributes
- Keyboard Navigation
- Screen Reader Compatibility
- Color Contrast Ratios
- Focus Management
- Alt Text for Images
- Form Labels
- Heading Hierarchy

### SEO Testing
- Meta Tags Analysis
- Structured Data (Schema.org)
- Open Graph Tags
- Twitter Cards
- Canonical URLs
- Robots.txt
- XML Sitemap
- Page Speed
- Mobile-Friendliness
- Internal Linking
- H1-H6 Structure
- Image Optimization

### Infrastructure Testing
- DNS Configuration
- SSL Certificate Validation
- HTTP/2 Support
- Compression (Gzip/Brotli)
- Caching Headers
- Security Headers
- Server Information Disclosure
- Port Scanning
- Service Detection

### Visual Regression Testing
- Screenshot Comparison
- Layout Shift Detection
- Font Rendering
- Image Loading
- CSS Rendering Differences

## 🏗️ Architecture

```
WebTestool/
├── core/               # Core framework engine
├── modules/            # Test modules (plugins)
│   ├── security/
│   ├── performance/
│   ├── functional/
│   ├── api/
│   ├── accessibility/
│   ├── seo/
│   └── ...
├── scanners/           # Web crawlers and discovery
├── reporters/          # Report generation
├── dashboard/          # Web UI
├── database/           # Data persistence
├── utils/              # Helper functions
└── config/             # Configuration files
```

## 🚀 Quick Start

### 🖥️ Desktop Application (Standalone - No Python Required!)

**Download and run the desktop app directly - perfect for non-technical users!**

#### Windows
1. Download `WebTestool-Setup.exe` from [Releases](https://github.com/agobrik/webtesttool/releases)
2. Run the installer
3. Launch WebTestool from Start Menu or Desktop
4. That's it! Start scanning websites immediately

#### Linux/macOS
1. Download `WebTestool-Linux.zip` or `WebTestool-macOS.zip` from [Releases](https://github.com/agobrik/webtesttool/releases)
2. Extract the archive
3. Run `./WebTestool`
4. Start scanning!

**Features:**
- ✅ No Python installation needed
- ✅ Beautiful modern UI
- ✅ One-click complete scan
- ✅ Real-time progress tracking
- ✅ Interactive reports viewer
- ✅ System health monitoring

**See [DESKTOP_APP_BUILD.md](DESKTOP_APP_BUILD.md) for building from source.**

---

### 💻 Installation (For Developers)

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh && ./install.sh
```

### Verification

```bash
python verify_installation.py
```

### Run Your First Scan

```bash
# Quick scan (30-60 seconds)
python main.py --url https://example.com --profile quick

# Full security scan
python main.py --url https://example.com --profile security

# Complete scan (all tests)
python main.py --url https://example.com
```

### View Results

Reports are generated in `reports/scan_YYYYMMDD_HHMMSS/`:
- `report.html` - Open in browser for interactive report
- `report.json` - Machine-readable format
- `summary.txt` - Quick overview

## 📊 Output Formats

- HTML Reports (detailed, interactive)
- JSON (machine-readable)
- PDF (executive summary)
- XML (CI/CD integration)
- CSV (data analysis)
- Real-time Dashboard

## ⚙️ Configuration

Create `config.yaml`:

```yaml
target:
  url: https://example.com
  auth:
    type: basic
    username: test
    password: test

scan:
  depth: 5
  timeout: 30
  parallel: 10

modules:
  security:
    enabled: true
    aggressive: false
  performance:
    enabled: true
    users: 100
    duration: 300
```

## 📜 License

MIT License - Educational and authorized testing only.

## ⚠️ Legal Notice

This tool is for authorized security testing only. Always obtain written permission before testing any website you don't own.
