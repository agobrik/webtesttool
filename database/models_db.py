"""Database models for SQLAlchemy"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ScanResultDB(Base):
    """Scan result database model"""

    __tablename__ = 'scan_results'

    id = Column(Integer, primary_key=True)
    scan_id = Column(String(100), unique=True, nullable=False)
    target_url = Column(String(500), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration = Column(Float)
    status = Column(String(50))
    summary = Column(JSON)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    findings = relationship("FindingDB", back_populates="scan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ScanResult(id={self.id}, target={self.target_url}, status={self.status})>"


class FindingDB(Base):
    """Finding database model"""

    __tablename__ = 'findings'

    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey('scan_results.id'), nullable=False)
    finding_id = Column(String(100))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    url = Column(String(1000))
    cwe_id = Column(String(50))
    owasp_category = Column(String(100))
    cvss_score = Column(Float)
    evidence = Column(JSON)
    recommendations = Column(JSON)
    finding_metadata = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy reserved word
    timestamp = Column(DateTime, default=datetime.now)

    # Relationships
    scan = relationship("ScanResultDB", back_populates="findings")

    def __repr__(self):
        return f"<Finding(id={self.id}, title={self.title}, severity={self.severity})>"
