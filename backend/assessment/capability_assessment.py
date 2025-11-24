"""
AI Capability Assessment System.
Tests what users CAN do with AI tools, not credentials.
Human-in-the-Loop: AI evaluates, humans verify edge cases.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from openai import OpenAI
from backend.config import settings
from backend.database.models import CapabilityAssessment, AnonymousUser
from backend.resilience.state_management import StateManager, CheckpointType

logger = logging.getLogger(__name__)


class CapabilityAssessmentEngine:
    """Assesses user AI capabilities through practical challenges."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.state_manager = StateManager(db_session)
    
    def assess_ai_tool_proficiency(
        self,
        user_id: str,
        portfolio_data: Dict[str, Any],
        challenge_responses: Optional[List[Dict[str, Any]]] = None
    ) -> CapabilityAssessment:
        """
        Assess user's proficiency with AI tools based on portfolio and challenges.
        Human-in-the-Loop: AI evaluates, humans verify edge cases.
        """
        # AI evaluation
        ai_results = self._evaluate_with_ai(portfolio_data, challenge_responses)
        
        # Create assessment record
        assessment = CapabilityAssessment(
            user_id=user_id,
            assessment_type="ai_tool_proficiency",
            results=ai_results,
            human_reviewed=False
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        # Create checkpoint for state recovery
        checkpoint = self.state_manager.create_checkpoint(
            checkpoint_type=CheckpointType.ASSESSMENT,
            entity_id=str(assessment.id),
            state_data={
                "assessment_id": assessment.id,
                "user_id": user_id,
                "results": ai_results,
                "created_at": assessment.created_at.isoformat()
            }
        )
        
        assessment.checkpoint_id = checkpoint.id
        self.db.commit()
        
        # Flag for human review if edge case detected
        if self._needs_human_review(ai_results):
            logger.info(f"Assessment {assessment.id} flagged for human review")
        
        return assessment
    
    def _evaluate_with_ai(
        self,
        portfolio_data: Dict[str, Any],
        challenge_responses: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Use AI to evaluate capabilities."""
        if not self.openai_client:
            # Fallback if OpenAI not configured
            return self._fallback_evaluation(portfolio_data)
        
        try:
            # Analyze portfolio projects
            projects = portfolio_data.get("projects", [])
            skills_mentioned = portfolio_data.get("skills", [])
            
            evaluation_prompt = f"""
            Evaluate the AI capabilities demonstrated in this portfolio:
            Projects: {projects}
            Skills mentioned: {skills_mentioned}
            
            Assess:
            1. AI tool proficiency (0-100)
            2. Project complexity (0-100)
            3. Practical experience level (beginner/intermediate/advanced)
            4. Key strengths
            5. Areas for improvement
            
            Return JSON format with scores and analysis.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at evaluating AI capabilities based on practical work."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.3
            )
            
            # Parse AI response (simplified - would need proper JSON parsing)
            ai_analysis = response.choices[0].message.content
            
            return {
                "ai_evaluation": ai_analysis,
                "tool_proficiency_score": self._extract_score(ai_analysis, "proficiency"),
                "project_complexity_score": self._extract_score(ai_analysis, "complexity"),
                "experience_level": self._extract_level(ai_analysis),
                "strengths": self._extract_list(ai_analysis, "strengths"),
                "needs_review": False
            }
        except Exception as e:
            logger.error(f"AI evaluation failed: {e}")
            return self._fallback_evaluation(portfolio_data)
    
    def _fallback_evaluation(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback evaluation when AI is unavailable."""
        projects = portfolio_data.get("projects", [])
        skills = portfolio_data.get("skills", [])
        
        return {
            "tool_proficiency_score": min(len(skills) * 10, 100),
            "project_complexity_score": min(len(projects) * 15, 100),
            "experience_level": "intermediate" if len(projects) > 2 else "beginner",
            "strengths": skills[:3],
            "needs_review": True  # Flag for human review when AI unavailable
        }
    
    def _extract_score(self, text: str, key: str) -> int:
        """Extract score from AI response (simplified)."""
        # In production, would use proper JSON parsing
        return 50  # Default
    
    def _extract_level(self, text: str) -> str:
        """Extract experience level from AI response."""
        text_lower = text.lower()
        if "advanced" in text_lower:
            return "advanced"
        elif "intermediate" in text_lower:
            return "intermediate"
        return "beginner"
    
    def _extract_list(self, text: str, key: str) -> List[str]:
        """Extract list from AI response."""
        return []
    
    def _needs_human_review(self, results: Dict[str, Any]) -> bool:
        """Determine if assessment needs human review."""
        # Flag for review if:
        # - Edge case scores
        # - Unclear evaluation
        # - AI flagged uncertainty
        return results.get("needs_review", False) or \
               results.get("tool_proficiency_score", 50) < 30 or \
               results.get("tool_proficiency_score", 50) > 90
    
    def human_review_assessment(
        self,
        assessment_id: int,
        reviewer_id: str,
        review_decision: str,
        feedback: Optional[str] = None
    ) -> CapabilityAssessment:
        """Human reviewer validates/refines assessment."""
        assessment = self.db.query(CapabilityAssessment).filter(
            CapabilityAssessment.id == assessment_id
        ).first()
        
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")
        
        assessment.human_reviewed = True
        assessment.human_reviewer_id = reviewer_id
        
        # Update results based on human feedback
        if feedback:
            assessment.results["human_feedback"] = feedback
            assessment.results["human_decision"] = review_decision
        
        self.db.commit()
        self.db.refresh(assessment)
        
        # Create new checkpoint after human review
        checkpoint = self.state_manager.create_checkpoint(
            checkpoint_type=CheckpointType.ASSESSMENT,
            entity_id=str(assessment.id),
            state_data={
                "assessment_id": assessment.id,
                "user_id": assessment.user_id,
                "results": assessment.results,
                "human_reviewed": True,
                "reviewer_id": reviewer_id,
                "created_at": datetime.utcnow().isoformat()
            },
            created_by=reviewer_id
        )
        
        assessment.checkpoint_id = checkpoint.id
        self.db.commit()
        
        return assessment
    
    def get_assessment(self, assessment_id: int) -> Optional[CapabilityAssessment]:
        """Get assessment by ID."""
        return self.db.query(CapabilityAssessment).filter(
            CapabilityAssessment.id == assessment_id
        ).first()
    
    def list_user_assessments(self, user_id: str) -> List[CapabilityAssessment]:
        """List all assessments for a user."""
        return self.db.query(CapabilityAssessment).filter(
            CapabilityAssessment.user_id == user_id
        ).order_by(CapabilityAssessment.created_at.desc()).all()


def create_assessment_engine(db_session: Session) -> CapabilityAssessmentEngine:
    """Factory function to create assessment engine."""
    return CapabilityAssessmentEngine(db_session)


