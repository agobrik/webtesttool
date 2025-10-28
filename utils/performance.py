"""
Performance monitoring and profiling utilities
"""

import time
import functools
import asyncio
from typing import Callable, Any, Dict
from contextlib import contextmanager
from loguru import logger
import psutil
import os


class PerformanceMonitor:
    """Monitor and track performance metrics"""

    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.process = psutil.Process(os.getpid())

    def record_metric(self, name: str, value: float):
        """Record a performance metric"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

    def get_average(self, name: str) -> float:
        """Get average value for a metric"""
        if name not in self.metrics or not self.metrics[name]:
            return 0.0
        return sum(self.metrics[name]) / len(self.metrics[name])

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage in MB"""
        mem_info = self.process.memory_info()
        return {
            'rss': mem_info.rss / 1024 / 1024,  # Resident Set Size in MB
            'vms': mem_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
            'percent': self.process.memory_percent()
        }

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return self.process.cpu_percent(interval=0.1)

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            'metrics': {
                name: {
                    'count': len(values),
                    'average': self.get_average(name),
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0
                }
                for name, values in self.metrics.items()
            },
            'memory': self.get_memory_usage(),
            'cpu': self.get_cpu_usage()
        }


# Global performance monitor
_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor"""
    return _monitor


@contextmanager
def measure_time(operation_name: str):
    """
    Context manager to measure execution time

    Example:
        with measure_time("database_query"):
            result = db.query(...)
    """
    start_time = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start_time
        _monitor.record_metric(f"{operation_name}_time", elapsed)
        logger.debug(f"{operation_name} took {elapsed:.3f}s")


def timeit(func: Callable) -> Callable:
    """
    Decorator to measure function execution time

    Example:
        @timeit
        def slow_function():
            time.sleep(1)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with measure_time(func.__name__):
            return func(*args, **kwargs)
    return wrapper


def async_timeit(func: Callable) -> Callable:
    """
    Decorator to measure async function execution time

    Example:
        @async_timeit
        async def slow_async_function():
            await asyncio.sleep(1)
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start_time
            _monitor.record_metric(f"{func.__name__}_time", elapsed)
            logger.debug(f"{func.__name__} took {elapsed:.3f}s")
    return wrapper


@contextmanager
def memory_profiler(operation_name: str):
    """
    Context manager to profile memory usage

    Example:
        with memory_profiler("data_processing"):
            large_data = process_data()
    """
    mem_before = _monitor.get_memory_usage()
    try:
        yield
    finally:
        mem_after = _monitor.get_memory_usage()
        mem_delta = mem_after['rss'] - mem_before['rss']
        _monitor.record_metric(f"{operation_name}_memory", mem_delta)
        logger.debug(
            f"{operation_name} memory delta: {mem_delta:.2f}MB "
            f"(total: {mem_after['rss']:.2f}MB)"
        )


class RateLimiter:
    """
    Token bucket rate limiter

    Example:
        limiter = RateLimiter(max_requests=100, window=60)
        if limiter.allow_request("user_123"):
            # Process request
            pass
        else:
            # Reject request
            raise RateLimitError()
    """

    def __init__(self, max_requests: int, window: int):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed
            window: Time window in seconds
        """
        self.max_requests = max_requests
        self.window = window
        self.requests: Dict[str, list] = {}

    def allow_request(self, key: str) -> bool:
        """Check if request is allowed"""
        now = time.time()

        # Initialize or clean old requests
        if key not in self.requests:
            self.requests[key] = []
        else:
            # Remove requests outside the window
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < self.window
            ]

        # Check if limit exceeded
        if len(self.requests[key]) >= self.max_requests:
            return False

        # Allow request
        self.requests[key].append(now)
        return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for key"""
        if key not in self.requests:
            return self.max_requests

        now = time.time()
        active_requests = [
            req_time for req_time in self.requests[key]
            if now - req_time < self.window
        ]
        return max(0, self.max_requests - len(active_requests))


class ProgressTracker:
    """
    Track progress of long-running operations

    Example:
        tracker = ProgressTracker(total=100)
        for i in range(100):
            # Do work
            tracker.update(1)
    """

    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()

    def update(self, amount: int = 1):
        """Update progress"""
        self.current += amount
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        elapsed = time.time() - self.start_time

        # Estimate remaining time
        if self.current > 0:
            rate = self.current / elapsed
            remaining = (self.total - self.current) / rate if rate > 0 else 0
            logger.info(
                f"{self.description}: {self.current}/{self.total} "
                f"({percentage:.1f}%) - ETA: {remaining:.0f}s"
            )

    def complete(self):
        """Mark as complete"""
        self.current = self.total
        elapsed = time.time() - self.start_time
        logger.info(
            f"{self.description}: Complete in {elapsed:.2f}s "
            f"(avg: {elapsed/self.total:.3f}s per item)"
        )
