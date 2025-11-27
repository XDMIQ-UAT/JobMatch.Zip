"""
Google OAuth Integration for JobMatch.
Maintains anonymous identity - only uses Google for authentication, not identity.
"""
import logging
import secrets
import base64
from fastapi import APIRouter, HTTPException, Request, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import httpx
import os

from database.connection import get_db
from database.models import AnonymousUser
from auth.social_auth import create_social_auth_manager
from auth.session_manager import create_session_manager
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth/google", tags=["google-oauth"])

# Store OAuth state temporarily (use Redis in production)
_oauth_states: Dict[str, Dict[str, Any]] = {}


@router.get("/login")
async def google_login(
    request: Request,
    redirect_uri: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Initiate Google OAuth login flow.
    Creates anonymous identity and links Google account without storing name.
    """
    # Check for Google OAuth credentials (prefer GOOGLE_OAUTH_* names)
    google_client_id = settings.GOOGLE_OAUTH_CLIENT_ID or settings.GOOGLE_CLIENT_ID
    google_client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET or settings.GOOGLE_CLIENT_SECRET
    
    if not google_client_id or not google_client_secret:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured. Please set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET"
        )
    
    # Generate secure state token
    state_token = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    # Determine redirect URI
    frontend_url = os.getenv('FRONTEND_URL', 'https://jobmatch.zip')
    callback_uri = redirect_uri or f"{frontend_url}/api/auth/google/callback"
    backend_callback = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/auth/google/callback"
    
    # Store state with callback info
    _oauth_states[state_token] = {
        "redirect_uri": callback_uri,
        "created_at": datetime.utcnow()
    }
    
    # Get Google OAuth credentials (prefer GOOGLE_OAUTH_* names)
    google_client_id = settings.GOOGLE_OAUTH_CLIENT_ID or settings.GOOGLE_CLIENT_ID
    google_client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET or settings.GOOGLE_CLIENT_SECRET
    
    # Build Google OAuth URL
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": google_client_id,
        "redirect_uri": backend_callback,
        "response_type": "code",
        "scope": "openid email profile",  # Request email and profile, but we won't store name
        "state": state_token,
        "access_type": "offline",
        "prompt": "consent"  # Force consent to get refresh token
    }
    
    auth_url = f"{google_auth_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    logger.info(f"Google OAuth initiated with state: {state_token[:16]}...")
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def google_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback.
    Exchanges code for token, gets user info, but only stores email (not name).
    Creates/links anonymous identity.
    """
    if error:
        logger.error(f"Google OAuth error: {error}")
        frontend_url = os.getenv('FRONTEND_URL', 'https://jobmatch.zip')
        return RedirectResponse(url=f"{frontend_url}/auth?error=oauth_cancelled")
    
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")
    
    # Verify state
    state_data = _oauth_states.get(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired state token")
    
    # Remove used state
    del _oauth_states[state]
    
    try:
        # Exchange code for token
        backend_callback = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/auth/google/callback"
        
        # Get Google OAuth credentials (prefer GOOGLE_OAUTH_* names)
        google_client_id = settings.GOOGLE_OAUTH_CLIENT_ID or settings.GOOGLE_CLIENT_ID
        google_client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET or settings.GOOGLE_CLIENT_SECRET
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": google_client_id,
                    "client_secret": google_client_secret,
                    "code": code,
                    "redirect_uri": backend_callback,
                    "grant_type": "authorization_code"
                }
            )
            
            if token_response.status_code != 200:
                logger.error(f"Token exchange failed: {token_response.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(status_code=400, detail="No access token received")
            
            # Get user info from Google
            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_info_response.status_code != 200:
                logger.error(f"User info fetch failed: {user_info_response.text}")
                raise HTTPException(status_code=400, detail="Failed to fetch user info")
            
            user_info = user_info_response.json()
            
            # Extract only what we need - email and locale (NOT name)
            provider_data = {
                "email": user_info.get("email"),
                "locale": user_info.get("locale"),  # For language preference
                "verified_email": user_info.get("verified_email", False)
            }
            
            # Get Google user ID (sub claim)
            provider_user_id = user_info.get("id") or user_info.get("sub")
            
            if not provider_user_id:
                raise HTTPException(status_code=400, detail="No user ID received from Google")
            
            # Authenticate with social auth manager (creates/links anonymous identity)
            manager = create_social_auth_manager(db)
            anonymous_id = manager.authenticate_with_provider(
                provider="google",
                provider_token=access_token,
                provider_data=provider_data
            )
            
            if not anonymous_id:
                raise HTTPException(status_code=401, detail="Failed to create anonymous identity")
            
            # Create session
            session_manager = create_session_manager()
            frontend_url = os.getenv('FRONTEND_URL', 'https://jobmatch.zip')
            redirect_url = f"{frontend_url}/dashboard?authenticated=true"
            
            # Create response with redirect
            response = RedirectResponse(url=redirect_url)
            
            # Set session cookie
            session_manager.create_session(
                anonymous_id=anonymous_id,
                response=response,
                additional_data={
                    "provider": "google",
                    "authenticated_at": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Google OAuth successful for anonymous_id: {anonymous_id[:8]}...")
            return response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}", exc_info=True)
        frontend_url = os.getenv('FRONTEND_URL', 'https://jobmatch.zip')
        return RedirectResponse(url=f"{frontend_url}/auth?error=oauth_failed")


@router.get("/status")
async def google_auth_status(
    request: Request,
    db: Session = Depends(get_db)
):
    """Check if user has Google account linked (without revealing identity)."""
    from auth.session_manager import get_session_from_request
    session = get_session_from_request(request)
    
    if not session:
        return {"linked": False, "provider": None}
    
    anonymous_id = session.get("anonymous_id")
    if not anonymous_id:
        return {"linked": False, "provider": None}
    
    user = db.query(AnonymousUser).filter(AnonymousUser.id == anonymous_id).first()
    if not user:
        return {"linked": False, "provider": None}
    
    # Check if Google is linked (without revealing details)
    if user.meta_data and "social_accounts" in user.meta_data:
        if "google" in user.meta_data["social_accounts"]:
            return {
                "linked": True,
                "provider": "google",
                "anonymous_id": anonymous_id
            }
    
    return {"linked": False, "provider": None}


import logging

