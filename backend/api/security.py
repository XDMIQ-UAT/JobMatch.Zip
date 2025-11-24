"""
Security Operations API Endpoints.
For cybersecurity operations team.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from database.connection import get_db
from security.risk_monitor import (
    create_risk_monitor,
    RiskLevel,
    RiskStatus
)
from security.vulnerability_scanner import create_vulnerability_scanner

router = APIRouter(prefix="/api/security", tags=["security"])


@router.get("/risks")
async def list_risks(
    level: str = None,
    status: str = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """List security risks."""
    monitor = create_risk_monitor(db)
    
    risks = monitor.list_risks(
        level=RiskLevel(level) if level else None,
        status=RiskStatus(status) if status else None
    )
    
    return {
        "risks": [risk.to_dict() for risk in risks],
        "count": len(risks)
    }


@router.get("/risks/unmitigated")
async def get_unmitigated_risks(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get all unmitigated risks."""
    monitor = create_risk_monitor(db)
    risks = monitor.get_unmitigated_risks()
    
    return {
        "risks": [risk.to_dict() for risk in risks],
        "count": len(risks),
        "critical_count": len([r for r in risks if r.level == RiskLevel.CRITICAL])
    }


@router.get("/risks/critical")
async def get_critical_risks(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get all critical risks."""
    monitor = create_risk_monitor(db)
    risks = monitor.get_critical_risks()
    
    return {
        "risks": [risk.to_dict() for risk in risks],
        "count": len(risks)
    }


@router.get("/risks/report")
async def get_risk_report(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get comprehensive security risk report."""
    monitor = create_risk_monitor(db)
    return monitor.generate_report()


@router.post("/risks/{risk_id}/mitigate")
async def mitigate_risk(
    risk_id: str,
    mitigated_by: str,
    notes: str = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Mark a risk as mitigated."""
    monitor = create_risk_monitor(db)
    
    success = monitor.mark_mitigated(risk_id, mitigated_by, notes)
    
    if not success:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    risk = monitor.get_risk(risk_id)
    return {
        "success": True,
        "risk": risk.to_dict() if risk else None
    }


@router.post("/scan/dependencies")
async def scan_dependencies(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Scan dependencies for vulnerabilities."""
    monitor = create_risk_monitor(db)
    scanner = create_vulnerability_scanner(monitor)
    
    vulnerabilities = scanner.scan_requirements()
    
    return {
        "vulnerabilities": vulnerabilities,
        "count": len(vulnerabilities),
        "scanned_at": "2024-01-01T00:00:00Z"  # Would use actual timestamp
    }


@router.post("/scan/code")
async def scan_code(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Scan code for security issues."""
    monitor = create_risk_monitor(db)
    scanner = create_vulnerability_scanner(monitor)
    
    issues = scanner.scan_python_code()
    
    return {
        "issues": issues,
        "count": len(issues),
        "scanned_at": "2024-01-01T00:00:00Z"  # Would use actual timestamp
    }

