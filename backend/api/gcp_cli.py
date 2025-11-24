"""
Google Cloud CLI API Endpoints.
Technical backdoor access - documented platform feature.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from backend.database.connection import get_db
from backend.auth.gcp_cli_auth import create_gcp_cli_auth_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gcp-cli", tags=["gcp-cli"])


class GCPCLIVerifyResponse(BaseModel):
    """Response for GCP CLI verification."""
    authenticated: bool
    gcp_account: Optional[str] = None
    gcp_project: Optional[str] = None
    authorized: bool = False
    message: str


class CLICommandRequest(BaseModel):
    """Request for CLI command execution."""
    command: str
    parameters: Optional[Dict[str, Any]] = None


class CLICommandResponse(BaseModel):
    """Response for CLI command execution."""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    session_id: Optional[str] = None


@router.get("/verify", response_model=GCPCLIVerifyResponse)
async def verify_gcp_cli(
    db: Session = Depends(get_db)
):
    """
    Verify Google Cloud CLI authentication.
    
    This is a documented technical backdoor feature.
    Checks if user is authenticated via GCP CLI.
    """
    manager = create_gcp_cli_auth_manager(db)
    gcp_identity = manager.verify_gcp_cli_identity()
    
    if not gcp_identity:
        return GCPCLIVerifyResponse(
            authenticated=False,
            authorized=False,
            message="GCP CLI not authenticated. Run 'gcloud auth login' first."
        )
    
    authorized = manager.authorize_gcp_cli_access(
        gcp_account=gcp_identity["gcp_account"],
        gcp_project=gcp_identity.get("gcp_project")
    )
    
    return GCPCLIVerifyResponse(
        authenticated=True,
        gcp_account=gcp_identity["gcp_account"],
        gcp_project=gcp_identity.get("gcp_project"),
        authorized=authorized,
        message="GCP CLI authenticated" if authorized else "GCP CLI authenticated but not authorized"
    )


@router.post("/execute", response_model=CLICommandResponse)
async def execute_cli_command(
    request: CLICommandRequest,
    x_gcp_account: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Execute CLI command via GCP CLI backdoor.
    
    This is a documented technical backdoor feature.
    Requires GCP CLI authentication and authorization.
    """
    manager = create_gcp_cli_auth_manager(db)
    
    # Verify GCP CLI identity
    gcp_identity = manager.verify_gcp_cli_identity()
    if not gcp_identity:
        raise HTTPException(
            status_code=401,
            detail="GCP CLI not authenticated. Run 'gcloud auth login' first."
        )
    
    # Check authorization
    if not manager.authorize_gcp_cli_access(
        gcp_account=gcp_identity["gcp_account"],
        gcp_project=gcp_identity.get("gcp_project")
    ):
        raise HTTPException(
            status_code=403,
            detail="GCP CLI account not authorized for CLI operations"
        )
    
    # Create session
    session = manager.create_cli_session(
        gcp_account=gcp_identity["gcp_account"],
        operation=request.command,
        metadata=request.parameters
    )
    
    # Execute command (whitelist approach for security)
    allowed_commands = [
        "status",
        "health",
        "metrics",
        "logs",
        "users",
        "assessments",
        "matches"
    ]
    
    if request.command not in allowed_commands:
        raise HTTPException(
            status_code=400,
            detail=f"Command '{request.command}' not allowed. Allowed: {', '.join(allowed_commands)}"
        )
    
    # Execute command handler
    try:
        result = await execute_allowed_command(request.command, request.parameters, db)
        return CLICommandResponse(
            success=True,
            output=result,
            session_id=session["session_id"]
        )
    except Exception as e:
        logger.error(f"CLI command execution failed: {e}")
        return CLICommandResponse(
            success=False,
            error=str(e),
            session_id=session["session_id"]
        )


