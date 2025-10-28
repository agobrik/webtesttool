# WebTestool Architecture Documentation

## System Overview

WebTestool is a comprehensive, modular web testing framework designed to perform extensive security, performance, functional, and compliance testing on web applications.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI / API                            │
│                        (main.py)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Test Engine (core/engine.py)              │
│  - Orchestrates entire testing workflow                      │
│  - Manages module execution (parallel/sequential)            │
│  - Handles results aggregation                              │
└──────┬──────────────────────────────────────────────────────┘
       │
       ├──────────────┬──────────────┬──────────────┬─────────┐
       ▼              ▼              ▼              ▼         ▼
┌─────────┐    ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│ Config  │    │  Scanner │   │  Module  │   │  Report  │   │
│ Manager │    │          │   │  Loader  │   │Generator │   │
└─────────┘    └──────────┘   └──────────┘   └──────────┘   │
                                      │                       │
                                      ▼                       │
                           ┌──────────────────┐              │
                           │  Test Modules    │              │
                           └─────────┬────────┘              │
                                     │                       │
            ┌────────────────────────┼────────────────┐      │
            ▼            ▼           ▼        ▼       ▼      ▼
     ┌──────────┐  ┌─────────┐  ┌──────┐  ┌────┐  ┌────┐ ┌────┐
     │ Security │  │ Perform │  │ SEO  │  │API │  │... │ │... │
     │  Module  │  │  ance   │  │Module│  │Mod │  │    │ │    │
     └──────────┘  └─────────┘  └──────┘  └────┘  └────┘ └────┘
```

## Core Components

### 1. Configuration Manager (`core/config.py`)

**Purpose**: Centralized configuration management

**Features**:
- YAML-based configuration
- Hierarchical configuration merging
- Runtime configuration updates
- Validation

**Key Classes**:
- `ConfigManager`: Main configuration handler
- `Config`: Pydantic model for type-safe configuration

### 2. Web Scanner (`core/scanner.py`)

**Purpose**: Website crawling and discovery

**Features**:
- Asynchronous crawling
- Depth and page limits
- Robots.txt compliance
- Form and input discovery
- API endpoint detection
- JavaScript analysis

**Key Classes**:
- `WebScanner`: Main crawler
- `CrawledPage`: Page metadata model

### 3. Test Engine (`core/engine.py`)

**Purpose**: Orchestrates entire testing process

**Workflow**:
1. Initialize configuration
2. Run web scanner (discovery phase)
3. Load and initialize test modules
4. Execute modules (parallel or sequential)
5. Aggregate results
6. Generate reports

**Key Classes**:
- `TestEngine`: Main orchestrator

### 4. Module Loader (`core/module_loader.py`)

**Purpose**: Dynamic test module discovery and loading

**Features**:
- Plugin architecture
- Dynamic module discovery
- Module lifecycle management
- Category-based filtering

**Key Classes**:
- `ModuleLoader`: Module discovery and loading
- `BaseTestModule`: Base class for all modules

### 5. Data Models (`core/models.py`)

**Purpose**: Type-safe data structures

**Key Models**:
- `ScanResult`: Complete scan results
- `ModuleResult`: Module execution results
- `TestResult`: Individual test results
- `Finding`: Security/quality findings
- `TestContext`: Runtime context for tests

## Test Modules

### Security Module (`modules/security/`)

**Tests**:
- SQL Injection (Union, Boolean, Time-based, Error-based)
- Cross-Site Scripting (Reflected, Stored, DOM-based)
- CSRF
- XXE
- SSRF
- Command Injection
- Path Traversal
- Security Headers
- SSL/TLS
- CORS
- Cookie Security
- Information Disclosure
- Clickjacking
- Open Redirect

**Architecture**:
```
security/
├── security_module.py       # Main module
└── tests/
    ├── base_security_test.py  # Base class
    ├── sql_injection.py
    ├── xss.py
    ├── csrf.py
    └── ... (other tests)
```

### Performance Module (`modules/performance/`)

**Tests**:
- Response Time Analysis
- Load Testing
- Resource Optimization
- Compression Check
- Caching Analysis

### SEO Module (`modules/seo/`)

**Tests**:
- Meta Tags
- Structured Data
- Open Graph
- Heading Structure
- Image Alt Text
- Mobile-Friendliness

### Accessibility Module (`modules/accessibility/`)

**Tests**:
- WCAG 2.1 Compliance
- ARIA Attributes
- Form Labels
- Heading Hierarchy
- Image Alt Text
- Semantic HTML

## Reporting System

### Report Generator (`reporters/report_generator.py`)

**Supports Multiple Formats**:
- HTML (interactive, styled)
- JSON (machine-readable)
- TXT (summary)
- (Extensible for PDF, XML, CSV)

**Report Structure**:
- Executive summary
- Findings by severity
- Module-wise results
- Detailed evidence
- Remediation recommendations

## Configuration System

### Configuration Hierarchy

1. **Default Configuration** (`config/default_config.yaml`)
2. **Custom Configuration** (optional)
3. **Runtime Overrides** (CLI arguments)

### Configuration Sections

```yaml
target:           # Target website configuration
crawler:          # Web crawler settings
modules:          # Test module configuration
  security:       # Security module settings
  performance:    # Performance module settings
  seo:            # SEO module settings
  accessibility:  # Accessibility settings
