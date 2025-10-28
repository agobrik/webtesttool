# WebTestool - Advanced Features Guide

## 🚀 New Advanced Features

WebTestool v1.5.0 introduces powerful new capabilities for enterprise testing.

---

## 1. 🎭 Functional Testing with Playwright

Test real browser interactions, JavaScript functionality, and user workflows.

### Features:
- ✅ Form validation testing
- ✅ Navigation flow testing
- ✅ JavaScript error detection
- ✅ UI component testing (modals, dropdowns)
- ✅ Dynamic content testing
- ✅ Error page testing

### Configuration:

```yaml
modules:
  functional:
    enabled: true
    forms:
      enabled: true
      test_validation: true
      test_submission: true
    navigation:
      enabled: true
      test_links: true
      test_breadcrumbs: true
    javascript:
      enabled: true
      test_ajax: true
      test_dynamic_content: true
    ui_components:
      enabled: true
      test_modals: true
      test_dropdowns: true
    error_handling:
      enabled: true
      test_404: true
      test_500: true
```

### Usage:

```bash
python main.py --url https://example.com --tests functional
```

---

## 2. 👁️ Visual Regression Testing

Detect visual changes and layout shifts across different viewports.

### Features:
- ✅ Screenshot comparison
- ✅ Baseline management
- ✅ Responsive design testing
- ✅ Layout shift detection (CLS)
- ✅ Multi-viewport testing

### Configuration:

```yaml
modules:
  visual:
    enabled: true
    screenshot_comparison: true
    baseline_dir: "baselines/"
    threshold: 0.1  # 10% difference threshold
```

### First Time Setup:

```bash
# First run creates baselines
python main.py --url https://example.com --tests visual

# Future runs compare against baselines
python main.py --url https://example.com --tests visual
```

---

## 3. 🔐 Advanced Authentication

Support for multiple authentication methods.

### Supported Auth Types:

| Type | Description | Configuration |
|------|-------------|---------------|
| **Basic** | HTTP Basic Auth | username, password |
| **Bearer** | Bearer Token | token |
| **JWT** | JSON Web Token | token |
| **API Key** | API Key Header | api_key |
| **OAuth2** | OAuth2 Token | token |
| **Form** | Form-based Login | username, password, login_url |
| **Digest** | HTTP Digest Auth | username, password |

### Configuration Examples:

#### Bearer Token:
```yaml
target:
  auth:
    type: "bearer"
    token: "your-jwt-token"
```

#### Form-based Auth:
```yaml
target:
  auth:
    type: "form"
    username: "testuser"
    password: "testpass"
    login_url: "https://example.com/login"
```

#### API Key:
```yaml
target:
  auth:
    type: "api_key"
    api_key: "your-api-key"
```

---

## 4. 📊 GraphQL Testing

Comprehensive GraphQL endpoint testing.

### Features:
- ✅ Introspection testing
- ✅ Schema analysis
- ✅ Query depth limit testing
- ✅ Batch query attacks
- ✅ Field duplication detection
- ✅ Mutation testing

### Configuration:

```yaml
modules:
  api:
    enabled: true
    graphql:
      enabled: true
      introspection: true
      test_mutations: true
      test_queries: true
```

### What It Tests:
- Introspection enabled (security risk)
- Sensitive fields in schema
- Query depth limits (DoS protection)
- Batch query limits
- Field duplication attacks

---

## 5. 🔌 WebSocket Testing

Test real-time WebSocket connections.

### Features:
- ✅ Connection testing
- ✅ Authentication verification
- ✅ Message handling
- ✅ Message flooding (DoS)
- ✅ Injection testing

### Configuration:

```yaml
modules:
  api:
    enabled: true
    websocket:
      enabled: true
```

### Automatic Detection:
WebTestool automatically tests common WebSocket paths:
- `/ws`
- `/websocket`
- `/socket.io`
- `/api/ws`

---

## 6. 🔔 Multi-Channel Notifications

Get notified when scans complete via multiple channels.

### Supported Channels:
- 📧 Email (SMTP)
- 💬 Slack
- 💬 Discord
- 👥 Microsoft Teams
- 🔗 Custom Webhooks

### Configuration:

#### Email:
```yaml
notifications:
  enabled: true
  email:
    enabled: true
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "your-password"
    recipients:
      - "team@example.com"
```

#### Slack:
```yaml
notifications:
  enabled: true
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

#### Discord:
```yaml
notifications:
  enabled: true
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/YOUR/WEBHOOK"
```

#### Microsoft Teams:
```yaml
notifications:
  enabled: true
  teams:
    enabled: true
    webhook_url: "https://outlook.office.com/webhook/YOUR/WEBHOOK"
```

#### Custom Webhook:
```yaml
notifications:
  enabled: true
  webhook:
    enabled: true
    url: "https://your-server.com/webhook"
```

### Notification Content:
- Scan completion status
- Finding counts by severity
- Scan duration
- URLs crawled
- Direct link to reports

---

## 7. 🔄 CI/CD Integration

Easy integration with popular CI/CD platforms.

### GitHub Actions:

```python
from integrations import GitHubActionsHelper

helper = GitHubActionsHelper()

# Generate workflow
workflow = helper.generate_workflow(
    name="Security Scan",
    target_url="${{ secrets.TARGET_URL }}",
    profile="security",
    on_schedule="0 0 * * *",  # Daily
    fail_on_high=True
)