async def execute_allowed_command(
    command: str,
    parameters: Optional[Dict[str, Any]],
    db: Session
) -> str:
    """Execute allowed CLI commands."""
    import json
    
    if command == "status":
        return json.dumps({
            "status": "operational",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }, indent=2)
    
    elif command == "health":
        from backend.infrastructure.scaling import scaling_manager
        redis_ok = scaling_manager.check_redis_health()
        es_ok = scaling_manager.check_elasticsearch_health()
        return json.dumps({
            "redis": "healthy" if redis_ok else "unhealthy",
            "elasticsearch": "healthy" if es_ok else "unhealthy",
            "overall": "healthy" if (redis_ok and es_ok) else "degraded"
        }, indent=2)
    
    elif command == "metrics":
        from backend.database.models import AnonymousUser, CapabilityAssessment, Match
        user_count = db.query(AnonymousUser).count()
        assessment_count = db.query(CapabilityAssessment).count()
        match_count = db.query(Match).count()
        return json.dumps({
            "users": user_count,
            "assessments": assessment_count,
            "matches": match_count
        }, indent=2)
    
    elif command == "logs":
        # Return recent logs (would implement actual log retrieval)
        return json.dumps({
            "message": "Log retrieval not yet implemented",
            "note": "Would return recent platform logs"
        }, indent=2)
    
    elif command == "users":
        from backend.database.models import AnonymousUser
        count = db.query(AnonymousUser).count()
        return json.dumps({
            "total_users": count,
            "message": f"Total anonymous users: {count}"
        }, indent=2)
    
    elif command == "assessments":
        from backend.database.models import CapabilityAssessment
        count = db.query(CapabilityAssessment).count()
        xdmiq_count = db.query(CapabilityAssessment).filter(
            CapabilityAssessment.assessment_type == "xdmiq"
        ).count()
        return json.dumps({
            "total_assessments": count,
            "xdmiq_assessments": xdmiq_count,
            "other_assessments": count - xdmiq_count
        }, indent=2)
    
    elif command == "matches":
        from backend.database.models import Match
        count = db.query(Match).count()
        reviewed_count = db.query(Match).filter(Match.human_reviewed == True).count()
        return json.dumps({
            "total_matches": count,
            "human_reviewed": reviewed_count,
            "pending_review": count - reviewed_count
        }, indent=2)
    
    return json.dumps({"message": "Command executed"}, indent=2)


@router.get("/access-token")
async def get_cli_access_token(
    db: Session = Depends(get_db)
):
    """
    Get CLI access token for API operations.
    
    This is a documented technical backdoor feature.
    Token is tied to GCP CLI identity.
    """
    manager = create_gcp_cli_auth_manager(db)
    
    gcp_identity = manager.verify_gcp_cli_identity()
    if not gcp_identity:
        raise HTTPException(
            status_code=401,
            detail="GCP CLI not authenticated"
        )
    
    if not manager.authorize_gcp_cli_access(gcp_identity["gcp_account"]):
        raise HTTPException(
            status_code=403,
            detail="GCP CLI account not authorized"
        )
    
    token = manager.get_cli_access_token(gcp_identity["gcp_account"])
    
    if not token:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate access token"
        )
    
    return {
        "access_token": token,
        "gcp_account": gcp_identity["gcp_account"],
        "expires_in": 3600,
        "message": "Use this token for API operations via X-GCP-CLI-Token header"
    }


@router.get("/info")
async def get_cli_info():
    """
    Get information about GCP CLI backdoor feature.
    
    This endpoint documents the technical backdoor as a platform feature.
    """
    return {
        "feature_name": "Google Cloud CLI Technical Access",
        "description": "This is a documented technical backdoor feature that allows authorized GCP CLI users to perform administrative operations.",
        "authentication": "Requires 'gcloud auth login'",
        "authorization": "GCP account must be in authorized list",
        "usage": {
            "verify": "GET /api/gcp-cli/verify - Verify GCP CLI authentication",
            "execute": "POST /api/gcp-cli/execute - Execute CLI commands",
            "token": "GET /api/gcp-cli/access-token - Get API access token"
        },
        "security": {
            "whitelist_commands": True,
            "audit_logging": True,
            "session_tracking": True,
            "gcp_identity_required": True
        },
        "documentation": "See docs/GCP_CLI_BACKDOOR.md for full documentation"
    }