reporting:        # Report generation settings
database:         # Database configuration
dashboard:        # Web dashboard settings
logging:          # Logging configuration
advanced:         # Advanced options
```

## Execution Flow

### 1. Initialization Phase
```
CLI Command → ConfigManager → Validate Configuration
```

### 2. Discovery Phase
```
WebScanner → Crawl Website → Extract:
  - Pages
  - Forms
  - Inputs
  - API Endpoints
  - Links
```

### 3. Testing Phase
```
ModuleLoader → Discover Modules → For Each Module:
  - Initialize
  - Setup
  - Run Tests
  - Teardown
  - Collect Results
```

### 4. Reporting Phase
```
ReportGenerator → Aggregate Results → Generate:
  - HTML Report
  - JSON Report
  - Text Summary
```

## Extensibility

### Creating Custom Modules

```python
from core.module_loader import BaseTestModule
from core.models import Category, ModuleResult

class CustomModule(BaseTestModule):
    name = "custom"
    description = "Custom test module"
    category = Category.SECURITY
    version = "1.0.0"

    async def run(self, context):
        module_result = ModuleResult(...)

        # Your test logic

        return module_result
```

### Custom Tests within Modules

```python
from .base_security_test import BaseSecurityTest

class CustomSecurityTest(BaseSecurityTest):
    name = "custom_test"
    description = "Custom security test"

    async def run_test(self, context):
        # Test logic

        if vulnerability_found:
            self.add_finding(
                title="Vulnerability Found",
                severity=Severity.HIGH,
                ...
            )
```

## Technology Stack

### Core
- **Python 3.11+**: Main language
- **AsyncIO**: Asynchronous programming
- **Pydantic**: Data validation
- **HTTPX**: Async HTTP client

### Web Interaction
- **Playwright**: Browser automation
- **BeautifulSoup4**: HTML parsing
- **Scrapy**: Web crawling

### Testing
- **Custom Security Scanners**: SQL injection, XSS, etc.
- **SSL/TLS Libraries**: Certificate validation

### Reporting
- **Jinja2**: Template engine
- **JSON**: Data serialization
- **HTML/CSS**: Report presentation

### CLI
- **Click**: Command-line interface
- **Loguru**: Logging

## Performance Considerations

### Asynchronous Execution
- All I/O operations are async
- Concurrent request handling
- Parallel module execution

### Rate Limiting
- Configurable request delays
- Concurrent request limits
- Respectful crawling

### Resource Management
- Connection pooling
- Memory-efficient crawling
- Streaming for large responses

## Security Considerations

### Ethical Testing
- Authorization required
- Configurable aggression levels
- Rate limiting to prevent DoS

### Data Handling
- No sensitive data storage by default
- Configurable evidence collection
- Secure credential handling

## Future Enhancements

### Planned Features
- Web Dashboard (real-time monitoring)
- Database persistence (SQLite/PostgreSQL)
- API REST interface
- More test modules (Functional, Visual Regression)
- Advanced reporting (PDF, Executive summaries)
- CI/CD integrations
- Plugin marketplace

### Scalability
- Distributed scanning
- Cloud deployment
- Kubernetes support
- Job queue system (Celery/Redis)

## Development Guidelines

### Adding New Tests
1. Create test class inheriting from appropriate base
2. Implement `run_test()` method
3. Use `add_finding()` for issues
4. Add configuration options
5. Update documentation

### Code Style
- PEP 8 compliance
- Type hints
- Comprehensive docstrings
- Error handling

### Testing
- Unit tests for core components
- Integration tests for modules
- Test fixtures for common scenarios

## Performance Benchmarks

### Typical Scan Times
- **Quick Scan** (10 pages): 30-60 seconds
- **Medium Scan** (100 pages): 5-10 minutes
- **Full Scan** (1000 pages): 30-60 minutes

*Times vary based on target response times and test configuration*

## Troubleshooting

### Common Issues

**Slow Scans**:
- Reduce `crawler.max_pages`
- Increase `crawler.crawl_delay`
- Disable unnecessary modules

**High Memory Usage**:
- Reduce concurrent requests
- Limit crawl depth
- Enable result streaming

**False Positives**:
- Adjust test sensitivity
- Customize payloads
- Review test configuration

## License

MIT License - See LICENSE file for details

## Contributors

WebTestool Team

---

**Version**: 1.0.0
**Last Updated**: 2024
**Status**: Production Ready
