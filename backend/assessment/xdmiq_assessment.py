"""
XDMIQ AI-Native Credentialing System Integration.
Uses preference-based questions: "Which do you prefer?" and "Why?"
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from openai import OpenAI
from config import settings
from database.models import CapabilityAssessment, AnonymousUser
from resilience.state_management import StateManager, CheckpointType

logger = logging.getLogger(__name__)


class XDMIQAssessmentEngine:
    """XDMIQ AI-native credentialing assessment engine."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.state_manager = StateManager(db_session)
    
    def start_xdmiq_assessment(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Start XDMIQ assessment with first preference question.
        Questions format:
        1) Which do you prefer?
        2) Why?
        """
        # Generate first preference question pair
        question_pair = self._generate_preference_question()
        
        return {
            "assessment_id": None,  # Will be created after first answer
            "question_number": 1,
            "question": question_pair["preference_question"],
            "options": question_pair["options"],
            "assessment_type": "xdmiq",
            "status": "in_progress"
        }
    
    def answer_preference_question(
        self,
        user_id: str,
        question_number: int,
        preference: str,
        reasoning: str,
        previous_answers: Optional[List[Dict[str, Any]]] = None,
        is_custom: bool = False
    ) -> Dict[str, Any]:
        """
        Process answer to preference question and generate next question or final score.
        Supports both predefined options and custom/freetext responses.
        """
        answers = previous_answers or []
        answers.append({
            "question_number": question_number,
            "preference": preference,
            "reasoning": reasoning,
            "is_custom": is_custom,  # Track if this was a custom/freetext response
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Determine if assessment is complete (typically 5-10 questions)
        if len(answers) >= 5:
            # Calculate XDMIQ score
            xdmiq_score = self._calculate_xdmiq_score(answers)
            
            # Create assessment record
            assessment = CapabilityAssessment(
                user_id=user_id,
                assessment_type="xdmiq",
                results={
                    "xdmiq_score": xdmiq_score,
                    "answers": answers,
                    "assessment_complete": True,
                    "calculated_at": datetime.utcnow().isoformat()
                },
                human_reviewed=False
            )
            
            self.db.add(assessment)
            self.db.commit()
            self.db.refresh(assessment)
            
            # Create checkpoint
            checkpoint = self.state_manager.create_checkpoint(
                checkpoint_type=CheckpointType.ASSESSMENT,
                entity_id=str(assessment.id),
                state_data={
                    "assessment_id": assessment.id,
                    "user_id": user_id,
                    "xdmiq_score": xdmiq_score,
                    "answers": answers
                }
            )
            
            assessment.checkpoint_id = checkpoint.id
            self.db.commit()
            
            return {
                "assessment_id": assessment.id,
                "xdmiq_score": xdmiq_score,
                "status": "complete",
                "message": "XDMIQ assessment complete"
            }
        else:
            # Generate next question
            next_question = self._generate_preference_question(answers)
            
            return {
                "assessment_id": None,
                "question_number": question_number + 1,
                "question": next_question["preference_question"],
                "options": next_question["options"],
                "status": "in_progress",
                "progress": f"{len(answers)}/5 questions answered"
            }
    
    def _generate_preference_question(
        self,
        previous_answers: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate a preference question pair."""
        # Question templates for AI capability assessment
        question_templates = [
            {
                "preference_question": "Which do you prefer when working with AI tools?",
                "options": [
                    "Building custom solutions from scratch",
                    "Using pre-built frameworks and libraries",
                    "A combination of both"
                ]
            },
            {
                "preference_question": "Which do you prefer when solving problems?",
                "options": [
                    "Systematic, step-by-step approaches",
                    "Creative, experimental approaches",
                    "Adaptive approaches based on context"
                ]
            },
            {
                "preference_question": "Which do you prefer when learning new AI tools?",
                "options": [
                    "Hands-on experimentation",
                    "Reading documentation first",
                    "Following tutorials and examples"
                ]
            },
            {
                "preference_question": "Which do you prefer when working on projects?",
                "options": [
                    "Working independently",
                    "Collaborating with a team",
                    "Both depending on the task"
                ]
            },
            {
                "preference_question": "Which do you prefer when encountering errors?",
                "options": [
                    "Debugging systematically",
                    "Trying different solutions quickly",
                    "Seeking help from community/documentation"
                ]
            }
        ]
        
        # Use AI to generate contextual questions if available
        if self.openai_client and previous_answers:
            try:
                context = self._build_context_from_answers(previous_answers)
                prompt = f"""
                Based on these previous answers: {context}
                
                Generate a new preference question for assessing AI capabilities that:
                1. Is relevant to LLC owners working with AI
                2. Helps understand their work style and capabilities
                3. Is different from previous questions
                
                Return JSON with:
                - preference_question: "Which do you prefer..."
                - options: [array of 2-3 options]
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You generate preference questions for AI capability assessment."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                # Parse response (simplified - would need proper JSON parsing)
                # For now, use template
                pass
            except Exception as e:
                logger.error(f"AI question generation failed: {e}")
        
        # Select question based on progress
        used_indices = []
        if previous_answers:
            # Track which question types have been used
            used_indices = [a.get("question_type", 0) for a in previous_answers]
        
        # Select unused question
        available = [i for i in range(len(question_templates)) if i not in used_indices]
        if available:
            selected = question_templates[available[0]]
        else:
            selected = question_templates[len(previous_answers) % len(question_templates)]
        
        return selected
    
    def _build_context_from_answers(self, answers: List[Dict[str, Any]]) -> str:
        """Build context string from previous answers."""
        context_parts = []
        for answer in answers:
            context_parts.append(
                f"Q{answer['question_number']}: Preferred '{answer['preference']}' "
                f"because '{answer['reasoning']}'"
            )
        return "; ".join(context_parts)
    
    def _calculate_xdmiq_score(
        self,
        answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate XDMIQ score from preference answers.
        XDMIQ score represents AI-native credentialing based on preferences and reasoning.
        """
        if not self.openai_client:
            return self._fallback_score_calculation(answers)
        
        try:
            # Use AI to analyze answers and generate score
            answers_summary = self._build_context_from_answers(answers)
            
            prompt = f"""
            Analyze these preference answers from an LLC owner working with AI:
            {answers_summary}
            
            Calculate an XDMIQ score (0-100) that represents:
            1. AI tool proficiency based on preferences
            2. Problem-solving approach quality
            3. Learning and adaptation capability
            4. Work style compatibility with AI-enabled work
            
            Return JSON with:
            - overall_score: (0-100)
            - proficiency_score: (0-100)
            - reasoning_score: (0-100)
            - adaptability_score: (0-100)
            - strengths: [array of key strengths]
            - areas_for_growth: [array of areas to improve]
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You calculate XDMIQ scores for AI capability assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse AI response (simplified)
            ai_analysis = response.choices[0].message.content
            
            return {
                "overall_score": self._extract_score(ai_analysis, "overall"),
                "proficiency_score": self._extract_score(ai_analysis, "proficiency"),
                "reasoning_score": self._extract_score(ai_analysis, "reasoning"),
                "adaptability_score": self._extract_score(ai_analysis, "adaptability"),
                "strengths": [],
                "areas_for_growth": [],
                "ai_analysis": ai_analysis
            }
        except Exception as e:
            logger.error(f"AI score calculation failed: {e}")
            return self._fallback_score_calculation(answers)
    
    def _extract_score(self, text: str, key: str) -> int:
        """Extract score from AI response."""
        # In production, would use proper JSON parsing
        # For now, return default based on answer count
        return 50 + (len(text) % 50)  # Placeholder
    
    def _fallback_score_calculation(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback score calculation when AI unavailable."""
        # Simple scoring based on answer quality
        reasoning_quality = sum(
            1 for a in answers 
            if len(a.get("reasoning", "")) > 20
        )
        
        base_score = (reasoning_quality / len(answers)) * 100 if answers else 50
        
        return {
            "overall_score": int(base_score),
            "proficiency_score": int(base_score * 0.9),
            "reasoning_score": int(base_score * 1.1),
            "adaptability_score": int(base_score * 0.95),
            "strengths": ["Strong reasoning ability"] if reasoning_quality > 3 else [],
            "areas_for_growth": ["Expand reasoning depth"] if reasoning_quality <= 3 else []
        }
    
    def get_xdmiq_assessment(self, assessment_id: int) -> Optional[CapabilityAssessment]:
        """Get XDMIQ assessment by ID."""
        return self.db.query(CapabilityAssessment).filter(
            CapabilityAssessment.id == assessment_id,
            CapabilityAssessment.assessment_type == "xdmiq"
        ).first()


def create_xdmiq_assessment_engine(db_session: Session) -> XDMIQAssessmentEngine:
    """Factory function to create XDMIQ assessment engine."""
    return XDMIQAssessmentEngine(db_session)


