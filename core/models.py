"""
Data models for test results, findings, and reports
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Severity levels for findings"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class TestStatus(str, Enum):
    """Status of a test execution"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class Category(str, Enum):
    """Test category"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    FUNCTIONAL = "functional"
    API = "api"
    COMPATIBILITY = "compatibility"
    ACCESSIBILITY = "accessibility"
    SEO = "seo"
    INFRASTRUCTURE = "infrastructure"
    VISUAL = "visual"
    DATA = "data"
    BUSINESS_LOGIC = "business_logic"


class Evidence(BaseModel):
    """Evidence for a finding"""
    type: str  # screenshot, code, request, response, etc.
    data: Any
    description: Optional[str] = None


class Recommendation(BaseModel):
    """Recommendation for fixing an issue"""
    title: str
    description: str
    references: List[str] = Field(default_factory=list)
    code_example: Optional[str] = None


class Finding(BaseModel):
    """A single test finding/issue"""
    id: str = Field(default_factory=lambda: f"finding_{datetime.now().timestamp()}")
    title: str
    description: str
    severity: Severity
    category: Category
    url: Optional[str] = None
    method: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    evidence: List[Evidence] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    cvss_score: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TestResult(BaseModel):
    """Result of a single test"""
    id: str = Field(default_factory=lambda: f"test_{datetime.now().timestamp()}")
    name: str
    description: str
    category: Category
    status: TestStatus
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: Optional[float] = None  # seconds
    findings: List[Finding] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None

    def add_finding(self, finding: Finding) -> None:
        """Add a finding to this test result"""
        self.findings.append(finding)

    def mark_completed(self, status: TestStatus) -> None:
        """Mark test as completed"""
        self.status = status
        self.end_time = datetime.now()
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()


class ModuleResult(BaseModel):
    """Result of a test module execution"""
    id: str = Field(default_factory=lambda: f"module_{datetime.now().timestamp()}")
    name: str
    category: Category
    status: TestStatus
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    test_results: List[TestResult] = Field(default_factory=list)
    summary: Dict[str, int] = Field(default_factory=dict)

    def add_test_result(self, test_result: TestResult) -> None:
        """Add a test result to this module"""
        self.test_results.append(test_result)

    @property
    def findings(self) -> List['Finding']:
        """Get all findings from all test results in this module"""
        all_findings = []
        for test_result in self.test_results:
            all_findings.extend(test_result.findings)
        return all_findings

    def mark_completed(self, status: TestStatus) -> None:
        """Mark module as completed"""
        self.status = status
        self.end_time = datetime.now()
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()

        # Calculate summary
        self.summary = {
            "total_tests": len(self.test_results),
            "passed": sum(1 for t in self.test_results if t.status == TestStatus.PASSED),
            "failed": sum(1 for t in self.test_results if t.status == TestStatus.FAILED),
            "error": sum(1 for t in self.test_results if t.status == TestStatus.ERROR),
            "skipped": sum(1 for t in self.test_results if t.status == TestStatus.SKIPPED),
            "total_findings": sum(len(t.findings) for t in self.test_results),
            "critical": sum(1 for t in self.test_results for f in t.findings if f.severity == Severity.CRITICAL),
            "high": sum(1 for t in self.test_results for f in t.findings if f.severity == Severity.HIGH),
            "medium": sum(1 for t in self.test_results for f in t.findings if f.severity == Severity.MEDIUM),
            "low": sum(1 for t in self.test_results for f in t.findings if f.severity == Severity.LOW),
            "info": sum(1 for t in self.test_results for f in t.findings if f.severity == Severity.INFO),
        }


class ScanResult(BaseModel):
    """Complete scan result"""
    id: str = Field(default_factory=lambda: f"scan_{datetime.now().timestamp()}")
    target_url: str
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: TestStatus = TestStatus.RUNNING
    module_results: List[ModuleResult] = Field(default_factory=list)
    crawled_urls: List[str] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)

    def add_module_result(self, module_result: ModuleResult) -> None:
        """Add a module result"""
        self.module_results.append(module_result)

    def mark_completed(self, status: TestStatus) -> None:
        """Mark scan as completed"""
        self.status = status
        self.end_time = datetime.now()
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()

        # Calculate overall summary
        total_findings = sum(m.summary.get("total_findings", 0) for m in self.module_results)

        self.summary = {
            "total_modules": len(self.module_results),
            "total_tests": sum(m.summary.get("total_tests", 0) for m in self.module_results),
            "total_findings": total_findings,
            "critical_findings": sum(m.summary.get("critical", 0) for m in self.module_results),
            "high_findings": sum(m.summary.get("high", 0) for m in self.module_results),
            "medium_findings": sum(m.summary.get("medium", 0) for m in self.module_results),
            "low_findings": sum(m.summary.get("low", 0) for m in self.module_results),
            "info_findings": sum(m.summary.get("info", 0) for m in self.module_results),
            "urls_crawled": len(self.crawled_urls),
            "duration_seconds": self.duration,
        }

    def get_all_findings(self) -> List[Finding]:
        """Get all findings from all modules"""
        findings = []
        for module_result in self.module_results:
            for test_result in module_result.test_results:
                findings.extend(test_result.findings)
        return findings

    def get_findings_by_severity(self, severity: Severity) -> List[Finding]:
        """Get findings filtered by severity"""
        return [f for f in self.get_all_findings() if f.severity == severity]

    def get_findings_by_category(self, category: Category) -> List[Finding]:
        """Get findings filtered by category"""
        return [f for f in self.get_all_findings() if f.category == category]


class CrawledPage(BaseModel):
    """Information about a crawled page"""
    url: str
    status_code: int
    content_type: Optional[str] = None
    title: Optional[str] = None
    depth: int = 0
    parent_url: Optional[str] = None
    forms: List[Dict[str, Any]] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list)
    inputs: List[Dict[str, Any]] = Field(default_factory=list)
    scripts: List[str] = Field(default_factory=list)
    stylesheets: List[str] = Field(default_factory=list)
    meta_tags: Dict[str, str] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    cookies: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    response_time: Optional[float] = None
    size_bytes: Optional[int] = None


class ApiEndpoint(BaseModel):
    """Discovered API endpoint"""
    url: str
    method: str
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    headers: Dict[str, str] = Field(default_factory=dict)
    response_type: Optional[str] = None
    authentication_required: bool = False
    discovered_from: Optional[str] = None


class TestContext(BaseModel):
    """Context information passed to test modules"""
    target_url: str
    base_url: str
    crawled_pages: List[CrawledPage] = Field(default_factory=list)
    api_endpoints: List[ApiEndpoint] = Field(default_factory=list)
    cookies: Dict[str, str] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    auth_token: Optional[str] = None
    session_data: Dict[str, Any] = Field(default_factory=dict)
