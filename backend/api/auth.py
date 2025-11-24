"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database.connection import get_db
from backend.database.models import AnonymousUser
from backend.auth.session_manager import create_session_manager

router = APIRouter(prefix="/api/auth", tags=["auth"])


class UserInfoResponse(BaseModel):
    """User information response."""
    anonymous_id: str
    preferred_language: Optional[str] = None
    created_at: str
    last_active: str
    provider: Optional[str] = None  # Login provider (facebook, linkedin, google, etc.)
    provider_display_name: Optional[str] = None  # Human-readable provider name
    meta_data: Optional[dict] = None  # User metadata including social accounts, emails, etc.


@router.get("/user", response_model=UserInfoResponse)
async def get_user_info(
    anonymous_id: str,
    db: Session = Depends(get_db)
):
    """Get user information including preferred language and login provider."""
    user = db.query(AnonymousUser).filter(AnonymousUser.id == anonymous_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    preferred_language = None
    provider = None
    provider_display_name = None
    
    if user.meta_data:
        if "preferred_language" in user.meta_data:
            preferred_language = user.meta_data["preferred_language"]
        
        # Get first provider from social_accounts
        if "social_accounts" in user.meta_data:
            social_accounts = user.meta_data["social_accounts"]
            if social_accounts:
                # Get first provider
                provider = list(social_accounts.keys())[0]
                # Map to display name
                provider_names = {
                    "facebook": "Facebook",
                    "linkedin": "LinkedIn",
                    "google": "Google",
                    "microsoft": "Microsoft",
                    "apple": "Apple",
                    "email": "Email",
                    "sms": "SMS/VoIP"
                }
                provider_display_name = provider_names.get(provider, provider.title())
        # Check for email or phone
        elif "emails" in user.meta_data and user.meta_data["emails"]:
            provider = "email"
            provider_display_name = "Email"
        elif "phone_numbers" in user.meta_data and user.meta_data["phone_numbers"]:
            provider = "sms"
            provider_display_name = "SMS/VoIP"
    
    # Return validated response model
    return UserInfoResponse(
        anonymous_id=user.id,
        preferred_language=preferred_language,
        created_at=user.created_at.isoformat(),
        last_active=user.last_active.isoformat(),
        provider=provider,
        provider_display_name=provider_display_name,
        meta_data=user.meta_data or {}
    )


@router.get("/session")
async def get_session(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current session information from cookie."""
    session_manager = create_session_manager()
    anonymous_id = session_manager.get_anonymous_id(request)
    
    if not anonymous_id:
        raise HTTPException(status_code=401, detail="No active session")
    
    # Get user info
    user = db.query(AnonymousUser).filter(AnonymousUser.id == anonymous_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Extract provider info
    provider = None
    provider_display_name = None
    
    if user.meta_data:
        if "social_accounts" in user.meta_data:
            social_accounts = user.meta_data["social_accounts"]
            if social_accounts:
                provider = list(social_accounts.keys())[0]
                provider_names = {
                    "facebook": "Facebook",
                    "linkedin": "LinkedIn",
                    "google": "Google",
                    "microsoft": "Microsoft",
                    "apple": "Apple",
                    "email": "Email",
                    "sms": "SMS/VoIP"
                }
                provider_display_name = provider_names.get(provider, provider.title())
        elif "emails" in user.meta_data and user.meta_data["emails"]:
            provider = "email"
            provider_display_name = "Email"
        elif "phone_numbers" in user.meta_data and user.meta_data["phone_numbers"]:
            provider = "sms"
            provider_display_name = "SMS/VoIP"
    
    return {
        "authenticated": True,
        "anonymous_id": user.id,
        "provider": provider,
        "provider_display_name": provider_display_name,
        "preferred_language": user.meta_data.get("preferred_language") if user.meta_data else None
    }


@router.post("/logout")
async def logout_post(
    request: Request,
    response: Response
):
    """Logout and destroy session (POST)."""
    session_manager = create_session_manager()
    destroyed = session_manager.destroy_session(request, response)
    
    if not destroyed:
        raise HTTPException(status_code=401, detail="No active session")
    
    return {"message": "Logged out successfully"}


@router.get("/logout")
async def logout_get(
    request: Request,
    response: Response
):
    """Logout and destroy session (GET) - for browser direct access."""
    session_manager = create_session_manager()
    destroyed = session_manager.destroy_session(request, response)
    
    return {
        "message": "Logged out successfully" if destroyed else "No active session found",
        "logged_out": destroyed
    }
