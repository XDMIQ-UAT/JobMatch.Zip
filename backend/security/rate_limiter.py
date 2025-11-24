"""
Rate Limiting Middleware.
Prevents abuse and DDoS attacks.
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: defaultdict = defaultdict(list)
        self.cleanup_interval = timedelta(minutes=5)
        self.last_cleanup = datetime.utcnow()
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Use IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Could also use anonymous user ID if available
        # For now, use IP
        return client_ip
    
    def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited."""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old entries
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries()
            self.last_cleanup = now
        
        # Get requests in last minute
        recent_requests = [
            req_time for req_time in self.request_counts[client_id]
            if req_time > minute_ago
        ]
        
        self.request_counts[client_id] = recent_requests
        
        # Check limit
        return len(recent_requests) >= self.requests_per_minute
    
    def _cleanup_old_entries(self):
        """Clean up old request entries."""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        for client_id in list(self.request_counts.keys()):
            self.request_counts[client_id] = [
                req_time for req_time in self.request_counts[client_id]
                if req_time > minute_ago
            ]
            
            # Remove empty entries
            if not self.request_counts[client_id]:
                del self.request_counts[client_id]
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request."""
        client_id = self._get_client_id(request)
        
        if self._is_rate_limited(client_id):
            logger.warning(f"Rate limit exceeded for {client_id}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Record request
        self.request_counts[client_id].append(datetime.utcnow())
        
        response = await call_next(request)
        
        # Add rate limit headers
        recent_requests = [
            req_time for req_time in self.request_counts[client_id]
            if req_time > datetime.utcnow() - timedelta(minutes=1)
        ]
        remaining = max(0, self.requests_per_minute - len(recent_requests))
        
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int((datetime.utcnow() + timedelta(minutes=1)).timestamp())
        )
        
        return response

