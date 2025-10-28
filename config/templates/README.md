# Configuration Templates

Pre-built configuration templates for common scanning scenarios.

## Available Templates

### 1. Quick Scan (`quick.yaml`)
**Duration:** 1-3 minutes
**Use case:** Quick validation, CI/CD integration, rapid testing

**Features:**
- Limited crawling (10 pages, depth 2)
- Essential security checks (SQL injection, XSS, SSL)
- Basic performance metrics
- Minimal reporting

**Usage:**
```bash
python main.py --config config/templates/quick.yaml --url https://example.com
```

---

### 2. E-Commerce Security (`ecommerce.yaml`)
**Duration:** 5-15 minutes
**Use case:** Online stores, payment gateways, shopping platforms

**Focus:**
- Payment security (PCI DSS compliance)
- Data protection (PII, credit cards)
- Injection attacks (SQL, XSS, CSRF)
- Authentication & authorization
- Session management
- Price tampering

**Usage:**
```bash
python main.py --config config/templates/ecommerce.yaml --url https://shop.example.com
```

**Required secrets:**
```bash
# Store credentials securely
python -m utils.secrets_manager
# Then enter: ecommerce / username / password
```

---

### 3. API Testing (`api.yaml`)
**Duration:** 3-8 minutes
**Use case:** REST APIs, GraphQL, JSON-based services

**Focus:**
- Authentication testing (JWT, OAuth, API keys)
- Authorization (IDOR, privilege escalation)
- Input validation
- Rate limiting
- CORS configuration
- API versioning
- Error handling

**Usage:**
```bash
python main.py --config config/templates/api.yaml --url https://api.example.com/v1
```

**Supported authentication:**
- Bearer tokens
- API keys
- OAuth2
- Basic auth

---

### 4. WCAG Compliance (`compliance.yaml`)
**Duration:** 15-30 minutes
**Use case:** Accessibility auditing, ADA/Section 508 compliance

**Focus:**
- WCAG 2.1 Level AA compliance
- Keyboard navigation
- Screen reader compatibility
- Color contrast
- Semantic HTML
- ARIA attributes
- Form accessibility

**Standards covered:**
- WCAG 2.1 Level AA
- ADA (Americans with Disabilities Act)
- Section 508
- EN 301 549

**Usage:**
```bash
python main.py --config config/templates/compliance.yaml --url https://example.com
```

---

### 5. WordPress Security (`wordpress.yaml`)
**Duration:** 10-20 minutes
**Use case:** WordPress websites, themes, and plugins

**Focus:**
- Version detection
- Plugin vulnerabilities
- Theme vulnerabilities
- User enumeration
- XML-RPC security
- REST API security
- File permissions
- Configuration issues

**Checks:**
- Outdated WordPress core
- Vulnerable plugins
- Weak passwords
- Directory listing
- Backup file exposure
- Debug mode enabled

**Usage:**
```bash
python main.py --config config/templates/wordpress.yaml --url https://wordpress-site.com
```

---

### 6. Full Comprehensive Scan (`full.yaml`)
**Duration:** 15-45 minutes
**Use case:** Complete website audit, compliance reporting

**Includes:**
- **Security:** All OWASP Top 10 tests
- **Performance:** Load testing, resource optimization
- **SEO:** Complete on-page and technical SEO
- **Accessibility:** WCAG 2.1 AA compliance
- **API:** REST and GraphQL testing
- **Functional:** Forms, navigation, search

**Compliance standards:**
- OWASP Top 10
- PCI DSS
- GDPR
- HIPAA
- WCAG 2.1 AA
- ISO 27001

**Usage:**
```bash
python main.py --config config/templates/full.yaml --url https://example.com
```

---

## How to Use Templates

### Method 1: Use template directly
```bash
python main.py --config config/templates/[template].yaml --url https://your-site.com
```

### Method 2: Copy and customize
```bash
# Copy template to your config directory
cp config/templates/ecommerce.yaml config/my-shop.yaml

# Edit the configuration
# Change URL, authentication, and other settings

# Run with your custom config
python main.py --config config/my-shop.yaml
```

### Method 3: Interactive mode (uses templates)
```bash
python -m cli.interactive
```
The interactive mode will ask you to select a profile (quick, security, performance, full) which maps to these templates.

---

## Customizing Templates

All templates can be customized to fit your specific needs.

### Common customizations:

