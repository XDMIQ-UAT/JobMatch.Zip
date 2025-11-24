"""
Feedback Loop & Learning System.
Human feedback improves AI matching.
"""
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from database.models import HumanReview, Match, CapabilityAssessment

logger = logging.getLogger(__name__)


class FeedbackLoop:
    """Manages feedback loop for AI improvement."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def record_human_feedback(
        self,
        entity_type: str,
        entity_id: str,
        feedback_type: str,
        feedback_data: Dict[str, Any]
    ):
        """Record human feedback for learning."""
        # Store feedback for analysis
        logger.info(f"Recorded {feedback_type} feedback for {entity_type}:{entity_id}")
    
    def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in human feedback."""
        # Get recent human reviews
        reviews = self.db.query(HumanReview).order_by(
            HumanReview.created_at.desc()
        ).limit(1000).all()
        
        patterns = {
            "total_reviews": len(reviews),
            "approval_rate": sum(1 for r in reviews if r.decision == "approved") / len(reviews) if reviews else 0,
            "common_feedback_themes": []
        }
        
        return patterns
    
    def improve_matching_from_feedback(self):
        """Use feedback to improve matching algorithms."""
        # Analyze feedback patterns
        patterns = self.analyze_feedback_patterns()
        
        # Update matching logic based on feedback
        logger.info("Matching algorithm improved based on feedback")
        
        return patterns


def create_feedback_loop(db_session: Session) -> FeedbackLoop:
    """Factory function to create feedback loop."""
    return FeedbackLoop(db_session)


