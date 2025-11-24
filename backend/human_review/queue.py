"""
Human Review Queue System.
Queue for human reviewers to validate AI decisions.
Scales human oversight as system grows.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Session

from database.models import HumanReview

logger = logging.getLogger(__name__)


class ReviewPriority(str, Enum):
    """Review priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ReviewType(str, Enum):
    """Types of reviews."""
    MATCHING = "matching"
    ASSESSMENT = "assessment"
    MODERATION = "moderation"
    ARTICULATION = "articulation"


class HumanReviewQueue:
    """Manages human review queue."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def add_to_queue(
        self,
        review_type: ReviewType,
        entity_id: str,
        priority: ReviewPriority = ReviewPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> HumanReview:
        """Add item to human review queue."""
        review = HumanReview(
            review_type=review_type.value,
            entity_id=entity_id,
            reviewer_id="",  # Will be assigned when picked up
            decision="pending",
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
        
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        
        logger.info(f"Added {review_type.value}:{entity_id} to review queue (priority: {priority.value})")
        return review
    
    def get_next_review(
        self,
        reviewer_id: str,
        review_type: Optional[ReviewType] = None,
        limit: int = 10
    ) -> List[HumanReview]:
        """Get next items from queue for a reviewer."""
        query = self.db.query(HumanReview).filter(
            HumanReview.decision == "pending"
        )
        
        if review_type:
            query = query.filter(HumanReview.review_type == review_type.value)
        
        # Prioritize by creation time (FIFO with priority consideration)
        reviews = query.order_by(HumanReview.created_at.asc()).limit(limit).all()
        
        # Assign to reviewer
        for review in reviews:
            if not review.reviewer_id:
                review.reviewer_id = reviewer_id
                review.meta_data = (review.meta_data or {})
                review.meta_data["assigned_at"] = datetime.utcnow().isoformat()
        
        self.db.commit()
        return reviews
    
    def complete_review(
        self,
        review_id: int,
        reviewer_id: str,
        decision: str,
        feedback: Optional[str] = None
    ) -> HumanReview:
        """Complete a review."""
        review = self.db.query(HumanReview).filter(
            HumanReview.id == review_id
        ).first()
        
        if not review:
            raise ValueError(f"Review {review_id} not found")
        
        if review.reviewer_id != reviewer_id:
            raise ValueError("Review assigned to different reviewer")
        
        review.decision = decision
        review.feedback = feedback
        review.meta_data = (review.meta_data or {})
        review.meta_data["completed_at"] = datetime.utcnow().isoformat()
        
        self.db.commit()
        self.db.refresh(review)
        
        logger.info(f"Review {review_id} completed: {decision}")
        return review
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        total_pending = self.db.query(HumanReview).filter(
            HumanReview.decision == "pending"
        ).count()
        
        by_type = {}
        for review_type in ReviewType:
            count = self.db.query(HumanReview).filter(
                HumanReview.review_type == review_type.value,
                HumanReview.decision == "pending"
            ).count()
            by_type[review_type.value] = count
        
        return {
            "total_pending": total_pending,
            "by_type": by_type
        }


def create_review_queue(db_session: Session) -> HumanReviewQueue:
    """Factory function to create review queue."""
    return HumanReviewQueue(db_session)


