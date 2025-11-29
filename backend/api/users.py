"""
User Management API endpoints.
Provides GDPR-compliant data deletion and user account management.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

from database.connection import get_db
from database.models import (
    AnonymousUser, LLCProfile, CapabilityAssessment, Match,
    ArticulationSuggestion, ForumPost, Referral,
    MarketplaceListing, MarketplaceTransaction
)
from security.pii_redaction import redact_anonymous_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])


class ProfileUpdateRequest(BaseModel):
    """Request model for updating profile."""
    skills: List[str]
    portfolio_url: Optional[str] = None
    work_preference: Optional[str] = None
    bio: Optional[str] = None
    projects: Optional[List[Dict[str, Any]]] = None


class UserDeleteResponse(BaseModel):
    """Response for user deletion request."""
    success: bool
    message: str
    anonymous_id: str
    deleted_at: str
    data_deleted: Dict[str, int]  # Count of deleted records by type


@router.delete("/{anonymous_id}", response_model=UserDeleteResponse)
async def delete_user_data(
    anonymous_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete all user data (GDPR Right to be Forgotten / CCPA Right to Delete).
    
    This endpoint performs CASCADE deletion of:
    - Anonymous user profile
    - LLC profiles
    - Capability assessments
    - Job matches
    - Articulation suggestions
    - Forum posts
    - Referrals
    - Marketplace listings
    - Marketplace transactions
    
    Args:
        anonymous_id: The anonymous user ID to delete
        db: Database session
        
    Returns:
        UserDeleteResponse with deletion summary
        
    Raises:
        HTTPException: 404 if user not found, 500 on deletion error
    """
    try:
        # Check if user exists
        user = db.query(AnonymousUser).filter(AnonymousUser.id == anonymous_id).first()
        if not user:
            logger.warning(f"Delete request for non-existent user: {redact_anonymous_id(anonymous_id)}")
            raise HTTPException(
                status_code=404,
                detail=f"User not found: {anonymous_id}"
            )
        
        logger.info(f"Starting data deletion for user: {redact_anonymous_id(anonymous_id)}")
        
        # Track deletion counts
        deletion_counts = {}
        
        # Delete LLC Profiles
        profiles_deleted = db.query(LLCProfile).filter(
            LLCProfile.user_id == anonymous_id
        ).delete(synchronize_session=False)
        deletion_counts["profiles"] = profiles_deleted
        
        # Delete Capability Assessments
        assessments_deleted = db.query(CapabilityAssessment).filter(
            CapabilityAssessment.user_id == anonymous_id
        ).delete(synchronize_session=False)
        deletion_counts["assessments"] = assessments_deleted
        
        # Delete Matches
        matches_deleted = db.query(Match).filter(
            Match.user_id == anonymous_id
        ).delete(synchronize_session=False)
        deletion_counts["matches"] = matches_deleted
        
        # Delete Articulation Suggestions
        suggestions_deleted = db.query(ArticulationSuggestion).filter(
            ArticulationSuggestion.user_id == anonymous_id
        ).delete(synchronize_session=False)
        deletion_counts["articulation_suggestions"] = suggestions_deleted
        
        # Delete Forum Posts
        posts_deleted = db.query(ForumPost).filter(
            ForumPost.user_id == anonymous_id
        ).delete(synchronize_session=False)
        deletion_counts["forum_posts"] = posts_deleted
        
        # Delete Referrals (both as referrer and referred)
        referrals_as_referrer = db.query(Referral).filter(
            Referral.referrer_id == anonymous_id
        ).delete(synchronize_session=False)
        
        referrals_as_referred = db.query(Referral).filter(
            Referral.referred_id == anonymous_id
        ).delete(synchronize_session=False)
        
        deletion_counts["referrals"] = referrals_as_referrer + referrals_as_referred
        
        # Delete Marketplace Listings
        listings_deleted = db.query(MarketplaceListing).filter(
            MarketplaceListing.seller_id == anonymous_id
        ).delete(synchronize_session=False)
        deletion_counts["marketplace_listings"] = listings_deleted
        
        # Delete Marketplace Transactions (as buyer or seller)
        transactions_as_buyer = db.query(MarketplaceTransaction).filter(
            MarketplaceTransaction.buyer_id == anonymous_id
        ).delete(synchronize_session=False)
        
        transactions_as_seller = db.query(MarketplaceTransaction).filter(
            MarketplaceTransaction.seller_id == anonymous_id
        ).delete(synchronize_session=False)
        
        deletion_counts["marketplace_transactions"] = transactions_as_buyer + transactions_as_seller
        
        # Finally, delete the anonymous user record
        db.delete(user)
        
        # Commit all deletions
        db.commit()
        
        deleted_at = datetime.utcnow().isoformat()
        total_records = sum(deletion_counts.values())
        
        logger.info(
            f"Successfully deleted user {redact_anonymous_id(anonymous_id)}: "
            f"{total_records} records across {len(deletion_counts)} data types"
        )
        
        # Create audit trail entry (could be logged to separate audit database)
        logger.info(f"GDPR DELETION AUDIT: {deletion_counts}")
        
        return UserDeleteResponse(
            success=True,
            message=f"All user data deleted successfully ({total_records} records)",
            anonymous_id=anonymous_id,
            deleted_at=deleted_at,
            data_deleted=deletion_counts
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Rollback on error
        db.rollback()
        logger.error(
            f"Failed to delete user data for {redact_anonymous_id(anonymous_id)}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user data: {str(e)}"
        )


@router.get("/{anonymous_id}/data-summary")
async def get_user_data_summary(
    anonymous_id: str,
    db: Session = Depends(get_db)
):
    """
    Get summary of user data (GDPR Right to Access).
    
    Returns a count of all data associated with the user without
    exposing the actual content.
    
    Args:
        anonymous_id: The anonymous user ID
        db: Database session
        
    Returns:
        Dict with counts of user data by type
    """
    try:
        # Check if user exists
        user = db.query(AnonymousUser).filter(AnonymousUser.id == anonymous_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User not found: {anonymous_id}"
            )
        
        # Count all user data
        data_summary = {
            "anonymous_id": anonymous_id,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_active": user.last_active.isoformat() if user.last_active else None,
            "data_counts": {
                "profiles": db.query(LLCProfile).filter(
                    LLCProfile.user_id == anonymous_id
                ).count(),
                "assessments": db.query(CapabilityAssessment).filter(
                    CapabilityAssessment.user_id == anonymous_id
                ).count(),
                "matches": db.query(Match).filter(
                    Match.user_id == anonymous_id
                ).count(),
                "articulation_suggestions": db.query(ArticulationSuggestion).filter(
                    ArticulationSuggestion.user_id == anonymous_id
                ).count(),
                "forum_posts": db.query(ForumPost).filter(
                    ForumPost.user_id == anonymous_id
                ).count(),
                "referrals": db.query(Referral).filter(
                    (Referral.referrer_id == anonymous_id) | 
                    (Referral.referred_id == anonymous_id)
                ).count(),
                "marketplace_listings": db.query(MarketplaceListing).filter(
                    MarketplaceListing.seller_id == anonymous_id
                ).count(),
                "marketplace_transactions": db.query(MarketplaceTransaction).filter(
                    (MarketplaceTransaction.buyer_id == anonymous_id) |
                    (MarketplaceTransaction.seller_id == anonymous_id)
                ).count(),
            }
        }
        
        total_records = sum(data_summary["data_counts"].values())
        data_summary["total_records"] = total_records
        
        logger.info(f"Data summary requested for user {redact_anonymous_id(anonymous_id)}: {total_records} records")
        
        return data_summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get data summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve data summary: {str(e)}"
        )


