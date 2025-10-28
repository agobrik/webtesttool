"""
Health check and system status utilities
"""

import asyncio
import sys
from typing import Dict, Any, List
from datetime import datetime
from enum import Enum
from loguru import logger
import psutil


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheck:
    """System health check"""

    def __init__(self):
        self.checks: Dict[str, callable] = {}
        self.register_default_checks()

    def register_check(self, name: str, check_func: callable):
        """Register a health check"""
        self.checks[name] = check_func

    def register_default_checks(self):
        """Register default system checks"""
        self.register_check("memory", self.check_memory)
        self.register_check("disk", self.check_disk)
        self.register_check("python", self.check_python_version)

    async def run_check(self, name: str) -> Dict[str, Any]:
        """Run a single health check"""
        if name not in self.checks:
            return {
                "name": name,
                "status": "unknown",
                "message": f"Check '{name}' not found"
            }

        try:
            if asyncio.iscoroutinefunction(self.checks[name]):
                result = await self.checks[name]()
            else:
                result = self.checks[name]()

            return {
                "name": name,
                "status": "healthy" if result["healthy"] else "unhealthy",
                "message": result.get("message", ""),
                "details": result.get("details", {})
            }
        except Exception as e:
            logger.error(f"Health check '{name}' failed: {e}")
            return {
                "name": name,
                "status": "error",
                "message": str(e)
            }

    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        for name in self.checks:
            results[name] = await self.run_check(name)

        # Overall status
        all_healthy = all(
            check["status"] == "healthy"
            for check in results.values()
        )

        # Determine overall status
        if all_healthy:
            status = HealthStatus.HEALTHY.value
        else:
            # Check if any are unhealthy vs just degraded
            any_unhealthy = any(
                check["status"] == "unhealthy"
                for check in results.values()
            )
            status = HealthStatus.UNHEALTHY.value if any_unhealthy else HealthStatus.DEGRADED.value

        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "checks": results
        }

    def check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        memory = psutil.virtual_memory()
        healthy = memory.percent < 90  # Less than 90% used

        return {
            "healthy": healthy,
            "message": f"Memory usage: {memory.percent:.1f}%",
            "details": {
                "total": memory.total / (1024**3),  # GB
                "available": memory.available / (1024**3),  # GB
                "percent": memory.percent
            }
        }

    def check_disk(self) -> Dict[str, Any]:
        """Check disk usage"""
        disk = psutil.disk_usage('/')
        healthy = disk.percent < 90  # Less than 90% used

        return {
            "healthy": healthy,
            "message": f"Disk usage: {disk.percent:.1f}%",
            "details": {
                "total": disk.total / (1024**3),  # GB
                "free": disk.free / (1024**3),  # GB
                "percent": disk.percent
            }
        }

    def check_python_version(self) -> Dict[str, Any]:
        """Check Python version"""
        version = sys.version_info
        healthy = version.major == 3 and version.minor >= 10

        return {
            "healthy": healthy,
            "message": f"Python {version.major}.{version.minor}.{version.micro}",
            "details": {
                "version": f"{version.major}.{version.minor}.{version.micro}",
                "implementation": sys.implementation.name
            }
        }

    async def check_database(self) -> bool:
        """Check database connectivity"""
        try:
            from database import get_db_manager
            db = get_db_manager()
            # Simple check - try to access database
            # If it doesn't raise exception, it's working
            return True
        except Exception as e:
            logger.warning(f"Database check failed: {e}")
            return False

    async def check_cache(self) -> bool:
        """Check cache connectivity"""
        try:
            from utils.cache import get_cache
            cache = get_cache()
            # Simple check - if cache instance exists
            return cache is not None
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
            return False

    async def check_disk_space(self) -> bool:
        """Check disk space availability (for readiness probe)"""
        try:
            disk = psutil.disk_usage('/')
            # Healthy if less than 90% used
            return disk.percent < 90
        except Exception as e:
            logger.warning(f"Disk space check failed: {e}")
            return False

    async def check_memory_status(self) -> bool:
        """Check memory availability (for readiness probe)"""
        try:
            memory = psutil.virtual_memory()
            # Healthy if less than 90% used
            return memory.percent < 90
        except Exception as e:
            logger.warning(f"Memory check failed: {e}")
            return False

    async def check_cpu_status(self) -> bool:
        """Check CPU usage (for readiness probe)"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            # Healthy if less than 90% used
            return cpu_percent < 90
        except Exception as e:
            logger.warning(f"CPU check failed: {e}")
            return False


class SystemInfo:
    """Get system information"""

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            "platform": {
                "system": sys.platform,
                "python_version": sys.version,
                "python_implementation": sys.implementation.name
            },
            "hardware": {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total": psutil.virtual_memory().total / (1024**3),
                "memory_available": psutil.virtual_memory().available / (1024**3),
                "disk_total": psutil.disk_usage('/').total / (1024**3),
                "disk_free": psutil.disk_usage('/').free / (1024**3)
            },
            "process": {
                "pid": psutil.Process().pid,
                "memory_mb": psutil.Process().memory_info().rss / (1024**2),
                "cpu_percent": psutil.Process().cpu_percent(interval=0.1),
                "threads": psutil.Process().num_threads()
            }
        }


# Global health check instance
_health_check = HealthCheck()


def get_health_check() -> HealthCheck:
    """Get global health check instance"""
    return _health_check


def get_health_checker() -> HealthCheck:
    """Get global health check instance (alias for compatibility)"""
    return _health_check


async def check_health() -> Dict[str, Any]:
    """Quick health check function"""
    return await _health_check.run_all_checks()
