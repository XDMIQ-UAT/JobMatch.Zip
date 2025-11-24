"""
AI Moderation & Facilitation.
Human-in-the-Loop: AI flags, humans make final decisions.
"""
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from openai import OpenAI
from backend.config import settings
from backend.database.models import ForumPost
from backend.resilience.state_management import StateManager, CheckpointType

logger = logging.getLogger(__name__)


class ModerationEngine:
    """AI moderation with human oversight."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.state_manager = StateManager(db_session)
    
    def moderate_content(
        self,
        content: str,
        content_type: str = "forum_post"
    ) -> Dict[str, Any]:
        """
        Moderate content with AI, flagging for human review.
        Human-in-the-Loop: AI flags, humans make final decisions.
        """
        moderation_result = self._analyze_with_ai(content)
        
        # Create checkpoint
        checkpoint = self.state_manager.create_checkpoint(
            checkpoint_type=CheckpointType.MODERATION,
            entity_id=f"{content_type}:{hash(content)}",
            state_data={
                "content": content,
                "content_type": content_type,
                "moderation_result": moderation_result
            }
        )
        
        return {
            "flagged": moderation_result.get("flagged", False),
            "reasons": moderation_result.get("reasons", []),
            "needs_human_review": moderation_result.get("needs_human_review", False),
            "checkpoint_id": checkpoint.id
        }
    
    def _analyze_with_ai(self, content: str) -> Dict[str, Any]:
        """Use AI to analyze content."""
        if not self.openai_client:
            return self._fallback_analysis(content)
        
        try:
            prompt = f"""
            Analyze this content for:
            1. Credentialism (requiring degrees over capabilities)
            2. Gatekeeping language
            3. Bias against LLC/independent contractors
            4. Inappropriate content
            
            Content: {content}
            
            Return JSON with flagged (boolean), reasons (list), and needs_human_review (boolean).
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You moderate content for bias and gatekeeping."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse response (simplified)
            return {
                "flagged": "flagged" in response.choices[0].message.content.lower(),
                "reasons": [],
                "needs_human_review": True
            }
        except Exception as e:
            logger.error(f"AI moderation failed: {e}")
            return self._fallback_analysis(content)
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback analysis when AI unavailable."""
        flagged_keywords = ["degree required", "must have phd", "ivy league"]
        flagged = any(keyword in content.lower() for keyword in flagged_keywords)
        
        return {
            "flagged": flagged,
            "reasons": ["Credentialism detected"] if flagged else [],
            "needs_human_review": flagged
        }


def create_moderation_engine(db_session: Session) -> ModerationEngine:
    """Factory function to create moderation engine."""
    return ModerationEngine(db_session)


