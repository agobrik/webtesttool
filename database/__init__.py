"""Database layer for storing scan results"""

from .db_manager import DatabaseManager, get_db_manager
from .models_db import ScanResultDB, FindingDB

# Backward compatibility alias
OptimizedDatabaseManager = DatabaseManager

__all__ = [
    'DatabaseManager',
    'OptimizedDatabaseManager',  # deprecated, use DatabaseManager
    'get_db_manager',
    'ScanResultDB',
    'FindingDB'
]
