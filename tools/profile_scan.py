"""
Performance Profiling Tool for WebTestool
Detects bottlenecks and performance issues
"""

import cProfile
import pstats
import asyncio
import sys
import time
import tracemalloc
from pathlib import Path
from io import StringIO
from typing import Dict, List, Tuple
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import ConfigManager, TestEngine
from loguru import logger


class PerformanceProfiler:
    """Comprehensive performance profiling"""

    def __init__(self):
        self.results = {}
        self.profiler = cProfile.Profile()

    async def profile_full_scan(
        self,
        target_url: str,
        max_pages: int = 10,
        profile: str = 'quick'
    ) -> Dict:
        """
        Profile a complete scan

        Args:
            target_url: Target URL to scan
            max_pages: Maximum pages to crawl
            profile: Scan profile (quick, security, full)

        Returns:
            Dictionary with profiling results
        """
        logger.info(f"Starting profiling for {target_url}")
        logger.info(f"Profile: {profile}, Max pages: {max_pages}")

        # Configure
        config = ConfigManager()
        config.set('target.url', target_url)
        config.set('crawler.max_pages', max_pages)
        config.set('crawler.enabled', True)

        # Set profile
        if profile == 'quick':
            config.set('modules.security.enabled', True)
            config.set('modules.performance.enabled', False)
            config.set('modules.seo.enabled', False)
        elif profile == 'security':
            config.set('modules.security.enabled', True)
            config.set('modules.performance.enabled', False)

        # Start memory tracking
        tracemalloc.start()

        # Create engine
        engine = TestEngine(config)

        # Profile execution
        self.profiler.enable()
        start_time = time.time()

        try:
            result = await engine.run()

            end_time = time.time()
            self.profiler.disable()

            # Get memory stats
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Analyze results
            duration = end_time - start_time

            profiling_results = {
                'target_url': target_url,
                'profile': profile,
                'timestamp': datetime.now().isoformat(),
                'duration': {
                    'total_seconds': duration,
                    'formatted': f"{duration:.2f}s"
                },
                'memory': {
                    'current_mb': current / 1024 / 1024,
                    'peak_mb': peak / 1024 / 1024
                },
                'scan_stats': {
                    'urls_crawled': len(result.crawled_urls),
                    'modules_executed': len(result.module_results),
                    'total_findings': result.summary.get('total_findings', 0)
                },
                'performance_stats': self._analyze_performance(),
                'bottlenecks': self._identify_bottlenecks()
            }

            logger.info(f"Profiling completed in {duration:.2f}s")
            logger.info(f"Peak memory: {peak / 1024 / 1024:.2f} MB")

            return profiling_results

        except Exception as e:
            logger.error(f"Profiling failed: {e}")
            self.profiler.disable()
            tracemalloc.stop()
            raise

    def _analyze_performance(self) -> Dict:
        """Analyze performance statistics"""
        stats = pstats.Stats(self.profiler)
        stats.sort_stats('cumulative')

        # Capture stats
        stream = StringIO()
        stats.stream = stream
        stats.print_stats(20)  # Top 20 functions

        output = stream.getvalue()

        # Parse top functions
        top_functions = []
        for line in output.split('\n')[5:25]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 6:
                    top_functions.append({
                        'ncalls': parts[0],
                        'tottime': parts[1],
                        'percall': parts[2],
                        'cumtime': parts[3],
                        'function': ' '.join(parts[5:])
                    })

        return {
            'top_functions': top_functions,
            'stats_available': True
        }

    def _identify_bottlenecks(self) -> List[Dict]:
        """Identify performance bottlenecks"""
        stats = pstats.Stats(self.profiler)
        stats.sort_stats('cumulative')

        bottlenecks = []

        # Get top time-consuming functions
        for func, (cc, nc, tt, ct, callers) in list(stats.stats.items())[:10]:
            if ct > 0.1:  # Functions taking more than 0.1s
                bottlenecks.append({
                    'function': f"{func[0]}:{func[1]}:{func[2]}",
                    'cumulative_time': ct,
                    'calls': nc,
                    'time_per_call': ct / nc if nc > 0 else 0,
                    'severity': self._classify_severity(ct)
                })

        return sorted(bottlenecks, key=lambda x: x['cumulative_time'], reverse=True)

    def _classify_severity(self, time: float) -> str:
        """Classify bottleneck severity"""
        if time > 5.0:
            return 'CRITICAL'
        elif time > 2.0:
            return 'HIGH'
        elif time > 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'

    def save_results(self, results: Dict, output_file: str = 'profiling_results.json'):
        """Save profiling results to file"""
        output_path = Path('reports') / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to {output_path}")

    def print_summary(self, results: Dict):
        """Print profiling summary"""
        print("\n" + "="*80)
        print("PERFORMANCE PROFILING SUMMARY")
        print("="*80)

        print(f"\n🎯 Target: {results['target_url']}")
        print(f"⏱️  Duration: {results['duration']['formatted']}")
        print(f"💾 Peak Memory: {results['memory']['peak_mb']:.2f} MB")

        print(f"\n📊 Scan Statistics:")
        stats = results['scan_stats']
        print(f"  URLs Crawled: {stats['urls_crawled']}")
        print(f"  Modules Executed: {stats['modules_executed']}")
        print(f"  Findings: {stats['total_findings']}")

        print(f"\n🔥 Top Bottlenecks:")
        for i, bottleneck in enumerate(results['bottlenecks'][:5], 1):
            print(f"  {i}. [{bottleneck['severity']}] {bottleneck['function']}")
            print(f"     Time: {bottleneck['cumulative_time']:.3f}s "
                  f"({bottleneck['calls']} calls)")

        print("\n" + "="*80)


