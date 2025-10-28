"""
Metrics Collection for WebTestool
Collects and exposes metrics for monitoring
"""

from typing import Dict, Optional
from datetime import datetime
import time
from collections import defaultdict
from threading import Lock

from loguru import logger


class MetricsCollector:
    """
    Collect and expose application metrics

    Metrics:
    - Scan counts (total, success, failure)
    - Finding counts by severity
    - Scan duration statistics
    - Module execution times
    - Cache hit rates
    - Error counts
    """

    def __init__(self):
        self._lock = Lock()

        # Counters
        self.scans_total = 0
        self.scans_success = 0
        self.scans_failure = 0

        self.findings_by_severity = defaultdict(int)
        self.modules_executed = defaultdict(int)
        self.errors = defaultdict(int)

        # Gauges
        self.active_scans = 0
        self.cache_hit_rate = 0.0

        # Histograms (stored as lists for now)
        self.scan_durations = []
        self.module_durations = defaultdict(list)

        # Timestamps
        self.start_time = time.time()
        self.last_scan_time: Optional[float] = None

    def record_scan_start(self):
        """Record that a scan has started"""
        with self._lock:
            self.scans_total += 1
            self.active_scans += 1
            self.last_scan_time = time.time()

        logger.debug(f"Metrics: Scan started (total: {self.scans_total})")

    def record_scan_end(self, duration: float, success: bool = True):
        """
        Record scan completion

        Args:
            duration: Scan duration in seconds
            success: Whether scan completed successfully
        """
        with self._lock:
            self.active_scans = max(0, self.active_scans - 1)

            if success:
                self.scans_success += 1
            else:
                self.scans_failure += 1

            self.scan_durations.append(duration)

            # Keep only last 1000 durations
            if len(self.scan_durations) > 1000:
                self.scan_durations = self.scan_durations[-1000:]

        logger.debug(f"Metrics: Scan completed in {duration:.2f}s (success: {success})")

    def record_finding(self, severity: str):
        """
        Record a security finding

        Args:
            severity: Finding severity (critical, high, medium, low, info)
        """
        with self._lock:
            self.findings_by_severity[severity.lower()] += 1

        logger.debug(f"Metrics: Finding recorded ({severity})")

    def record_module_execution(self, module_name: str, duration: float):
        """
        Record module execution

        Args:
            module_name: Name of the module
            duration: Execution duration in seconds
        """
        with self._lock:
            self.modules_executed[module_name] += 1
            self.module_durations[module_name].append(duration)

            # Keep only last 100 durations per module
            if len(self.module_durations[module_name]) > 100:
                self.module_durations[module_name] = self.module_durations[module_name][-100:]

        logger.debug(f"Metrics: Module '{module_name}' executed in {duration:.2f}s")

    def record_error(self, error_type: str):
        """
        Record an error

        Args:
            error_type: Type of error
        """
        with self._lock:
            self.errors[error_type] += 1

        logger.debug(f"Metrics: Error recorded ({error_type})")

    def update_cache_metrics(self, hit_rate: float):
        """
        Update cache metrics

        Args:
            hit_rate: Cache hit rate (0.0 to 1.0)
        """
        with self._lock:
            self.cache_hit_rate = hit_rate

    def get_all_metrics(self) -> Dict:
        """
        Get all metrics as dictionary

        Returns:
            Dictionary containing all metrics
        """
        with self._lock:
            uptime = time.time() - self.start_time

            # Calculate statistics
            avg_scan_duration = (
                sum(self.scan_durations) / len(self.scan_durations)
                if self.scan_durations else 0
            )

            max_scan_duration = max(self.scan_durations) if self.scan_durations else 0
            min_scan_duration = min(self.scan_durations) if self.scan_durations else 0

            return {
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': uptime,
                'scans': {
                    'total': self.scans_total,
                    'success': self.scans_success,
                    'failure': self.scans_failure,
                    'active': self.active_scans,
                    'success_rate': (
                        self.scans_success / self.scans_total * 100
                        if self.scans_total > 0 else 0
                    )
                },
                'scan_durations': {
                    'average_seconds': avg_scan_duration,
                    'max_seconds': max_scan_duration,
                    'min_seconds': min_scan_duration,
                    'count': len(self.scan_durations)
                },
                'findings': {
                    'by_severity': dict(self.findings_by_severity),
                    'total': sum(self.findings_by_severity.values())
                },
                'modules': {
                    'executed': dict(self.modules_executed),
                    'total_executions': sum(self.modules_executed.values())
                },
                'cache': {
                    'hit_rate_percent': self.cache_hit_rate * 100
                },
                'errors': {
                    'by_type': dict(self.errors),
                    'total': sum(self.errors.values())
                }
            }

    def get_metrics(self) -> str:
        """
        Get metrics in Prometheus format

        Returns:
            Metrics in Prometheus text format
        """
        metrics = self.get_all_metrics()

        lines = [
            "# HELP webtestool_scans_total Total number of scans",
            "# TYPE webtestool_scans_total counter",
            f"webtestool_scans_total {metrics['scans']['total']}",
            "",
            "# HELP webtestool_scans_success Number of successful scans",
            "# TYPE webtestool_scans_success counter",
            f"webtestool_scans_success {metrics['scans']['success']}",
            "",
            "# HELP webtestool_scans_failure Number of failed scans",
            "# TYPE webtestool_scans_failure counter",
            f"webtestool_scans_failure {metrics['scans']['failure']}",
            "",
            "# HELP webtestool_active_scans Number of currently active scans",
            "# TYPE webtestool_active_scans gauge",
            f"webtestool_active_scans {metrics['scans']['active']}",
            "",
            "# HELP webtestool_scan_duration_seconds Scan duration statistics",
            "# TYPE webtestool_scan_duration_seconds summary",
            f"webtestool_scan_duration_seconds_sum {sum(self.scan_durations)}",
            f"webtestool_scan_duration_seconds_count {len(self.scan_durations)}",
            "",
            "# HELP webtestool_findings_total Total findings by severity",
            "# TYPE webtestool_findings_total counter"
        ]

        # Add findings by severity
        for severity, count in metrics['findings']['by_severity'].items():
            lines.append(f'webtestool_findings_total{{severity="{severity}"}} {count}')

        lines.append("")
        lines.append("# HELP webtestool_cache_hit_rate Cache hit rate")
        lines.append("# TYPE webtestool_cache_hit_rate gauge")
        lines.append(f"webtestool_cache_hit_rate {metrics['cache']['hit_rate_percent'] / 100}")

        lines.append("")
        lines.append("# HELP webtestool_errors_total Total errors by type")
        lines.append("# TYPE webtestool_errors_total counter")

        # Add errors by type
        for error_type, count in metrics['errors']['by_type'].items():
            lines.append(f'webtestool_errors_total{{type="{error_type}"}} {count}')

        return "\n".join(lines)

    def reset(self):
        """Reset all metrics"""
        with self._lock:
            self.scans_total = 0
            self.scans_success = 0
            self.scans_failure = 0
            self.findings_by_severity.clear()
            self.modules_executed.clear()
            self.errors.clear()
            self.active_scans = 0
            self.cache_hit_rate = 0.0
            self.scan_durations.clear()
            self.module_durations.clear()
            self.start_time = time.time()

        logger.info("Metrics reset")

    def print_summary(self):
        """Print metrics summary"""
        metrics = self.get_all_metrics()

        print("\n" + "="*60)
        print("METRICS SUMMARY")
        print("="*60)

        print(f"\n⏱️  Uptime: {metrics['uptime_seconds']:.0f}s")

        print(f"\n📊 Scans:")
        print(f"  Total: {metrics['scans']['total']}")
        print(f"  Success: {metrics['scans']['success']}")
        print(f"  Failure: {metrics['scans']['failure']}")
        print(f"  Active: {metrics['scans']['active']}")
        print(f"  Success Rate: {metrics['scans']['success_rate']:.1f}%")

        print(f"\n🔍 Findings: {metrics['findings']['total']}")
        for severity, count in metrics['findings']['by_severity'].items():
            print(f"  {severity.capitalize()}: {count}")

        print(f"\n💾 Cache Hit Rate: {metrics['cache']['hit_rate_percent']:.1f}%")

        if metrics['errors']['total'] > 0:
            print(f"\n❌ Errors: {metrics['errors']['total']}")
            for error_type, count in metrics['errors']['by_type'].items():
                print(f"  {error_type}: {count}")

        print("="*60 + "\n")


# Global singleton
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """
    Get or create metrics collector singleton

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector

    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()

    return _metrics_collector
