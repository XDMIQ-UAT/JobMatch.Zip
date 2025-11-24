"""
Social Authentication API endpoints.
Supports: Facebook, LinkedIn, Google, Microsoft, Apple, Email, SMS/VoIP
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

from backend.database.connection import get_db
from backend.database.models import AnonymousUser
from backend.auth.social_auth import create_social_auth_manager
from backend.auth.session_manager import create_session_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth/social", tags=["social-auth"])


class SocialAuthRequest(BaseModel):
    """Request for social authentication."""
    provider: str  # facebook, linkedin, google, microsoft, apple
    provider_token: str
    provider_data: Optional[Dict[str, Any]] = None


class SocialAuthResponse(BaseModel):
    """Response for social authentication."""
    anonymous_id: str
    provider: str
    message: str


class LinkSocialRequest(BaseModel):
    """Request to link social account."""
    anonymous_id: str
    provider: str
    provider_token: str
    provider_data: Optional[Dict[str, Any]] = None


class SMSVerificationRequest(BaseModel):
    """Request for SMS verification."""
    phone_number: str


class SMSVerifyRequest(BaseModel):
    """Request to verify SMS code."""
    phone_number: str
    code: str


class EmailVerificationRequest(BaseModel):
    """Request for email verification."""
    email: EmailStr


class EmailVerifyRequest(BaseModel):
    """Request to verify email code."""
    email: EmailStr
    code: str


class MagicLinkRequest(BaseModel):
    """Request for magic link."""
    email: EmailStr
    base_url: Optional[str] = "https://jobmatch.zip"


@router.post("/authenticate", response_model=SocialAuthResponse)
async def authenticate_with_social(
    request: SocialAuthRequest,
    db: Session = Depends(get_db)
):
    """Authenticate with social provider (Facebook, LinkedIn, Google, Microsoft, Apple)."""
    if request.provider not in ["facebook", "linkedin", "google", "microsoft", "apple"]:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    # Fetch user info from provider to get locale
    from backend.auth.oauth_providers import create_oauth_manager
    oauth_manager = create_oauth_manager()
    
    provider_data = request.provider_data
    if not provider_data:
        try:
            # Fetch user info from provider API
            user_info = await oauth_manager.get_user_info(
                provider=request.provider,
                access_token=request.provider_token
            )
            provider_data = user_info
        except Exception as e:
            logger.warning(f"Could not fetch user info from {request.provider}: {e}")
            provider_data = {}
    
    manager = create_social_auth_manager(db)
    anonymous_id = manager.authenticate_with_provider(
        provider=request.provider,
        provider_token=request.provider_token,
        provider_data=provider_data
    )
    
    if not anonymous_id:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    # Get preferred language from user
    user = db.query(AnonymousUser).filter(AnonymousUser.id == anonymous_id).first()
    preferred_language = None
    if user and user.meta_data and "preferred_language" in user.meta_data:
        preferred_language = user.meta_data["preferred_language"]
    
    return SocialAuthResponse(
        anonymous_id=anonymous_id,
        provider=request.provider,
        message=f"Authenticated with {request.provider}"
    )


@router.post("/link", response_model=Dict[str, Any])
async def link_social_account(
    request: LinkSocialRequest,
    db: Session = Depends(get_db)
):
    """Link social account to existing anonymous identity."""
    manager = create_social_auth_manager(db)
    
    # Verify token and get provider user ID
    provider_user_id = manager._verify_provider_token(
        request.provider,
        request.provider_token
    )
    
    if not provider_user_id:
        raise HTTPException(status_code=401, detail="Invalid provider token")
    
    success = manager.link_social_account(
        anonymous_id=request.anonymous_id,
        provider=request.provider,
        provider_user_id=provider_user_id,
        provider_data=request.provider_data
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to link account")
    
    return {
        "message": f"Linked {request.provider} account successfully",
        "anonymous_id": request.anonymous_id
    }


@router.post("/sms/send", response_model=Dict[str, Any])
async def send_sms_verification(
    request: SMSVerificationRequest,
    db: Session = Depends(get_db)
):
    """Send SMS verification code."""
    manager = create_social_auth_manager(db)
    result = manager.send_sms_verification(request.phone_number)
    
    return {
        "message": "SMS verification code sent",
        "phone_number": request.phone_number,
        "expires_in": result["expires_in"]
    }


@router.post("/sms/verify", response_model=SocialAuthResponse)
async def verify_sms_code(
    request: SMSVerifyRequest,
    db: Session = Depends(get_db)
):
    """Verify SMS code and authenticate."""
    manager = create_social_auth_manager(db)
    anonymous_id = manager.verify_sms_code(
        phone_number=request.phone_number,
        code=request.code
    )
    
    if not anonymous_id:
        raise HTTPException(status_code=401, detail="Invalid verification code")
    
    return SocialAuthResponse(
        anonymous_id=anonymous_id,
        provider="sms",
        message="SMS verified successfully"
    )


@router.post("/email/send", response_model=Dict[str, Any])
async def send_email_verification(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """Send email verification code."""
    try:
        manager = create_social_auth_manager(db)
        result = manager.send_email_verification(request.email)
        
        response = {
            "message": "Email verification code sent",
            "email": request.email,
            "expires_in": result["expires_in"]
        }
        
        # Include verification code in dev mode for testing
        from backend.config import settings
        if getattr(settings, 'ENVIRONMENT', 'production') == 'development' or getattr(settings, 'DEV_MODE', False):
            response["verification_code"] = result.get("verification_code")
        
        return response
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send email verification to {redact_email(request.email)}: {error_msg}", exc_info=True)
        
        # Provide user-friendly error message without technical details
        detail = "Unable to send verification email. Please try again or contact support if the issue persists."
        
        raise HTTPException(
            status_code=500,
            detail=detail
        )


@router.post("/email/verify")
async def verify_email_code(
    request: EmailVerifyRequest,
    db: Session = Depends(get_db)
):
    """Verify email code and authenticate with session cookie."""
    try:
        manager = create_social_auth_manager(db)
        anonymous_id = manager.verify_email_code(
            email=request.email,
            code=request.code
        )
        
        if not anonymous_id:
            logger.warning(f"Email verification failed for {redact_email(request.email)}")
            raise HTTPException(
                status_code=401, 
                detail="Invalid or expired verification code. Please request a new code."
            )
        
        # Create session and set secure cookie
        from fastapi.responses import JSONResponse
        response = JSONResponse({
            "success": True,
            "anonymous_id": anonymous_id,
            "provider": "email",
            "message": "Email verified successfully"
        })
        
        session_manager = create_session_manager()
        session_manager.create_session(
            anonymous_id=anonymous_id,
            response=response,
            additional_data={
                "provider": "email",
                "authenticated_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Email verified and session created for user {anonymous_id[:8]}...")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying email code: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during verification. Please try again."
        )


def _get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address from request."""
    # Check X-Forwarded-For header (for proxies/load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP (original client)
        return forwarded_for.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct client IP
    if request.client:
        return request.client.host
    
    return None


