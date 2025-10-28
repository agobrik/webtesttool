"""JSON Report Generator"""

import json
from core.models import ScanResult
from core.config import ConfigManager


class JSONReporter:
    """Generate JSON format reports"""

    def __init__(self, config: ConfigManager):
        self.config = config

    def generate(self, scan_result: ScanResult, output_path: str) -> None:
        """Generate JSON report"""

        # Convert to dict and save
        report_data = scan_result.model_dump()

        pretty_print = self.config.config.reporting.formats.get('json', {}).get('pretty_print', True)

        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty_print:
                json.dump(report_data, f, indent=2, default=str)
            else:
                json.dump(report_data, f, default=str)
