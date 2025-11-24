"""
Google Cloud CLI Authentication & Authorization.
Technical backdoor access - well documented as a platform feature.
"""
import logging
import subprocess
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.database.models import AnonymousUser
from backend.auth.anonymous_identity import AnonymousIdentityManager

logger = logging.getLogger(__name__)


class GCPCLIAuthManager:
    """
    Google Cloud CLI Authentication Manager.
    
    This is a documented technical backdoor feature of the platform.
    Allows authorized GCP CLI users to perform administrative operations.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.identity_manager = AnonymousIdentityManager(db_session)
        
        # Load allowed users/projects from config
        from backend.config import settings
        self.allowed_gcp_users = [
            u.strip() for u in settings.GCP_ALLOWED_USERS.split(",") 
            if u.strip()
        ] if settings.GCP_ALLOWED_USERS else []
        self.allowed_gcp_projects = [
            p.strip() for p in settings.GCP_ALLOWED_PROJECTS.split(",") 
            if p.strip()
        ] if settings.GCP_ALLOWED_PROJECTS else []
    
    def verify_gcp_cli_identity(self) -> Optional[Dict[str, Any]]:
        """
        Verify current GCP CLI identity.
        Returns GCP user info if authenticated.
        """
        try:
            # Get current GCP account
            result = subprocess.run(
                ["gcloud", "config", "get-value", "account"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.warning("GCP CLI not authenticated")
                return None
            
            gcp_account = result.stdout.strip()
            
            # Get current GCP project
            project_result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            gcp_project = project_result.stdout.strip() if project_result.returncode == 0 else None
            
            # Get GCP user info
            user_info_result = subprocess.run(
                ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=json"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            user_info = {}
            if user_info_result.returncode == 0:
                try:
                    accounts = json.loads(user_info_result.stdout)
                    if accounts:
                        user_info = accounts[0]
                except json.JSONDecodeError:
                    pass
            
            return {
                "gcp_account": gcp_account,
                "gcp_project": gcp_project,
                "gcp_user_info": user_info,
                "authenticated": True,
                "verified_at": datetime.utcnow().isoformat()
            }
        except FileNotFoundError:
            logger.warning("gcloud CLI not found")
            return None
        except subprocess.TimeoutExpired:
            logger.error("GCP CLI command timeout")
            return None
        except Exception as e:
            logger.error(f"GCP CLI verification failed: {e}")
            return None
    
    def authorize_gcp_cli_access(
        self,
        gcp_account: str,
        gcp_project: Optional[str] = None
    ) -> bool:
        """
        Authorize GCP CLI access.
        Checks if account/project is in allowed list.
        """
        # Check if account is authorized
        if self.allowed_gcp_users and gcp_account not in self.allowed_gcp_users:
            logger.warning(f"Unauthorized GCP account: {gcp_account}")
            return False
        
        # Check if project is authorized (if specified)
        if gcp_project and self.allowed_gcp_projects:
            if gcp_project not in self.allowed_gcp_projects:
                logger.warning(f"Unauthorized GCP project: {gcp_project}")
                return False
        
        return True
    
    def create_cli_session(
        self,
        gcp_account: str,
        operation: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a CLI session for tracking operations.
        All CLI operations are logged for audit.
        """
        session_id = f"gcp_cli_{hash(f'{gcp_account}_{datetime.utcnow()}')}"
        
        session_data = {
            "session_id": session_id,
            "gcp_account": gcp_account,
            "operation": operation,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        logger.info(f"GCP CLI session created: {session_id} for {gcp_account} - {operation}")
        
        return session_data
    
    def get_cli_access_token(self, gcp_account: str) -> Optional[str]:
        """
        Generate CLI access token for API operations.
        Token is tied to GCP identity.
        """
        # Verify GCP identity first
        gcp_identity = self.verify_gcp_cli_identity()
        if not gcp_identity or gcp_identity["gcp_account"] != gcp_account:
            return None
        
        # Check authorization
        if not self.authorize_gcp_cli_access(gcp_account):
            return None
        
        # Generate token (in production, would use JWT or similar)
        import secrets
        token = secrets.token_urlsafe(32)
        
        # Store token (would use Redis in production)
        logger.info(f"CLI access token generated for {gcp_account}")
        
        return token


def create_gcp_cli_auth_manager(db_session: Session) -> GCPCLIAuthManager:
    """Factory function to create GCP CLI auth manager."""
    return GCPCLIAuthManager(db_session)