@router.post("/email/magic-link", response_model=Dict[str, Any])
async def send_magic_link(
    request: MagicLinkRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Send magic link email (valid for 24 hours)."""
    try:
        # Get client IP for security validation
        client_ip = _get_client_ip(http_request) if http_request else None
        
        manager = create_social_auth_manager(db)
        result = manager.send_magic_link(
            email=request.email,
            base_url=request.base_url or "https://jobmatch.zip",
            request_ip=client_ip
        )
        
        response = {
            "message": "Magic link sent successfully",
            "email": request.email,
            "expires_in": result["expires_in"]
        }
        
        # Include magic link in dev mode for testing
        from backend.config import settings
        if getattr(settings, 'ENVIRONMENT', 'production') == 'development' or getattr(settings, 'DEV_MODE', False):
            response["magic_link"] = result.get("magic_link")
            logger.info(f"Magic link returned in response: {result.get('magic_link')}")
        
        return response
    except Exception as e:
        logger.error(f"Failed to send magic link: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send magic link: {str(e)}"
        )


@router.get("/magic-link/verify")
async def verify_magic_link(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify magic link token and authenticate with session cookie."""
    try:
        # Get client IP for security validation
        client_ip = _get_client_ip(request)
        
        # In development, allow IP validation to be skipped
        from backend.config import settings
        validate_ip = getattr(settings, 'ENVIRONMENT', 'production') == 'production'
        
        manager = create_social_auth_manager(db)
        anonymous_id = manager.verify_magic_link(
            token,
            request_ip=client_ip,
            validate_ip=validate_ip
        )
        
        if not anonymous_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired magic link. Please request a new one."
            )
        
        # Create session and set secure cookie
        from fastapi.responses import JSONResponse
        response = JSONResponse({
            "success": True,
            "anonymous_id": anonymous_id,
            "provider": "email",
            "message": "Magic link verified successfully"
        })
        
        session_manager = create_session_manager()
        session_manager.create_session(
            anonymous_id=anonymous_id,
            response=response,
            additional_data={
                "provider": "email",
                "authenticated_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Magic link verified and session created for user {anonymous_id[:8]}...")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying magic link: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during verification. Please try again."
        )


