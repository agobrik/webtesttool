"""
Health Check and Monitoring API
Provides endpoints for system health monitoring
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import JSONResponse
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import psutil
import os

from utils.health import get_health_checker, HealthStatus
from utils.metrics import get_metrics


app = FastAPI(
    title="WebTestool Monitoring API",
    description="Health checks and metrics for WebTestool",
    version="1.0.0"
)


class ComponentStatus(Enum):
    """Component health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@app.get("/health")
async def health_check():
    """
    Comprehensive health check
    Returns overall system health and component status
    """
    health_checker = get_health_checker()
    result = await health_checker.run_all_checks()

    status_code = 200
    if result['status'] == HealthStatus.UNHEALTHY.value:
        status_code = 503
    elif result['status'] == HealthStatus.DEGRADED.value:
        status_code = 200  # Still operational

    return JSONResponse(
        content=result,
        status_code=status_code
    )


@app.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe
    Returns 200 if application is alive
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health/ready")
async def readiness_probe():
    """
    Kubernetes readiness probe
    Returns 200 if application is ready to serve requests
    """
    health_checker = get_health_checker()

    # Check critical components
    database_ok = await health_checker.check_database()
    cache_ok = await health_checker.check_cache()

    if database_ok and cache_ok:
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "database": database_ok,
                "cache": cache_ok
            }
        )


@app.get("/health/components")
async def component_health():
    """
    Detailed component health status
    """
    health_checker = get_health_checker()

    components = {
        "database": await health_checker.check_database(),
        "cache": await health_checker.check_cache(),
        "disk_space": await health_checker.check_disk_space(),
        "memory": await health_checker.check_memory_status(),
        "cpu": await health_checker.check_cpu_status()
    }

    return {
        "timestamp": datetime.now().isoformat(),
        "components": components,
        "overall_status": "healthy" if all(components.values()) else "degraded"
    }


@app.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus metrics endpoint
    Returns metrics in Prometheus format
    """
    metrics_collector = get_metrics()
    metrics_text = metrics_collector.get_metrics()

    return Response(
        content=metrics_text,
        media_type="text/plain; version=0.0.4"
    )


@app.get("/metrics/json")
async def metrics_json():
    """
    Get metrics in JSON format
    """
    metrics_collector = get_metrics()
    metrics = metrics_collector.get_all_metrics()

    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics
    }


@app.get("/stats/system")
async def system_stats():
    """
    Get system resource statistics
    """
    # CPU stats
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()

    # Memory stats
    memory = psutil.virtual_memory()

    # Disk stats
    disk = psutil.disk_usage('/')

    # Process stats
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info()

    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": {
            "percent": cpu_percent,
            "count": cpu_count,
            "per_cpu": psutil.cpu_percent(interval=1, percpu=True)
        },
        "memory": {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "used_gb": memory.used / (1024**3),
            "percent": memory.percent
        },
        "disk": {
            "total_gb": disk.total / (1024**3),
            "used_gb": disk.used / (1024**3),
            "free_gb": disk.free / (1024**3),
            "percent": disk.percent
        },
        "process": {
            "memory_mb": process_memory.rss / (1024**2),
            "cpu_percent": process.cpu_percent()
        }
    }


@app.get("/stats/scans")
async def scan_statistics():
    """
    Get scan statistics
    """
    from database import get_db_manager

    try:
        db = get_db_manager()

        # Get statistics from database
        stats = await db.get_scan_statistics()

        return {
            "timestamp": datetime.now().isoformat(),
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve scan statistics: {str(e)}"
        )


@app.get("/version")
async def version_info():
    """
    Get version information
    """
    return {
        "name": "WebTestool",
        "version": "2.0.0",
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "build_date": "2025-10-23",
        "status": "production"
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
