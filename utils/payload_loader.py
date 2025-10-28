"""Payload loading utilities"""

import os
from pathlib import Path
from typing import List


class PayloadLoader:
    """Load test payloads from files"""

    def __init__(self, payloads_dir: str = None):
        """
        Initialize PayloadLoader

        Args:
            payloads_dir: Directory containing payload files
        """
        if payloads_dir is None:
            self.payloads_dir = Path(__file__).parent.parent / "payloads"
        else:
            self.payloads_dir = Path(payloads_dir)

    def load_payloads(self, filename: str) -> List[str]:
        """
        Load payloads from file

        Args:
            filename: Payload filename (e.g., 'sqli.txt')

        Returns:
            List of payload strings
        """
        filepath = self.payloads_dir / filename

        if not filepath.exists():
            return []

        with open(filepath, 'r', encoding='utf-8') as f:
            payloads = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        return payloads

    def load_sqli_payloads(self) -> List[str]:
        """Load SQL injection payloads"""
        return self.load_payloads('sqli.txt')

    def load_xss_payloads(self) -> List[str]:
        """Load XSS payloads"""
        return self.load_payloads('xss.txt')

    def load_lfi_payloads(self) -> List[str]:
        """Load LFI/Path traversal payloads"""
        return self.load_payloads('lfi.txt')

    def get_custom_payloads(self, test_type: str) -> List[str]:
        """
        Get custom payloads for a test type

        Args:
            test_type: Type of test (sqli, xss, lfi, etc.)

        Returns:
            List of payloads
        """
        return self.load_payloads(f'{test_type}.txt')
