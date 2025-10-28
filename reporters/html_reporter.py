"""HTML Report Generator"""

from core.models import ScanResult, Severity
from core.config import ConfigManager


class HTMLReporter:
    """Generate HTML format reports"""

    def __init__(self, config: ConfigManager):
        self.config = config

    def generate(self, scan_result: ScanResult, output_path: str) -> None:
        """Generate HTML report"""

        html = self._generate_html(scan_result)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def _generate_html(self, scan_result: ScanResult) -> str:
        """Generate HTML content"""

        findings = scan_result.get_all_findings()
        summary = scan_result.summary

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebTestool Security Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white;
                     box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  color: white; padding: 40px; }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                   gap: 20px; padding: 30px; background: #f9fafb; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px;
                     box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .stat-card h3 {{ color: #6b7280; font-size: 14px; margin-bottom: 10px; }}
        .stat-card .value {{ font-size: 32px; font-weight: bold; }}
        .critical {{ color: #dc2626; }}
        .high {{ color: #ea580c; }}
        .medium {{ color: #d97706; }}
        .low {{ color: #65a30d; }}
        .info {{ color: #0891b2; }}
        .findings {{ padding: 30px; }}
        .finding {{ border-left: 4px solid #e5e7eb; padding: 20px; margin-bottom: 20px;
                   background: #f9fafb; border-radius: 4px; }}
        .finding.critical {{ border-left-color: #dc2626; }}
        .finding.high {{ border-left-color: #ea580c; }}
        .finding.medium {{ border-left-color: #d97706; }}
        .finding.low {{ border-left-color: #65a30d; }}
        .finding h3 {{ margin-bottom: 10px; color: #111827; }}
        .finding .severity {{ display: inline-block; padding: 4px 12px; border-radius: 12px;
                            font-size: 12px; font-weight: 600; margin-bottom: 10px; }}
        .finding .url {{ color: #6b7280; font-size: 14px; margin-top: 10px; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 WebTestool Security Report</h1>
            <p>Target: {scan_result.target_url}</p>
            <p>Scan Date: {scan_result.start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Duration: {scan_result.duration:.2f} seconds</p>
        </div>

        <div class="summary">
            <div class="stat-card">
                <h3>URLs Crawled</h3>
                <div class="value">{summary.get('urls_crawled', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>Total Findings</h3>
                <div class="value">{summary.get('total_findings', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>Critical</h3>
                <div class="value critical">{summary.get('critical_findings', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>High</h3>
                <div class="value high">{summary.get('high_findings', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>Medium</h3>
                <div class="value medium">{summary.get('medium_findings', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>Low</h3>
                <div class="value low">{summary.get('low_findings', 0)}</div>
            </div>
        </div>

        <div class="findings">
            <h2 style="margin-bottom: 20px;">Findings</h2>
"""

        # Add findings grouped by severity
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            severity_findings = [f for f in findings if f.severity == severity]

            if severity_findings:
                html += f"<h3 style='margin: 20px 0; color: #374151;'>{severity.value.upper()} Severity ({len(severity_findings)})</h3>"

                for finding in severity_findings:
                    html += f"""
            <div class="finding {severity.value}">
                <span class="severity" style="background: {'#fee2e2' if severity == Severity.CRITICAL else '#ffedd5' if severity == Severity.HIGH else '#fef3c7' if severity == Severity.MEDIUM else '#ecfccb' if severity == Severity.LOW else '#cffafe'}; color: {'#991b1b' if severity == Severity.CRITICAL else '#9a3412' if severity == Severity.HIGH else '#92400e' if severity == Severity.MEDIUM else '#365314' if severity == Severity.LOW else '#164e63'};">
                    {severity.value.upper()}
                </span>
                <h3>{finding.title}</h3>
                <p>{finding.description}</p>
                {f'<div class="url">URL: {finding.url}</div>' if finding.url else ''}
                {f'<div style="margin-top: 10px; color: #6b7280; font-size: 13px;">CWE: {finding.cwe_id}</div>' if finding.cwe_id else ''}
            </div>
"""

        html += """
        </div>
    </div>
</body>
</html>
"""

        return html
