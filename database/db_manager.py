"""
Database Manager
High-performance database operations with connection pooling and batch inserts
"""

import os
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy import Index
from loguru import logger

from .models_db import Base, ScanResultDB, FindingDB
from core.models import ScanResult, Finding
from core.exceptions import DatabaseError


class DatabaseManager:
    """
    Optimized database manager with performance enhancements

    Features:
    - Connection pooling
    - Batch insert operations
    - Context manager for sessions
    - Query optimization
    - Index management
    - Async support preparation
    """

    def __init__(
        self,
        db_url: Optional[str] = None,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_pre_ping: bool = True,
        echo: bool = False
    ):
        """
        Initialize optimized database manager

        Args:
            db_url: Database URL (defaults to SQLite)
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
            pool_pre_ping: Enable connection health checks
            echo: Enable SQL logging
        """
        if db_url is None:
            # Default to SQLite in data directory
            os.makedirs('data', exist_ok=True)
            db_url = 'sqlite:///data/testool.db'

        # Determine if SQLite
        self.is_sqlite = db_url.startswith('sqlite')

        # Create engine with optimizations
        if self.is_sqlite:
            # SQLite-specific optimizations
            self.engine = create_engine(
                db_url,
                echo=echo,
                poolclass=NullPool,  # SQLite doesn't benefit from pooling
                connect_args={'check_same_thread': False}  # Allow multi-threading
            )

            # Enable WAL mode for better concurrency
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()

        else:
            # PostgreSQL/MySQL with connection pooling
            self.engine = create_engine(
                db_url,
                echo=echo,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=pool_pre_ping,
                pool_recycle=3600  # Recycle connections after 1 hour
            )

        # Create session factory
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.Session = scoped_session(self.session_factory)

        # Create tables and indexes
        self._initialize_database()

        logger.info(f"Optimized database initialized: {db_url}")

    def _initialize_database(self):
        """Initialize database schema and indexes"""
        # Create tables
        Base.metadata.create_all(self.engine)

        # Create indexes for better query performance
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes for optimized queries"""
        try:
            # Index on scan_id for faster joins
            if not Index('ix_scan_result_scan_id', ScanResultDB.scan_id).exists(self.engine):
                Index('ix_scan_result_scan_id', ScanResultDB.scan_id).create(self.engine)

            # Index on target_url for faster searches
            if not Index('ix_scan_result_target_url', ScanResultDB.target_url).exists(self.engine):
                Index('ix_scan_result_target_url', ScanResultDB.target_url).create(self.engine)

            # Index on start_time for faster sorting
            if not Index('ix_scan_result_start_time', ScanResultDB.start_time).exists(self.engine):
                Index('ix_scan_result_start_time', ScanResultDB.start_time).create(self.engine)

            # Index on severity for faster filtering
            if not Index('ix_finding_severity', FindingDB.severity).exists(self.engine):
                Index('ix_finding_severity', FindingDB.severity).create(self.engine)

            # Composite index on scan_id and severity
            if not Index('ix_finding_scan_severity', FindingDB.scan_id, FindingDB.severity).exists(self.engine):
                Index('ix_finding_scan_severity', FindingDB.scan_id, FindingDB.severity).create(self.engine)

            logger.debug("Database indexes created successfully")

        except Exception as e:
            logger.warning(f"Failed to create some indexes: {e}")

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions

        Usage:
            with db.get_session() as session:
                session.query(...)
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise DatabaseError(
                f"Database operation failed: {str(e)}",
                original_error=e
            )
        finally:
            session.close()

    def save_scan_result(self, scan_result: ScanResult) -> int:
        """
        Save scan result to database

        Args:
            scan_result: ScanResult object to save

        Returns:
            Database ID of saved scan
        """
        with self.get_session() as session:
            # Create scan result record
            scan_db = ScanResultDB(
                scan_id=scan_result.id,
                target_url=scan_result.target_url,
                start_time=scan_result.start_time,
                end_time=scan_result.end_time,
                duration=scan_result.duration,
                status=scan_result.status.value,
                summary=scan_result.summary,
                config=scan_result.config
            )

            session.add(scan_db)
            session.flush()  # Get the ID

            # Batch insert findings
            findings = scan_result.get_all_findings()
            if findings:
                self._batch_insert_findings(session, scan_db.id, findings)

            logger.info(f"Saved scan result {scan_result.id} to database (ID: {scan_db.id})")
            return scan_db.id

    def _batch_insert_findings(
        self,
        session: Session,
        scan_id: int,
        findings: List[Finding],
        batch_size: int = 100
    ):
        """
        Batch insert findings for better performance

        Args:
            session: Database session
            scan_id: Scan database ID
            findings: List of findings
            batch_size: Number of records per batch
        """
        finding_dicts = []

        for finding in findings:
            finding_dict = {
                'scan_id': scan_id,
                'finding_id': finding.id,
                'title': finding.title,
                'description': finding.description,
                'severity': finding.severity.value,
                'category': finding.category.value,
                'url': finding.url,
                'cwe_id': finding.cwe_id,
                'owasp_category': finding.owasp_category,
                'cvss_score': finding.cvss_score,
                'evidence': [e.model_dump() for e in finding.evidence],
                'recommendations': [r.model_dump() for r in finding.recommendations],
                'metadata': finding.metadata,
                'timestamp': finding.timestamp
            }
            finding_dicts.append(finding_dict)

            # Insert batch when batch_size is reached
            if len(finding_dicts) >= batch_size:
                session.bulk_insert_mappings(FindingDB, finding_dicts)
                finding_dicts = []

        # Insert remaining findings
        if finding_dicts:
            session.bulk_insert_mappings(FindingDB, finding_dicts)

        logger.debug(f"Batch inserted {len(findings)} findings")

    def get_scan_result(self, scan_id: int) -> Optional[ScanResultDB]:
        """
        Get scan result by ID

        Args:
            scan_id: Database ID of scan

        Returns:
            ScanResultDB object or None
        """
        with self.get_session() as session:
            return session.query(ScanResultDB).filter(
                ScanResultDB.id == scan_id
            ).first()

    def get_all_scans(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = 'start_time',
        descending: bool = True
    ) -> List[ScanResultDB]:
        """
        Get all scan results with pagination

        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            order_by: Column to order by
            descending: Sort in descending order

        Returns:
            List of ScanResultDB objects
        """
        with self.get_session() as session:
            query = session.query(ScanResultDB)

            # Order by
            order_column = getattr(ScanResultDB, order_by, ScanResultDB.start_time)
            if descending:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())

            # Pagination
            query = query.limit(limit).offset(offset)

            return query.all()

    def get_findings_by_severity(
        self,
        severity: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[FindingDB]:
        """
        Get findings by severity with pagination

        Args:
            severity: Severity level
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of FindingDB objects
        """
        with self.get_session() as session:
            return session.query(FindingDB).filter(
                FindingDB.severity == severity
            ).order_by(
                FindingDB.timestamp.desc()
            ).limit(limit).offset(offset).all()

    def get_findings_by_scan(
        self,
        scan_id: int,
        severity: Optional[str] = None
    ) -> List[FindingDB]:
        """
        Get all findings for a scan

        Args:
            scan_id: Database ID of scan
            severity: Optional severity filter

        Returns:
            List of FindingDB objects
        """
        with self.get_session() as session:
            query = session.query(FindingDB).filter(FindingDB.scan_id == scan_id)

            if severity:
                query = query.filter(FindingDB.severity == severity)

            return query.all()

    def delete_scan(self, scan_id: int) -> bool:
        """
        Delete scan and its findings (cascade)

        Args:
            scan_id: Database ID of scan

        Returns:
            True if deleted, False otherwise
        """
        with self.get_session() as session:
            scan = session.query(ScanResultDB).filter(
                ScanResultDB.id == scan_id
            ).first()

            if scan:
                session.delete(scan)
                logger.info(f"Deleted scan {scan_id}")
                return True
            return False

    def delete_old_scans(self, days: int = 30) -> int:
        """
        Delete scans older than specified days

        Args:
            days: Number of days to keep

        Returns:
            Number of scans deleted
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)

        with self.get_session() as session:
            deleted = session.query(ScanResultDB).filter(
                ScanResultDB.start_time < cutoff_date
            ).delete()

            logger.info(f"Deleted {deleted} old scans (older than {days} days)")
            return deleted

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics with optimized queries

        Returns:
            Dictionary with statistics
        """
        with self.get_session() as session:
            # Use single query with conditional aggregation for better performance
            from sqlalchemy import func, case

            stats = session.query(
                func.count(ScanResultDB.id).label('total_scans'),
            ).first()

            finding_stats = session.query(
                func.count(FindingDB.id).label('total_findings'),
                func.sum(case((FindingDB.severity == 'critical', 1), else_=0)).label('critical'),
                func.sum(case((FindingDB.severity == 'high', 1), else_=0)).label('high'),
                func.sum(case((FindingDB.severity == 'medium', 1), else_=0)).label('medium'),
                func.sum(case((FindingDB.severity == 'low', 1), else_=0)).label('low'),
            ).first()

            return {
                'total_scans': stats.total_scans,
                'total_findings': finding_stats.total_findings or 0,
                'critical_findings': finding_stats.critical or 0,
                'high_findings': finding_stats.high or 0,
                'medium_findings': finding_stats.medium or 0,
                'low_findings': finding_stats.low or 0
            }

    def get_scan_summary(self, scan_id: int) -> Optional[Dict[str, Any]]:
        """
        Get scan summary with finding counts

        Args:
            scan_id: Database ID of scan

        Returns:
            Dictionary with scan summary
        """
        with self.get_session() as session:
            from sqlalchemy import func, case

            scan = session.query(ScanResultDB).filter(
                ScanResultDB.id == scan_id
            ).first()

            if not scan:
                return None

            finding_stats = session.query(
                func.count(FindingDB.id).label('total'),
                func.sum(case((FindingDB.severity == 'critical', 1), else_=0)).label('critical'),
                func.sum(case((FindingDB.severity == 'high', 1), else_=0)).label('high'),
                func.sum(case((FindingDB.severity == 'medium', 1), else_=0)).label('medium'),
                func.sum(case((FindingDB.severity == 'low', 1), else_=0)).label('low'),
            ).filter(FindingDB.scan_id == scan_id).first()

            return {
                'scan_id': scan.scan_id,
                'target_url': scan.target_url,
                'start_time': scan.start_time,
                'end_time': scan.end_time,
                'duration': scan.duration,
                'status': scan.status,
                'findings': {
                    'total': finding_stats.total or 0,
                    'critical': finding_stats.critical or 0,
                    'high': finding_stats.high or 0,
                    'medium': finding_stats.medium or 0,
                    'low': finding_stats.low or 0,
                }
            }

    def vacuum_database(self):
        """Vacuum database to reclaim space (SQLite only)"""
        if self.is_sqlite:
            with self.engine.connect() as conn:
                conn.execute("VACUUM")
            logger.info("Database vacuumed successfully")

    def close(self):
        """Close database connections"""
        self.Session.remove()
        self.engine.dispose()
        logger.info("Database connections closed")


# Singleton instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(
    db_url: Optional[str] = None,
    **kwargs
) -> DatabaseManager:
    """
    Get or create singleton database manager

    Args:
        db_url: Database URL
        **kwargs: Additional arguments for OptimizedDatabaseManager

    Returns:
        OptimizedDatabaseManager instance
    """
    global _db_manager

    if _db_manager is None:
        _db_manager = DatabaseManager(db_url, **kwargs)

    return _db_manager