#### 1. Change target URL
```yaml
target:
  url: "https://your-website.com"
```

#### 2. Add authentication
```yaml
target:
  auth:
    type: "bearer"
    token: "{{ SECRET:myapp:token }}"
```

#### 3. Adjust crawling limits
```yaml
crawler:
  max_pages: 200  # Increase/decrease pages
  max_depth: 5    # Increase/decrease depth
  crawl_delay: 0.5  # Adjust delay between requests
```

#### 4. Enable/disable modules
```yaml
modules:
  security:
    enabled: true
  performance:
    enabled: false  # Disable if not needed
```

#### 5. Adjust reporting
```yaml
reporting:
  format: "html"
  exports:
    - "html"
    - "pdf"
    - "json"
```

---

## Template Parameters Reference

### Target Configuration
- `url`: Target website URL
- `auth`: Authentication settings
- `headers`: Custom HTTP headers

### Crawler Configuration
- `max_pages`: Maximum pages to crawl
- `max_depth`: Maximum crawl depth
- `crawl_delay`: Delay between requests (seconds)
- `include_patterns`: URL patterns to include
- `exclude_patterns`: URL patterns to exclude

### Modules
- `security`: Security testing module
- `performance`: Performance testing module
- `seo`: SEO analysis module
- `accessibility`: Accessibility testing module
- `api`: API testing module
- `functional`: Functional testing module

### Reporting
- `format`: Output format (html, pdf, json)
- `output_dir`: Directory for reports
- `exports`: List of export formats

---

## Secret Management

Templates use secret references to avoid storing credentials in plaintext.

### Format
```yaml
auth:
  password: "{{ SECRET:service:username }}"
```

### Storing secrets
```bash
# Method 1: CLI
python -m utils.secrets_manager

# Method 2: Interactive mode
python -m cli.interactive
# (It will prompt and store secrets automatically)

# Method 3: Programmatically
from utils.secrets_manager import get_secrets_manager
manager = get_secrets_manager()
manager.store_credential("service", "username", "password")
```

---

## Best Practices

### 1. Start with quick scan
Always start with a quick scan to verify configuration:
```bash
python main.py --config config/templates/quick.yaml --url https://example.com
```

### 2. Use appropriate template
- E-commerce sites → `ecommerce.yaml`
- APIs → `api.yaml`
- WordPress → `wordpress.yaml`
- Compliance audit → `compliance.yaml`
- Complete audit → `full.yaml`

### 3. Test on staging first
Never run aggressive scans on production without testing on staging.

### 4. Respect rate limits
```yaml
rate_limit:
  requests_per_second: 5  # Lower for production
  max_concurrent: 2
```

### 5. Use caching
```yaml
cache:
  enabled: true
  ttl: 3600  # Cache for 1 hour
```

### 6. Review before running
Always review the template configuration before running, especially:
- Crawl limits
- Rate limiting
- Aggressive tests
- Form submission

---

## Creating Custom Templates

You can create your own templates for specific use cases.

### Example: Creating a blog template

```yaml
# config/templates/blog.yaml
target:
  url: "https://blog.example.com"

crawler:
  max_pages: 100
  max_depth: 5

  include_patterns:
    - "/posts/*"
    - "/category/*"
    - "/author/*"

modules:
  security:
    enabled: true
    tests:
      - xss:
          enabled: true
          test_comments: true

  seo:
    enabled: true
    tests:
      - meta_tags:
          enabled: true
      - structured_data:
          enabled: true
          check_article_markup: true

  accessibility:
    enabled: true
    wcag_level: "AA"

reporting:
  format: "html"
  output_dir: "reports/blog"
```

---

## Troubleshooting

### Template not found
```
Error: Configuration file not found
```
**Solution:** Use absolute or relative path:
```bash
python main.py --config ./config/templates/quick.yaml --url https://example.com
```

### Secret not resolved
```
Warning: Secret not found: myapp/username
```
**Solution:** Store the secret:
```bash
python -m utils.secrets_manager
```

### Too many pages crawled
```
Warning: Max pages limit reached
```
**Solution:** Adjust `max_pages` in config:
```yaml
crawler:
  max_pages: 50  # Lower limit
```

---

## Support

For issues or questions:
- Check documentation: `docs/`
- View examples: `YENI_OZELLIKLER_KULLANIM.md`
- Report bugs: GitHub Issues