@router.get("/{anonymous_id}/profile")
async def get_user_profile(
    anonymous_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user's LLC profile.
    
    Args:
        anonymous_id: The anonymous user ID
        db: Database session
        
    Returns:
        Profile data including skills, portfolio, work preferences
    """
    try:
        # Check if user exists
        user = db.query(AnonymousUser).filter(AnonymousUser.id == anonymous_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User not found: {anonymous_id}"
            )
        
        # Get or create profile
        profile = db.query(LLCProfile).filter(
            LLCProfile.user_id == anonymous_id
        ).first()
        
        if not profile:
            return {
                "anonymous_id": anonymous_id,
                "skills": [],
                "portfolio_url": None,
                "work_preference": None,
                "bio": None,
                "projects": []
            }
        
        projects = profile.projects if profile.projects else []
        experience_summary = profile.experience_summary or ""
        
        return {
            "anonymous_id": anonymous_id,
            "skills": profile.skills if profile.skills else [],
            "portfolio_url": projects[0].get("url") if projects and len(projects) > 0 else None,
            "work_preference": experience_summary.split("\n")[0] if experience_summary else None,
            "bio": experience_summary if experience_summary else None,
            "projects": projects
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve profile: {str(e)}"
        )


@router.put("/{anonymous_id}/profile")
async def update_user_profile(
    anonymous_id: str,
    request: ProfileUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update or create user's LLC profile.
    
    Args:
        anonymous_id: The anonymous user ID
        request: Profile update data
        db: Database session
        
    Returns:
        Updated profile data
    """
    try:
        # Check if user exists, create if not
        user = db.query(AnonymousUser).filter(AnonymousUser.id == anonymous_id).first()
        if not user:
            user = AnonymousUser(
                id=anonymous_id,
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow()
            )
            db.add(user)
            db.flush()
        
        # Get or create profile
        profile = db.query(LLCProfile).filter(
            LLCProfile.user_id == anonymous_id
        ).first()
        
        # Prepare projects list
        projects = request.projects or []
        if request.portfolio_url:
            # Add portfolio URL as a project if not already present
            if not any(p.get("url") == request.portfolio_url for p in projects):
                projects.insert(0, {"url": request.portfolio_url, "type": "portfolio"})
        
        # Prepare experience summary
        experience_parts = []
        if request.work_preference:
            experience_parts.append(request.work_preference)
        if request.bio:
            experience_parts.append(request.bio)
        experience_summary = "\n".join(experience_parts) if experience_parts else None
        
        if profile:
            # Update existing profile
            profile.skills = request.skills
            profile.projects = projects
            profile.experience_summary = experience_summary
            profile.updated_at = datetime.utcnow()
        else:
            # Create new profile
            profile = LLCProfile(
                user_id=anonymous_id,
                skills=request.skills,
                projects=projects,
                experience_summary=experience_summary
            )
            db.add(profile)
        
        # Update user's last_active
        user.last_active = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Profile updated for user {redact_anonymous_id(anonymous_id)}")
        
        return {
            "success": True,
            "anonymous_id": anonymous_id,
            "skills": profile.skills,
            "portfolio_url": request.portfolio_url,
            "work_preference": request.work_preference,
            "bio": request.bio,
            "projects": projects,
            "updated_at": profile.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update profile: {str(e)}"
        )
