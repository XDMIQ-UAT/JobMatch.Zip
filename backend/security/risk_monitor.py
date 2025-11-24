"""
Security Risk Monitoring System.
Continuously monitors and tracks security risks.
"""
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RiskStatus(str, Enum):
    """Risk status."""
    UNMITIGATED = "unmitigated"
    IN_PROGRESS = "in_progress"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    FALSE_POSITIVE = "false_positive"


class SecurityRisk:
    """Represents a security risk."""
    
    def __init__(
        self,
        risk_id: str,
        title: str,
        description: str,
        level: RiskLevel,
        category: str,
        location: str,
        status: RiskStatus = RiskStatus.UNMITIGATED,
        remediation_steps: Optional[List[str]] = None,
        detected_at: Optional[datetime] = None
    ):
        self.risk_id = risk_id
        self.title = title
        self.description = description
        self.level = level
        self.category = category
        self.location = location
        self.status = status
        self.remediation_steps = remediation_steps or []
        self.detected_at = detected_at or datetime.utcnow()
        self.mitigated_at: Optional[datetime] = None
        self.mitigated_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert risk to dictionary."""
        return {
            "risk_id": self.risk_id,
            "title": self.title,
            "description": self.description,
            "level": self.level.value,
            "category": self.category,
            "location": self.location,
            "status": self.status.value,
            "remediation_steps": self.remediation_steps,
            "detected_at": self.detected_at.isoformat(),
            "mitigated_at": self.mitigated_at.isoformat() if self.mitigated_at else None,
            "mitigated_by": self.mitigated_by
        }


class RiskMonitor:
    """Monitors and tracks security risks."""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session
        self.risks: Dict[str, SecurityRisk] = {}
        self._initialize_known_risks()
    
    def _initialize_known_risks(self):
        """Initialize known security risks."""
        known_risks = [
            SecurityRisk(
                risk_id="RISK-001",
                title="Hardcoded Default SECRET_KEY",
                description="Default SECRET_KEY 'change-me-in-production' found in config",
                level=RiskLevel.CRITICAL,
                category="Secrets Management",
                location="backend/config.py:24",
                remediation_steps=[
                    "Generate strong random SECRET_KEY",
                    "Move to environment variables",
                    "Use secrets management service",
                    "Rotate keys regularly"
                ]
            ),
            SecurityRisk(
                risk_id="RISK-002",
                title="Dependency Vulnerabilities",
                description="Dependencies may contain known CVEs",
                level=RiskLevel.CRITICAL,
                category="Dependency Management",
                location="backend/requirements.txt",
                remediation_steps=[
                    "Run dependency vulnerability scanner",
                    "Update vulnerable packages",
                    "Pin secure versions",
                    "Enable automated scanning"
                ]
            ),
            SecurityRisk(
                risk_id="RISK-003",
                title="Overly Permissive CORS",
                description="CORS allows all methods and headers",
                level=RiskLevel.HIGH,
                category="API Security",
                location="backend/main.py:18-24",
                remediation_steps=[
                    "Restrict CORS origins to specific domains",
                    "Limit allowed methods",
                    "Restrict allowed headers",
                    "Remove credentials for public endpoints"
                ]
            ),
            SecurityRisk(
                risk_id="RISK-004",
                title="Missing Security Headers",
                description="No CSP, HSTS, X-Frame-Options headers",
                level=RiskLevel.HIGH,
                category="Web Security",
                location="backend/main.py",
                remediation_steps=[
                    "Add Content-Security-Policy header",
                    "Add Strict-Transport-Security header",
                    "Add X-Frame-Options header",
                    "Add X-Content-Type-Options header"
                ]
            ),
            SecurityRisk(
                risk_id="RISK-005",
                title="No Rate Limiting",
                description="API endpoints lack rate limiting",
                level=RiskLevel.MEDIUM,
                category="API Security",
                location="backend/main.py",
                remediation_steps=[
                    "Implement rate limiting middleware",
                    "Configure per-endpoint limits",
                    "Add IP-based throttling",
                    "Monitor for abuse"
                ]
            ),
            SecurityRisk(
                risk_id="RISK-006",
                title="Duplicate Dependency",
                description="httpx==0.25.2 appears twice in requirements.txt",
                level=RiskLevel.LOW,
                category="Dependency Management",
                location="backend/requirements.txt:14,17",
                remediation_steps=[
                    "Remove duplicate entry",
                    "Verify single version",
                    "Update requirements.txt"
                ]
            )
        ]
        
        for risk in known_risks:
            self.risks[risk.risk_id] = risk
    
    def register_risk(self, risk: SecurityRisk):
        """Register a new security risk."""
        self.risks[risk.risk_id] = risk
        logger.warning(f"Security risk detected: {risk.risk_id} - {risk.title} ({risk.level.value})")
    
    def get_risk(self, risk_id: str) -> Optional[SecurityRisk]:
        """Get a specific risk by ID."""
        return self.risks.get(risk_id)
    
    def list_risks(
        self,
        level: Optional[RiskLevel] = None,
        status: Optional[RiskStatus] = None
    ) -> List[SecurityRisk]:
        """List risks with optional filtering."""
        risks = list(self.risks.values())
        
        if level:
            risks = [r for r in risks if r.level == level]
        
        if status:
            risks = [r for r in risks if r.status == status]
        
        return sorted(risks, key=lambda x: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}[x.level.value],
            x.detected_at
        ))
    
    def get_unmitigated_risks(self) -> List[SecurityRisk]:
        """Get all unmitigated risks."""
        return self.list_risks(status=RiskStatus.UNMITIGATED)
    
    def get_critical_risks(self) -> List[SecurityRisk]:
        """Get all critical risks."""
        return self.list_risks(level=RiskLevel.CRITICAL)
    
    def mark_mitigated(
        self,
        risk_id: str,
        mitigated_by: str,
        notes: Optional[str] = None
    ) -> bool:
        """Mark a risk as mitigated."""
        risk = self.risks.get(risk_id)
        if not risk:
            return False
        
        risk.status = RiskStatus.MITIGATED
        risk.mitigated_at = datetime.utcnow()
        risk.mitigated_by = mitigated_by
        
        logger.info(f"Risk {risk_id} mitigated by {mitigated_by}")
        return True
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate security risk report."""
        total_risks = len(self.risks)
        unmitigated = len(self.get_unmitigated_risks())
        critical = len(self.get_critical_risks())
        
        by_level = {}
        for level in RiskLevel:
            by_level[level.value] = len(self.list_risks(level=level))
        
        by_status = {}
        for status in RiskStatus:
            by_status[status.value] = len(self.list_risks(status=status))
        
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_risks": total_risks,
                "unmitigated": unmitigated,
                "critical": critical,
                "by_level": by_level,
                "by_status": by_status
            },
            "risks": [risk.to_dict() for risk in self.risks.values()]
        }


def create_risk_monitor(db_session: Optional[Session] = None) -> RiskMonitor:
    """Factory function to create risk monitor."""
    return RiskMonitor(db_session)

