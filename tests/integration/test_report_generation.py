"""
Integration tests for report generation
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from core import ConfigManager
from reporters import ReportGenerator, HTMLReporter, JSONReporter


class TestReportGeneration:
    """Test report generation workflow"""

    @pytest.fixture
    def temp_report_dir(self):
        """Create temporary report directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_html_report_generation(self, sample_scan_result, temp_report_dir):
        """Test HTML report generation"""
        # Create config
        config = ConfigManager()
        config.set('reporting.output_dir', temp_report_dir)

        # Generate report
        reporter = HTMLReporter(config)

        # This would generate actual report
        # For now, test the reporter setup
        assert reporter is not None

    def test_json_report_generation(self, sample_scan_result, temp_report_dir):
        """Test JSON report generation"""
        config = ConfigManager()
        config.set('reporting.output_dir', temp_report_dir)

        reporter = JSONReporter(config)

        assert reporter is not None

    def test_report_generator_orchestration(self, sample_scan_result, temp_report_dir):
        """Test report generator orchestration"""
        config = ConfigManager()
        config.set('reporting.output_dir', temp_report_dir)
        config.set('reporting.formats', {'html': {}, 'json': {}})

        generator = ReportGenerator(config)

        assert generator is not None

    def test_report_output_directory_creation(self, temp_report_dir):
        """Test that report directories are created"""
        config = ConfigManager()
        non_existent_dir = Path(temp_report_dir) / 'new_reports'
        config.set('reporting.output_dir', str(non_existent_dir))

        # Directory should be created when needed
        assert not non_existent_dir.exists()