# Save to .github/workflows/
helper.save_workflow(workflow)
```

Generated workflow includes:
- Python setup
- Dependency caching
- Playwright installation
- Scan execution
- Artifact upload
- Quality gates

### GitLab CI:

```python
from integrations import GitLabCIHelper

helper = GitLabCIHelper()
pipeline = helper.generate_pipeline(
    target_url="$TARGET_URL",
    profile="security"
)

# Save as .gitlab-ci.yml
with open('.gitlab-ci.yml', 'w') as f:
    f.write(pipeline)
```

### Jenkins:

```python
from integrations import JenkinsHelper

helper = JenkinsHelper()
jenkinsfile = helper.generate_jenkinsfile(
    target_url="${TARGET_URL}",
    profile="security"
)

# Save as Jenkinsfile
with open('Jenkinsfile', 'w') as f:
    f.write(jenkinsfile)
```

---

## 8. 🎯 Test Profiles

Pre-configured profiles for different scenarios.

| Profile | Tests | Use Case |
|---------|-------|----------|
| `quick` | All (limited pages) | Quick validation |
| `full` | All (comprehensive) | Complete audit |
| `security` | Security only | Security assessment |
| `performance` | Performance only | Load testing |
| `api` | API only | API testing |
| `functional` | Functional only | UI testing |

### Usage:

```bash
python main.py --url https://example.com --profile security
```

---

## 9. 📊 Enhanced Reporting

Advanced reporting features.

### Multiple Formats:
- **HTML**: Interactive, styled reports
- **JSON**: Machine-readable for automation
- **PDF**: Executive summaries (coming soon)
- **Database**: Historical tracking

### Database Storage:

```python
from database import DatabaseManager

db = DatabaseManager()

# Get statistics
stats = db.get_statistics()
print(f"Total scans: {stats['total_scans']}")
print(f"Total findings: {stats['total_findings']}")

# Get all scans
scans = db.get_all_scans(limit=10)

# Get findings by severity
critical = db.get_findings_by_severity('critical')
```

---

## 10. 🔧 Advanced Configuration

### Custom Profiles:

Create `profiles/security_strict.yaml`:

```yaml
extends: "config/default_config.yaml"

modules:
  security:
    enabled: true
    aggressive_mode: true
    sql_injection:
      test_types: ["union", "boolean", "time", "error"]
    xss:
      test_types: ["reflected", "stored", "dom"]
```

Use with:
```bash
python main.py --url https://example.com --config profiles/security_strict.yaml
```

### Rate Limiting:

```yaml
advanced:
  rate_limiting:
    enabled: true
    requests_per_second: 10
  max_workers: 20
  retry_failed_tests: true
  retry_count: 3
```

### Proxy Support:

```yaml
advanced:
  proxy:
    enabled: true
    http: "http://proxy.example.com:8080"
    https: "https://proxy.example.com:8080"
```

---

## 11. 🎨 Custom Test Modules

Create your own test modules.

### Example:

```python
# modules/custom/my_test.py

from core.module_loader import BaseTestModule
from core.models import Category, ModuleResult, TestStatus

class CustomModule(BaseTestModule):
    name = "custom"
    description = "My custom tests"
    category = Category.SECURITY
    version = "1.0.0"

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

---

## 12. 📈 Performance Features

### Async Execution:
- All I/O operations are asynchronous
- Parallel module execution
- Concurrent request handling

### Caching:
- Dependency caching in CI/CD
- DNS resolution caching
- Session persistence

### Resource Management:
- Configurable worker pools
- Memory-efficient crawling
- Connection pooling

---

## 13. 🛡️ Security Features

### Safe Testing:
- Rate limiting to prevent DoS
- Respectful crawling
- robots.txt compliance
- Configurable aggression levels

### Credential Management:
- Environment variable support
- Secure credential storage
- No plaintext passwords in logs

---

## 🎓 Advanced Usage Examples

### Example 1: Complete Security Audit

```bash
python main.py \
  --url https://staging.example.com \
  --profile security \
  --config configs/strict_security.yaml \
  --verbose
```

### Example 2: API Testing with Auth

```yaml
# api_test_config.yaml
target:
  url: "https://api.example.com"
  auth:
    type: "bearer"
    token: "${API_TOKEN}"

modules:
  api:
    enabled: true
  security:
    enabled: true
  performance:
    enabled: false
```

```bash
export API_TOKEN="your-token"
python main.py --config api_test_config.yaml
```

### Example 3: Visual Regression in CI/CD

```yaml
# .github/workflows/visual-test.yml
name: Visual Regression Tests
on: [push]

jobs:
  visual-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: playwright install chromium
      - run: python main.py --url ${{ secrets.URL }} --tests visual
      - uses: actions/upload-artifact@v3
        with:
          name: visual-diffs
          path: screenshots/
```

---

## 📚 Additional Resources

- **Documentation**: All guides in `/docs`
- **Examples**: Sample configs in `/examples`
- **Integrations**: CI/CD helpers in `/integrations`
- **Modules**: Test modules in `/modules`

---

## 🎉 Coming Soon

- 🤖 Machine Learning for false positive detection
- 📱 Mobile app testing
- 🌐 Multi-language support
- 📊 Advanced analytics dashboard
- 🔍 Fuzzing capabilities
- 🎯 Custom rule engine

---

**WebTestool v1.5.0** - Enterprise-grade testing with advanced features!
