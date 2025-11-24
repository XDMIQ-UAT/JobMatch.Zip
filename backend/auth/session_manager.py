"""
Session Management with Redis backend.
Implements secure, HIPAA-compliant token-based sessions.
"""
import logging
import secrets
import redis
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import Request, Response

from config import settings

logger = logging.getLogger(__name__)

# Redis connection
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        logger.info(f"Redis client connected to {settings.REDIS_URL}")
    return _redis_client


class SessionManager:
    """Manages secure, token-based sessions with Redis backend."""
    
    # Session configuration
    SESSION_COOKIE_NAME = "jobmatch_session"
    SESSION_DURATION = timedelta(days=30)  # Rolling 30-day sessions
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Initialize session manager with Redis client."""
        self.redis = redis_client or get_redis_client()
    
    def create_session(
        self,
        anonymous_id: str,
        response: Response,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new session and set secure cookie.
        
        Args:
            anonymous_id: User's anonymous ID
            response: FastAPI Response object to set cookie
            additional_data: Additional session data to store
        
        Returns:
            Session token
        """
        # Generate cryptographically secure session token
        token = secrets.token_urlsafe(32)
        
        # Prepare session data
        session_data = {
            "anonymous_id": anonymous_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat(),
        }
        
        if additional_data:
            session_data.update(additional_data)
        
        # Store in Redis with expiration
        session_key = f"session:{token}"
        expiration_seconds = int(self.SESSION_DURATION.total_seconds())
        
        # Store each field separately for easier updates
        self.redis.hset(session_key, mapping=session_data)
        self.redis.expire(session_key, expiration_seconds)
        
        logger.info(f"Created session for user {anonymous_id[:8]}... (expires in {expiration_seconds}s)")
        
        # Set secure HTTP-only cookie
        self._set_session_cookie(response, token)
        
        return token
    
    def get_session(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Get session data from request cookie.
        
        Args:
            request: FastAPI Request object
        
        Returns:
            Session data dict or None if invalid/expired
        """
        # Get token from cookie
        token = request.cookies.get(self.SESSION_COOKIE_NAME)
        if not token:
            return None
        
        # Retrieve from Redis
        session_key = f"session:{token}"
        session_data = self.redis.hgetall(session_key)
        
        if not session_data:
            logger.debug("Session not found or expired")
            return None
        
        # Update last active timestamp (rolling session)
        self.redis.hset(session_key, "last_active", datetime.utcnow().isoformat())
        self.redis.expire(session_key, int(self.SESSION_DURATION.total_seconds()))
        
        return session_data
    
    def get_anonymous_id(self, request: Request) -> Optional[str]:
        """
        Get anonymous ID from session cookie.
        
        Args:
            request: FastAPI Request object
        
        Returns:
            Anonymous ID or None if no valid session
        """
        session = self.get_session(request)
        if session:
            return session.get("anonymous_id")
        return None
    
    def refresh_session(self, request: Request, response: Response) -> bool:
        """
        Refresh session expiration (rolling sessions).
        
        Args:
            request: FastAPI Request object
            response: FastAPI Response object
        
        Returns:
            True if session refreshed, False otherwise
        """
        token = request.cookies.get(self.SESSION_COOKIE_NAME)
        if not token:
            return False
        
        session_key = f"session:{token}"
        
        # Check if session exists
        if not self.redis.exists(session_key):
            return False
        
        # Refresh expiration
        expiration_seconds = int(self.SESSION_DURATION.total_seconds())
        self.redis.expire(session_key, expiration_seconds)
        self.redis.hset(session_key, "last_active", datetime.utcnow().isoformat())
        
        # Refresh cookie
        self._set_session_cookie(response, token)
        
        return True
    
    def destroy_session(self, request: Request, response: Response) -> bool:
        """
        Destroy session (logout).
        
        Args:
            request: FastAPI Request object
            response: FastAPI Response object
        
        Returns:
            True if session destroyed, False if no session found
        """
        token = request.cookies.get(self.SESSION_COOKIE_NAME)
        if not token:
            return False
        
        # Delete from Redis
        session_key = f"session:{token}"
        deleted = self.redis.delete(session_key)
        
        # Clear cookie
        response.delete_cookie(
            key=self.SESSION_COOKIE_NAME,
            path="/",
            domain=self._get_cookie_domain(),
            secure=self._is_production(),
            httponly=True,
            samesite="strict"
        )
        
        logger.info("Session destroyed")
        return bool(deleted)
    
    def _set_session_cookie(self, response: Response, token: str) -> None:
        """
        Set secure session cookie.
        
        Args:
            response: FastAPI Response object
            token: Session token
        """
        response.set_cookie(
            key=self.SESSION_COOKIE_NAME,
            value=token,
            max_age=int(self.SESSION_DURATION.total_seconds()),
            path="/",
            domain=self._get_cookie_domain(),
            secure=self._is_production(),  # HTTPS only in production
            httponly=True,  # Not accessible via JavaScript
            samesite="strict"  # CSRF protection
        )
    
    def _get_cookie_domain(self) -> Optional[str]:
        """Get cookie domain based on environment."""
        if self._is_production():
            return "jobmatch.zip"  # Allow subdomains
        return None  # Local development
    
    def _is_production(self) -> bool:
        """Check if running in production environment."""
        return settings.ENVIRONMENT == "production"


# Factory function
def create_session_manager(redis_client: Optional[redis.Redis] = None) -> SessionManager:
    """Create session manager instance."""
    return SessionManager(redis_client)