@router.post("/unlink", response_model=Dict[str, Any])
async def unlink_social_account(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Unlink social account from anonymous identity."""
    anonymous_id = request.get("anonymous_id")
    provider = request.get("provider")
    
    if not anonymous_id or not provider:
        raise HTTPException(status_code=400, detail="anonymous_id and provider are required")
    
    manager = create_social_auth_manager(db)
    user = manager.identity_manager.get_user(anonymous_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove provider from social_accounts
    if user.meta_data and "social_accounts" in user.meta_data:
        if provider in user.meta_data["social_accounts"]:
            del user.meta_data["social_accounts"][provider]
            db.commit()
            logger.info(f"Unlinked {provider} account from anonymous user {anonymous_id[:8]}...")
            return {
                "message": f"Unlinked {provider} account successfully",
                "anonymous_id": anonymous_id
            }
    
    # Also check emails/phone_numbers
    if provider == "email" and user.meta_data and "emails" in user.meta_data:
        user.meta_data["emails"] = []
        db.commit()
        return {
            "message": "Unlinked email account successfully",
            "anonymous_id": anonymous_id
        }
    
    if provider == "sms" and user.meta_data and "phone_numbers" in user.meta_data:
        user.meta_data["phone_numbers"] = []
        db.commit()
        return {
            "message": "Unlinked SMS account successfully",
            "anonymous_id": anonymous_id
        }
    
    raise HTTPException(status_code=404, detail="Account not linked")


@router.get("/email/debug/{email}")
async def debug_email_code(
    email: str,
    db: Session = Depends(get_db)
):
    """Debug endpoint to check email verification code status (dev only)."""
    from backend.config import settings
    if getattr(settings, 'ENVIRONMENT', 'production') != 'development' and not getattr(settings, 'DEV_MODE', False):
        raise HTTPException(status_code=403, detail="Debug endpoint only available in development mode")
    
    manager = create_social_auth_manager(db)
    # Access the codes dict through the manager's module
    import backend.auth.social_auth as social_auth_module
    email_lower = email.lower()
    stored_data = social_auth_module._email_verification_codes.get(email_lower)
    
    if not stored_data:
        return {
            "email": email,
            "email_lower": email_lower,
            "status": "no_code",
            "message": "No verification code found for this email",
            "available_emails": list(social_auth_module._email_verification_codes.keys())
        }
    
    from datetime import datetime
    now = datetime.utcnow()
    expires_at = stored_data["expires_at"]
    is_expired = now > expires_at
    time_remaining = (expires_at - now).total_seconds() if not is_expired else 0
    
    return {
        "email": email,
        "email_lower": email_lower,
        "status": "expired" if is_expired else "active",
        "code": stored_data["code"],
        "created_at": stored_data["created_at"].isoformat(),
        "expires_at": expires_at.isoformat(),
        "is_expired": is_expired,
        "time_remaining_seconds": int(time_remaining),
        "time_remaining_minutes": round(time_remaining / 60, 1) if time_remaining > 0 else 0
    }


@router.get("/providers")
async def list_providers():
    """List available authentication providers."""
    return {
        "providers": [
            {
                "id": "facebook",
                "name": "Facebook",
                "type": "oauth"
            },
            {
                "id": "linkedin",
                "name": "LinkedIn",
                "type": "oauth"
            },
            {
                "id": "google",
                "name": "Google",
                "type": "oauth"
            },
            {
                "id": "microsoft",
                "name": "Microsoft",
                "type": "oauth"
            },
            {
                "id": "apple",
                "name": "Apple",
                "type": "oauth"
            },
            {
                "id": "email",
                "name": "Email",
                "type": "email_verification"
            },
            {
                "id": "sms",
                "name": "SMS/VoIP",
                "type": "sms_verification"
            }
        ]
    }


