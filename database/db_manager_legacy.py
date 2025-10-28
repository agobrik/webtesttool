"""Database manager for storing and retrieving scan results"""

import os
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from .models_db import Base, ScanResultDB, FindingDB
from core.models import ScanResult


class DatabaseManager:
    """Manages database operations for scan results"""

    def __init__(self, db_url: str = None):
        """
        Initialize DatabaseManager

        Args:
            db_url: Database URL (defaults to SQLite)
        """
        if db_url is None:
            # Default to SQLite in data directory
            os.makedirs('data', exist_ok=True)
            db_url = 'sqlite:///data/testool.db'

        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables
        Base.metadata.create_all(self.engine)
        logger.info(f"Database initialized: {db_url}")

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    def save_scan_result(self, scan_result: ScanResult) -> int:
        """
        Save scan result to database

        Args:
            scan_result: ScanResult object to save

        Returns:
            Database ID of saved scan
        """
        session = self.get_session()

        try:
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

            # Save all findings
            for finding in scan_result.get_all_findings():
                finding_db = FindingDB(
                    scan_id=scan_db.id,
                    finding_id=finding.id,
                    title=finding.title,
                    description=finding.description,
                    severity=finding.severity.value,
                    category=finding.category.value,
                    url=finding.url,
                    cwe_id=finding.cwe_id,
                    owasp_category=finding.owasp_category,
                    cvss_score=finding.cvss_score,
                    evidence=[e.dict() for e in finding.evidence],
                    recommendations=[r.dict() for r in finding.recommendations],
                    metadata=finding.metadata,
                    timestamp=finding.timestamp
                )
                session.add(finding_db)

            session.commit()
            logger.info(f"Saved scan result {scan_result.id} to database (ID: {scan_db.id})")
            return scan_db.id

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving scan result: {str(e)}")
            raise
        finally:
            session.close()

    def get_scan_result(self, scan_id: int) -> Optional[ScanResultDB]:
        """
        Get scan result by ID

        Args:
            scan_id: Database ID of scan

        Returns:
            ScanResultDB object or None
        """
        session = self.get_session()
        try:
            return session.query(ScanResultDB).filter(ScanResultDB.id == scan_id).first()
        finally:
            session.close()

    def get_all_scans(self, limit: int = 100) -> List[ScanResultDB]:
        """
        Get all scan results

        Args:
            limit: Maximum number of results

        Returns:
            List of ScanResultDB objects
        """
        session = self.get_session()
        try:
            return session.query(ScanResultDB).order_by(ScanResultDB.start_time.desc()).limit(limit).all()
        finally:
            session.close()

    def get_findings_by_severity(self, severity: str, limit: int = 100) -> List[FindingDB]:
        """
        Get findings by severity

        Args:
            severity: Severity level
            limit: Maximum number of results

        Returns:
            List of FindingDB objects
        """
        session = self.get_session()
        try:
            return session.query(FindingDB).filter(
                FindingDB.severity == severity
            ).order_by(FindingDB.timestamp.desc()).limit(limit).all()
        finally:
            session.close()

    def get_findings_by_scan(self, scan_id: int) -> List[FindingDB]:
        """
        Get all findings for a scan

        Args:
            scan_id: Database ID of scan

        Returns:
            List of FindingDB objects
        """
        session = self.get_session()
        try:
            return session.query(FindingDB).filter(FindingDB.scan_id == scan_id).all()
        finally:
            session.close()

    def delete_scan(self, scan_id: int) -> bool:
        """
        Delete scan and its findings

        Args:
            scan_id: Database ID of scan

        Returns:
            True if deleted, False otherwise
        """
        session = self.get_session()
        try:
            scan = session.query(ScanResultDB).filter(ScanResultDB.id == scan_id).first()
            if scan:
                session.delete(scan)
                session.commit()
                logger.info(f"Deleted scan {scan_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting scan: {str(e)}")
            return False
        finally:
            session.close()

    def get_statistics(self) -> dict:
        """
        Get database statistics

        Returns:
            Dictionary with statistics
        """
        session = self.get_session()
        try:
            total_scans = session.query(ScanResultDB).count()
            total_findings = session.query(FindingDB).count()

            critical_findings = session.query(FindingDB).filter(FindingDB.severity == 'critical').count()
            high_findings = session.query(FindingDB).filter(FindingDB.severity == 'high').count()
            medium_findings = session.query(FindingDB).filter(FindingDB.severity == 'medium').count()
            low_findings = session.query(FindingDB).filter(FindingDB.severity == 'low').count()

            return {
                'total_scans': total_scans,
                'total_findings': total_findings,
                'critical_findings': critical_findings,
                'high_findings': high_findings,
                'medium_findings': medium_findings,
                'low_findings': low_findings
            }
        finally:
            session.close()
