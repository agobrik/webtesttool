"""
PDF Report Generator
Professional PDF reports with charts, tables, and visualizations
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart

from loguru import logger

from core.exceptions import ReportGenerationError


class PDFReporter:
    """
    Professional PDF report generator

    Features:
    - Executive summary
    - Vulnerability tables
    - Security metrics charts
    - Performance graphs
    - Compliance status
    - Recommendations
    """

    # Color scheme
    COLORS = {
        'critical': colors.HexColor('#DC143C'),  # Crimson
        'high': colors.HexColor('#FF6347'),      # Tomato
        'medium': colors.HexColor('#FFA500'),    # Orange
        'low': colors.HexColor('#FFD700'),       # Gold
        'info': colors.HexColor('#87CEEB'),      # SkyBlue
        'pass': colors.HexColor('#32CD32'),      # LimeGreen
        'primary': colors.HexColor('#2E4053'),   # Dark blue-grey
        'secondary': colors.HexColor('#5D6D7E'), # Medium grey
    }

    def __init__(
        self,
        output_dir: str = "reports",
        page_size=letter,
        include_charts: bool = True
    ):
        """
        Initialize PDF reporter

        Args:
            output_dir: Directory for PDF reports
            page_size: Page size (letter or A4)
            include_charts: Include charts and graphs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.page_size = page_size
        self.include_charts = include_charts

        # Styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.COLORS['primary'],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.COLORS['secondary'],
            spaceAfter=20,
            alignment=TA_CENTER
        ))

        # Section Header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.COLORS['primary'],
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Subsection Header
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=self.COLORS['secondary'],
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))

        # Body
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))

    def generate(
        self,
        scan_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Generate PDF report

        Args:
            scan_data: Scan results data
            filename: Output filename (optional)

        Returns:
            Path to generated PDF file
        """
        try:
            # Generate filename
            if not filename:
                from urllib.parse import urlparse

                # Extract site name from URL
                target_url = scan_data.get('target', 'unknown-site')
                try:
                    parsed_url = urlparse(target_url)
                    site_name = parsed_url.netloc.replace(':', '-').replace('.', '-')
                    if not site_name:
                        site_name = "unknown-site"
                except:
                    site_name = "unknown-site"

                # Determine test type from vulnerabilities
                vulns = scan_data.get('vulnerabilities', [])
                if vulns:
                    test_types = set()
                    for v in vulns[:10]:  # Sample first 10
                        vtype = v.get('type', 'test')
                        test_types.add(vtype)
                    test_name = '-'.join(sorted(list(test_types))[:3])
                else:
                    test_name = "fullscan"

                # Create timestamp
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

                # Create filename: site-test-datetime.pdf
                filename = f"{site_name}-{test_name}-{timestamp}.pdf"

            filepath = self.output_dir / filename

            # Create PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=self.page_size,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1*inch,
                bottomMargin=1*inch
            )

            # Build content
            story = []

            # Cover page
            story.extend(self._create_cover_page(scan_data))
            story.append(PageBreak())

            # Executive summary
            story.extend(self._create_executive_summary(scan_data))
            story.append(PageBreak())

            # Security overview
            if 'security' in scan_data:
                story.extend(self._create_security_section(scan_data['security']))
                story.append(PageBreak())

            # Vulnerabilities
            if 'vulnerabilities' in scan_data:
                story.extend(self._create_vulnerabilities_section(scan_data['vulnerabilities']))
                story.append(PageBreak())

            # Performance
            if 'performance' in scan_data:
                story.extend(self._create_performance_section(scan_data['performance']))
                story.append(PageBreak())

            # Recommendations
            if 'recommendations' in scan_data:
                story.extend(self._create_recommendations_section(scan_data['recommendations']))

            # Build PDF
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)

            logger.info(f"PDF report generated: {filepath}")
            return str(filepath)

        except Exception as e:
            raise ReportGenerationError(
                f"Failed to generate PDF report: {str(e)}",
                details={'filename': filename},
                original_error=e
            )

    def _create_cover_page(self, scan_data: Dict) -> List:
        """Create cover page"""
        elements = []

        # Title
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph("Security Scan Report", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.5*inch))

        # Target info
        target = scan_data.get('target', 'Unknown')
        elements.append(Paragraph(f"Target: <b>{target}</b>", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.3*inch))

        # Date
        date = scan_data.get('date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        elements.append(Paragraph(f"Scan Date: {date}", self.styles['CustomBody']))
        elements.append(Spacer(1, 1*inch))

        # Summary stats table
        if 'summary' in scan_data:
            summary_data = [
                ['Metric', 'Value'],
                ['Total Pages Scanned', str(scan_data['summary'].get('pages_scanned', 0))],
                ['Critical Issues', str(scan_data['summary'].get('critical', 0))],
                ['High Issues', str(scan_data['summary'].get('high', 0))],
                ['Medium Issues', str(scan_data['summary'].get('medium', 0))],
                ['Low Issues', str(scan_data['summary'].get('low', 0))],
            ]

            table = Table(summary_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(table)

        return elements

    def _create_executive_summary(self, scan_data: Dict) -> List:
        """Create executive summary section"""
        elements = []

        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=self.COLORS['primary']))
        elements.append(Spacer(1, 0.2*inch))

        summary = scan_data.get('summary', {})

        # Overview text
        overview = f"""
        This security scan was performed on {scan_data.get('target', 'the target application')}
        on {scan_data.get('date', 'N/A')}. The scan covered {summary.get('pages_scanned', 0)} pages
        and identified a total of {summary.get('total_issues', 0)} security issues.
        """
        elements.append(Paragraph(overview, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))

        # Severity breakdown chart
        if self.include_charts and summary:
            chart_drawing = self._create_severity_pie_chart(summary)
            if chart_drawing:
                elements.append(chart_drawing)
                elements.append(Spacer(1, 0.3*inch))

        # Key findings
        elements.append(Paragraph("Key Findings:", self.styles['SubsectionHeader']))

        findings = scan_data.get('key_findings', [
            f"Found {summary.get('critical', 0)} critical vulnerabilities requiring immediate attention",
            f"Identified {summary.get('high', 0)} high-severity issues",
            f"Detected {summary.get('medium', 0)} medium-severity concerns",
        ])

        for finding in findings:
            elements.append(Paragraph(f"• {finding}", self.styles['CustomBody']))

        return elements

    def _create_security_section(self, security_data: Dict) -> List:
        """Create security overview section"""
        elements = []

        elements.append(Paragraph("Security Overview", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=self.COLORS['primary']))
        elements.append(Spacer(1, 0.2*inch))

        # Security score
        score = security_data.get('score', 0)
        score_text = f"<b>Overall Security Score: {score}/100</b>"
        elements.append(Paragraph(score_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))

        # Tests performed
        tests = security_data.get('tests_performed', [])
        if tests:
            elements.append(Paragraph("Tests Performed:", self.styles['SubsectionHeader']))

            test_data = [['Test Name', 'Status', 'Issues Found']]
            for test in tests:
                test_data.append([
                    test.get('name', ''),
                    test.get('status', ''),
                    str(test.get('issues', 0))
                ])

            table = Table(test_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))

            elements.append(table)

        return elements

    def _create_vulnerabilities_section(self, vulnerabilities: List[Dict]) -> List:
        """Create vulnerabilities section"""
        elements = []

        elements.append(Paragraph("Vulnerabilities", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=self.COLORS['primary']))
        elements.append(Spacer(1, 0.2*inch))

        # Group by severity
        by_severity = {
            'Critical': [],
            'High': [],
            'Medium': [],
            'Low': []
        }

        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'Low')
            by_severity[severity].append(vuln)

        # Display each severity group
        for severity in ['Critical', 'High', 'Medium', 'Low']:
            vulns = by_severity[severity]
            if not vulns:
                continue

            # Severity header
            color = self.COLORS.get(severity.lower(), colors.gray)
            elements.append(Paragraph(
                f"{severity} Severity ({len(vulns)} issues)",
                self.styles['SubsectionHeader']
            ))

            # Vulnerability table
            vuln_data = [['ID', 'Type', 'Description', 'Location']]

            for i, vuln in enumerate(vulns, 1):
                vuln_data.append([
                    str(i),
                    vuln.get('type', 'Unknown'),
                    vuln.get('description', '')[:50] + '...',
                    vuln.get('location', '')[:30]
                ])

            table = Table(vuln_data, colWidths=[0.5*inch, 1.5*inch, 2.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_performance_section(self, performance_data: Dict) -> List:
        """Create performance section"""
        elements = []

        elements.append(Paragraph("Performance Analysis", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=self.COLORS['primary']))
        elements.append(Spacer(1, 0.2*inch))

        # Performance metrics
        metrics = performance_data.get('metrics', {})

        metrics_data = [['Metric', 'Value', 'Status']]
        metrics_data.append(['Average Response Time', f"{metrics.get('avg_response_time', 0)}ms", 'Good'])
        metrics_data.append(['Page Load Time', f"{metrics.get('page_load_time', 0)}ms", 'Good'])
        metrics_data.append(['Total Requests', str(metrics.get('total_requests', 0)), 'N/A'])

        table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)

        return elements

    def _create_recommendations_section(self, recommendations: List[Dict]) -> List:
        """Create recommendations section"""
        elements = []

        elements.append(Paragraph("Recommendations", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=self.COLORS['primary']))
        elements.append(Spacer(1, 0.2*inch))

        for i, rec in enumerate(recommendations, 1):
            priority = rec.get('priority', 'Medium')
            title = rec.get('title', f'Recommendation {i}')
            description = rec.get('description', '')

            # Priority badge
            color = self.COLORS.get(priority.lower(), colors.gray)

            elements.append(Paragraph(
                f"<b>{i}. [{priority}] {title}</b>",
                self.styles['SubsectionHeader']
            ))
            elements.append(Paragraph(description, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_severity_pie_chart(self, summary: Dict) -> Optional[Drawing]:
        """Create pie chart for severity distribution"""
        try:
            data = [
                summary.get('critical', 0),
                summary.get('high', 0),
                summary.get('medium', 0),
                summary.get('low', 0)
            ]

            # Only create chart if there's data
            if sum(data) == 0:
                return None

            drawing = Drawing(400, 200)
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 100
            pie.height = 100
            pie.data = data
            pie.labels = ['Critical', 'High', 'Medium', 'Low']
            pie.slices.strokeWidth = 0.5

            # Colors
            pie.slices[0].fillColor = self.COLORS['critical']
            pie.slices[1].fillColor = self.COLORS['high']
            pie.slices[2].fillColor = self.COLORS['medium']
            pie.slices[3].fillColor = self.COLORS['low']

            drawing.add(pie)
            return drawing

        except Exception as e:
            logger.warning(f"Failed to create pie chart: {e}")
            return None

    def _add_page_number(self, canvas, doc):
        """Add page number to each page"""
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(7.5*inch, 0.5*inch, text)
        canvas.restoreState()


# Convenience function

def generate_pdf_report(
    scan_data: Dict[str, Any],
    output_dir: str = "reports",
    filename: Optional[str] = None
) -> str:
    """
    Generate PDF report (convenience function)

    Args:
        scan_data: Scan results data
        output_dir: Output directory
        filename: Output filename

    Returns:
        Path to generated PDF
    """
    reporter = PDFReporter(output_dir=output_dir)
    return reporter.generate(scan_data, filename)
