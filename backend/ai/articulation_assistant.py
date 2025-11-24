"""
Capability Articulation Assistant.
Helps LLC owners translate their AI work into job market terms.
Human-in-the-Loop: AI suggests language, humans refine.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from openai import OpenAI
from config import settings
from database.models import ArticulationSuggestion, AnonymousUser
from resilience.state_management import StateManager, CheckpointType

logger = logging.getLogger(__name__)


class ArticulationAssistant:
    """Assists users in articulating their AI capabilities."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.state_manager = StateManager(db_session)
    
    def suggest_articulation(
        self,
        user_id: str,
        original_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ArticulationSuggestion:
        """
        Generate language suggestions for articulating capabilities.
        Human-in-the-Loop: AI suggests, humans refine.
        """
        # Get user's latest assessment for context
        from database.models import CapabilityAssessment
        assessment = self.db.query(CapabilityAssessment).filter(
            CapabilityAssessment.user_id == user_id
        ).order_by(CapabilityAssessment.created_at.desc()).first()
        
        # AI generates suggestion
        suggested_text = self._generate_suggestion(original_text, assessment, context)
        
        # Get latest version number
        latest = self.db.query(ArticulationSuggestion).filter(
            ArticulationSuggestion.user_id == user_id
        ).order_by(ArticulationSuggestion.version.desc()).first()
        
        version = (latest.version + 1) if latest else 1
        
        # Create suggestion record
        suggestion = ArticulationSuggestion(
            user_id=user_id,
            original_text=original_text,
            suggested_text=suggested_text,
            version=version,
            human_refined=False
        )
        
        self.db.add(suggestion)
        self.db.commit()
        self.db.refresh(suggestion)
        
        # Create checkpoint
        checkpoint = self.state_manager.create_checkpoint(
            checkpoint_type=CheckpointType.ARTICULATION,
            entity_id=str(suggestion.id),
            state_data={
                "suggestion_id": suggestion.id,
                "user_id": user_id,
                "original_text": original_text,
                "suggested_text": suggested_text,
                "version": version,
                "created_at": suggestion.created_at.isoformat()
            }
        )
        
        suggestion.checkpoint_id = checkpoint.id
        self.db.commit()
        
        return suggestion
    
    def _generate_suggestion(
        self,
        original_text: str,
        assessment: Optional[Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Use AI to generate articulation suggestion."""
        if not self.openai_client:
            return self._fallback_suggestion(original_text)
        
        try:
            assessment_context = ""
            if assessment:
                strengths = assessment.results.get("strengths", [])
                assessment_context = f"User's strengths: {', '.join(strengths)}"
            
            prompt = f"""
            Translate this description of AI work into professional job market language:
            
            Original: {original_text}
            {assessment_context}
            
            Requirements:
            - Use industry-standard terminology
            - Highlight practical AI capabilities
            - Remove credential-focused language
            - Focus on what was accomplished, not credentials
            - Make it compelling for employers seeking AI talent
            
            Return only the improved text.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You help LLC owners articulate their AI capabilities professionally."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"AI suggestion failed: {e}")
            return self._fallback_suggestion(original_text)
    
    def _fallback_suggestion(self, original_text: str) -> str:
        """Fallback when AI unavailable."""
        # Simple improvements
        text = original_text
        # Add action verbs if missing
        if not any(word in text.lower() for word in ["built", "created", "developed", "implemented"]):
            text = f"Developed {text.lower()}"
        return text
    
    def human_refine_suggestion(
        self,
        suggestion_id: int,
        refined_text: str
    ) -> ArticulationSuggestion:
        """Human refines AI suggestion."""
        suggestion = self.db.query(ArticulationSuggestion).filter(
            ArticulationSuggestion.id == suggestion_id
        ).first()
        
        if not suggestion:
            raise ValueError(f"Suggestion {suggestion_id} not found")
        
        # Create new version with human refinement
        new_suggestion = ArticulationSuggestion(
            user_id=suggestion.user_id,
            original_text=suggestion.original_text,
            suggested_text=refined_text,
            version=suggestion.version + 1,
            human_refined=True
        )
        
        self.db.add(new_suggestion)
        self.db.commit()
        self.db.refresh(new_suggestion)
        
        # Create checkpoint
        checkpoint = self.state_manager.create_checkpoint(
            checkpoint_type=CheckpointType.ARTICULATION,
            entity_id=str(new_suggestion.id),
            state_data={
                "suggestion_id": new_suggestion.id,
                "user_id": new_suggestion.user_id,
                "original_text": new_suggestion.original_text,
                "suggested_text": new_suggestion.suggested_text,
                "version": new_suggestion.version,
                "human_refined": True,
                "created_at": new_suggestion.created_at.isoformat()
            }
        )
        
        new_suggestion.checkpoint_id = checkpoint.id
        self.db.commit()
        
        return new_suggestion
    
    def get_suggestion(self, suggestion_id: int) -> Optional[ArticulationSuggestion]:
        """Get suggestion by ID."""
        return self.db.query(ArticulationSuggestion).filter(
            ArticulationSuggestion.id == suggestion_id
        ).first()
    
    def list_user_suggestions(self, user_id: str) -> List[ArticulationSuggestion]:
        """List all suggestions for a user."""
        return self.db.query(ArticulationSuggestion).filter(
            ArticulationSuggestion.user_id == user_id
        ).order_by(ArticulationSuggestion.version.desc()).all()


def create_articulation_assistant(db_session: Session) -> ArticulationAssistant:
    """Factory function to create articulation assistant."""
    return ArticulationAssistant(db_session)


