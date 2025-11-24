"""
Referral API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database.connection import get_db
from backend.growth.referrals import create_referral_system

router = APIRouter(prefix="/api/referrals", tags=["referrals"])


class ReferralRequest(BaseModel):
    """Request model for referral."""
    referrer_id: str
    referred_id: str
    referral_code: str = None


class ReferralResponse(BaseModel):
    """Response model for referral."""
    referral_id: int
    referrer_id: str
    referred_id: str
    referral_code: str
    created_at: str


@router.post("/create", response_model=ReferralResponse)
async def create_referral(
    request: ReferralRequest,
    db: Session = Depends(get_db)
):
    """Create a referral."""
    system = create_referral_system(db)
    
    referral = system.create_referral(
        referrer_id=request.referrer_id,
        referred_id=request.referred_id,
        referral_code=request.referral_code
    )
    
    return ReferralResponse(
        referral_id=referral.id,
        referrer_id=referral.referrer_id,
        referred_id=referral.referred_id,
        referral_code=referral.referral_code,
        created_at=referral.created_at.isoformat()
    )


@router.get("/code/{code}")
async def get_referral_by_code(
    code: str,
    db: Session = Depends(get_db)
):
    """Get referral by code."""
    system = create_referral_system(db)
    referral = system.get_referral_by_code(code)
    
    if not referral:
        raise HTTPException(status_code=404, detail="Referral code not found")
    
    return {
        "referrer_id": referral.referrer_id,
        "referral_code": referral.referral_code
    }


@router.get("/stats/{user_id}")
async def get_referral_stats(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get referral statistics."""
    system = create_referral_system(db)
    stats = system.get_referral_stats(user_id)
    
    return stats


