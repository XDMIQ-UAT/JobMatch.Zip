"""
AI-Powered Matching Engine.
Human-in-the-Loop Architecture: AI generates initial matches, human reviewers validate.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from openai import OpenAI
from backend.config import settings
from backend.database.models import Match, JobPosting, AnonymousUser, CapabilityAssessment
from backend.resilience.state_management import StateManager, CheckpointType
from backend.infrastructure.scaling import scaling_manager
from backend.ai.longevity_predictor import create_longevity_predictor

logger = logging.getLogger(__name__)


class MatchingEngine:
    """AI-powered matching engine with human review."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.state_manager = StateManager(db_session)
        self.es_client = scaling_manager.get_elasticsearch_client()
        self.longevity_predictor = create_longevity_predictor()
    
    def generate_matches(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Match]:
        """
        Generate matches for a user.
        Human-in-the-Loop: AI generates, humans validate.
        """
        # Get user's latest assessment (prefer XDMIQ if available)
        xdmiq_assessment = self.db.query(CapabilityAssessment).filter(
            CapabilityAssessment.user_id == user_id,
            CapabilityAssessment.assessment_type == "xdmiq"
        ).order_by(CapabilityAssessment.created_at.desc()).first()
        
        # Fallback to regular assessment if no XDMIQ
        assessment = xdmiq_assessment or self.db.query(CapabilityAssessment).filter(
            CapabilityAssessment.user_id == user_id
        ).order_by(CapabilityAssessment.created_at.desc()).first()
        
        if not assessment:
            raise ValueError("User has no capability assessment")
        
        # Get user's profile
        user = self.db.query(AnonymousUser).filter(
            AnonymousUser.id == user_id
        ).first()
        
        if not user:
            raise ValueError("User not found")
        
        # AI generates initial matches
        ai_matches = self._generate_ai_matches(user_id, assessment, limit)
        
        # Create match records with longevity predictions
        matches = []
        for match_data in ai_matches:
            match = Match(
                user_id=user_id,
                job_posting_id=match_data["job_posting_id"],
                match_score=match_data["final_score"],
                compatibility_score=match_data["compatibility_score"],
                longevity_score=match_data["longevity_score"],
                predicted_months=match_data["predicted_months"],
                longevity_factors=match_data["longevity_factors"],
                match_reasons=match_data["reasons"],
                human_reviewed=False
            )
            self.db.add(match)
            matches.append(match)
        
        self.db.commit()
        
        # Create checkpoints for each match
        for match in matches:
            checkpoint = self.state_manager.create_checkpoint(
                checkpoint_type=CheckpointType.MATCHING,
                entity_id=str(match.id),
                state_data={
                    "match_id": match.id,
                    "user_id": match.user_id,
                    "job_posting_id": match.job_posting_id,
                    "match_score": match.match_score,
                    "match_reasons": match.match_reasons,
                    "created_at": match.created_at.isoformat()
                }
            )
            match.checkpoint_id = checkpoint.id
        
        self.db.commit()
        
        # Refresh matches
        for match in matches:
            self.db.refresh(match)
        
        # Flag for human review if needed
        high_value_matches = [m for m in matches if m.match_score >= 80]
        if high_value_matches:
            logger.info(f"Flagged {len(high_value_matches)} high-value matches for human review")
        
        return matches
    
    def _generate_ai_matches(
        self,
        user_id: str,
        assessment: CapabilityAssessment,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Use AI to generate matches."""
        # Get active job postings
        job_postings = self.db.query(JobPosting).filter(
            JobPosting.active == True
        ).limit(limit * 3).all()  # Get more candidates for AI to evaluate
        
        if not job_postings:
            return []
        
        # Extract user capabilities from assessment
        # Check if XDMIQ assessment
        if assessment.assessment_type == "xdmiq":
            xdmiq_score = assessment.results.get("xdmiq_score", {})
            user_skills = xdmiq_score.get("strengths", [])
            proficiency_score = xdmiq_score.get("overall_score", 50)
        else:
            user_skills = assessment.results.get("strengths", [])
            proficiency_score = assessment.results.get("tool_proficiency_score", 50)
        
        matches = []
        
        # Build user profile for longevity prediction
        user = self.db.query(AnonymousUser).filter(
            AnonymousUser.id == user_id
        ).first()
        
        user_profile = {
            "skills": user_skills,
            "learning_goals": assessment.results.get("learning_goals", []),
            "work_style": assessment.results.get("work_style", {}),
            "career_stage": assessment.results.get("career_stage"),
            "past_engagements": assessment.results.get("past_engagements", []),
            "compensation_expectations": assessment.results.get("compensation_expectations", {})
        }
        
        for job in job_postings:
            # Calculate compatibility score (immediate skill fit)
            compatibility_score = self._calculate_match_score(
                user_skills=user_skills,
                user_proficiency=proficiency_score,
                job_requirements=job.required_skills,
                job_preferred=job.preferred_skills or []
            )
            
            if compatibility_score >= 50:  # Minimum threshold
                # Build job profile for longevity prediction
                job_profile = {
                    "required_skills": job.required_skills,
                    "preferred_skills": job.preferred_skills or [],
                    "work_style": {},  # TODO: Extract from job description
                    "compensation": {}  # TODO: Extract from job posting
                }
                
                # Predict longevity
                longevity_prediction = self.longevity_predictor.predict_longevity(
                    user_profile=user_profile,
                    job_posting=job_profile,
                    compatibility_score=compatibility_score
                )
                
                # Calculate final score: compatibility (40%) + longevity (60%)
                # This prioritizes longest-lasting matches
                final_score = int(
                    (compatibility_score * 0.4) + (longevity_prediction["longevity_score"] * 0.6)
                )
                
                matches.append({
                    "job_posting_id": job.id,
                    "final_score": final_score,
                    "compatibility_score": compatibility_score,
                    "longevity_score": longevity_prediction["longevity_score"],
                    "predicted_months": longevity_prediction["predicted_months"],
                    "longevity_factors": longevity_prediction["factors"],
                    "reasons": self._generate_match_reasons(
                        user_skills, job.required_skills, compatibility_score
                    ) + longevity_prediction["factors"]
                })
        
        # Sort by final score (longevity-weighted) and limit
        matches.sort(key=lambda x: x["final_score"], reverse=True)
        return matches[:limit]
    
    def _calculate_match_score(
        self,
        user_skills: List[str],
        user_proficiency: int,
        job_requirements: List[str],
        job_preferred: List[str]
    ) -> int:
        """Calculate match score between user and job."""
        # Base score from proficiency
        score = user_proficiency * 0.4
        
        # Required skills match
        required_match = len(set(user_skills) & set(job_requirements))
        if job_requirements:
            required_score = (required_match / len(job_requirements)) * 40
            score += required_score
        else:
            score += 20
        
        # Preferred skills bonus
        preferred_match = len(set(user_skills) & set(job_preferred))
        if job_preferred:
            preferred_score = (preferred_match / len(job_preferred)) * 20
            score += preferred_score
        
        return min(int(score), 100)
    
    def _generate_match_reasons(
        self,
        user_skills: List[str],
        job_requirements: List[str],
        score: int
    ) -> List[str]:
        """Generate reasons for the match."""
        reasons = []
        
        matching_skills = set(user_skills) & set(job_requirements)
        if matching_skills:
            reasons.append(f"Strong match on: {', '.join(list(matching_skills)[:3])}")
        
        if score >= 80:
            reasons.append("High compatibility score")
        elif score >= 60:
            reasons.append("Good skill alignment")
        
        return reasons
    
    def human_review_match(
        self,
        match_id: int,
        reviewer_id: str,
        decision: str,
        feedback: Optional[str] = None
    ) -> Match:
        """Human reviewer validates/refines match."""
        match = self.db.query(Match).filter(Match.id == match_id).first()
        
        if not match:
            raise ValueError(f"Match {match_id} not found")
        
        match.human_reviewed = True
        match.human_reviewer_id = reviewer_id
        match.human_feedback = feedback
        
        # Adjust score based on human feedback
        if decision == "approved":
            # Human confirms it's a good match
            pass
        elif decision == "rejected":
            match.match_score = max(match.match_score - 20, 0)
        elif decision == "needs_revision":
            # Keep score but flag for refinement
            match.match_reasons = (match.match_reasons or []) + ["Needs refinement"]
        
        self.db.commit()
        
        # Create checkpoint after human review
        checkpoint = self.state_manager.create_checkpoint(
            checkpoint_type=CheckpointType.MATCHING,
            entity_id=str(match.id),
            state_data={
                "match_id": match.id,
                "user_id": match.user_id,
                "job_posting_id": match.job_posting_id,
                "match_score": match.match_score,
                "human_reviewed": True,
                "reviewer_id": reviewer_id,
                "decision": decision,
                "created_at": datetime.utcnow().isoformat()
            },
            created_by=reviewer_id
        )
        
        match.checkpoint_id = checkpoint.id
        self.db.commit()
        self.db.refresh(match)
        
        return match
    
    def get_match(self, match_id: int) -> Optional[Match]:
        """Get match by ID."""
        return self.db.query(Match).filter(Match.id == match_id).first()
    
    def list_user_matches(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Match]:
        """List matches for a user."""
        return self.db.query(Match).filter(
            Match.user_id == user_id
        ).order_by(Match.match_score.desc()).limit(limit).all()


def create_matching_engine(db_session: Session) -> MatchingEngine:
    """Factory function to create matching engine."""
    return MatchingEngine(db_session)