class BottleneckDetector:
    """Detect specific bottlenecks"""

    @staticmethod
    async def detect_slow_operations() -> List[Dict]:
        """Detect slow operations in the codebase"""
        bottlenecks = []

        # Test crawler speed
        from core import ConfigManager
        from core.scanner import WebScanner

        config = ConfigManager()
        config.set('target.url', 'https://example.com')
        config.set('crawler.max_pages', 5)

        scanner = WebScanner(config)

        start = time.time()
        pages, apis = await scanner.scan()
        duration = time.time() - start

        if duration > 10:
            bottlenecks.append({
                'component': 'WebScanner',
                'operation': 'scan',
                'duration': duration,
                'severity': 'HIGH',
                'recommendation': 'Consider parallel crawling or caching'
            })

        return bottlenecks


async def main():
    """Main profiling entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Profile WebTestool performance')
    parser.add_argument('--url', required=True, help='Target URL')
    parser.add_argument('--pages', type=int, default=10, help='Max pages to crawl')
    parser.add_argument('--profile', default='quick',
                       choices=['quick', 'security', 'full'],
                       help='Scan profile')
    parser.add_argument('--output', default='profiling_results.json',
                       help='Output file')

    args = parser.parse_args()

    # Run profiling
    profiler = PerformanceProfiler()

    print(f"\n🔬 Starting performance profiling...")
    print(f"Target: {args.url}")
    print(f"Profile: {args.profile}")
    print(f"Max pages: {args.pages}\n")

    results = await profiler.profile_full_scan(
        target_url=args.url,
        max_pages=args.pages,
        profile=args.profile
    )

    # Save results
    profiler.save_results(results, args.output)

    # Print summary
    profiler.print_summary(results)

    # Detect bottlenecks
    print("\n🔍 Detecting bottlenecks...")
    detector = BottleneckDetector()
    bottlenecks = await detector.detect_slow_operations()

    if bottlenecks:
        print("\n⚠️  Additional Bottlenecks Detected:")
        for bottleneck in bottlenecks:
            print(f"\n  Component: {bottleneck['component']}")
            print(f"  Operation: {bottleneck['operation']}")
            print(f"  Duration: {bottleneck['duration']:.2f}s")
            print(f"  Severity: {bottleneck['severity']}")
            print(f"  💡 {bottleneck['recommendation']}")

    print("\n✅ Profiling complete!")


if __name__ == '__main__':
    asyncio.run(main())
