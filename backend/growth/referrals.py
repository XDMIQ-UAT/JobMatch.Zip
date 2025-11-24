"""
Referral System for Viral Growth.
"""
import secrets
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.database.models import Referral, AnonymousUser

logger = logging.getLogger(__name__)


class ReferralSystem:
    """Manages referral system for viral growth."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def generate_referral_code(self, user_id: str) -> str:
        """Generate unique referral code for a user."""
        # Check if user already has a referral code
        existing = self.db.query(Referral).filter(
            Referral.referrer_id == user_id
        ).first()
        
        if existing:
            return existing.referral_code
        
        # Generate new code
        code = secrets.token_urlsafe(8).upper()
        
        # Ensure uniqueness
        while self.db.query(Referral).filter(
            Referral.referral_code == code
        ).first():
            code = secrets.token_urlsafe(8).upper()
        
        return code
    
    def create_referral(
        self,
        referrer_id: str,
        referred_id: str,
        referral_code: Optional[str] = None
    ) -> Referral:
        """Create a referral relationship."""
        if not referral_code:
            referral_code = self.generate_referral_code(referrer_id)
        
        referral = Referral(
            referrer_id=referrer_id,
            referred_id=referred_id,
            referral_code=referral_code
        )
        
        self.db.add(referral)
        self.db.commit()
        self.db.refresh(referral)
        
        logger.info(f"Created referral: {referrer_id} -> {referred_id}")
        return referral
    
    def get_referral_by_code(self, code: str) -> Optional[Referral]:
        """Get referral by code."""
        return self.db.query(Referral).filter(
            Referral.referral_code == code
        ).first()
    
    def get_referral_stats(self, user_id: str) -> dict:
        """Get referral statistics for a user."""
        referrals = self.db.query(Referral).filter(
            Referral.referrer_id == user_id
        ).all()
        
        return {
            "total_referrals": len(referrals),
            "referral_code": self.generate_referral_code(user_id)
        }


def create_referral_system(db_session: Session) -> ReferralSystem:
    """Factory function to create referral system."""
    return ReferralSystem(db_session)


