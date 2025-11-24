"""
Longevity Prediction Engine.
Predicts engagement duration for job matches based on multiple factors.
"""
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LongevityPredictor:
    """Predicts long-term match success and engagement duration."""
    
    def __init__(self):
        """Initialize longevity predictor."""
        pass
    
    def predict_longevity(
        self,
        user_profile: Dict[str, Any],
        job_posting: Dict[str, Any],
        compatibility_score: int
    ) -> Dict[str, Any]:
        """
        Predict longevity of a match.
        
        Returns:
            {
                "longevity_score": int (0-100, represents predicted months),
                "factors": List[str] (contributing factors),
                "confidence": float (0-1)
            }
        """
        factors = []
        score = 0
        
        # 1. Capability Alignment (30 points)
        # Deep skill fit indicates long-term value
        capability_score = self._score_capability_alignment(
            user_profile, job_posting
        )
        score += capability_score
        if capability_score >= 20:
            factors.append("Strong capability alignment")
        
        # 2. Growth Potential (25 points)
        # Room for skill development keeps engagement high
        growth_score = self._score_growth_potential(
            user_profile, job_posting
        )
        score += growth_score
        if growth_score >= 15:
            factors.append("High growth potential")
        
        # 3. Cultural Compatibility (20 points)
        # Work style and communication fit
        cultural_score = self._score_cultural_fit(
            user_profile, job_posting
        )
        score += cultural_score
        if cultural_score >= 12:
            factors.append("Cultural compatibility")
        
        # 4. Stability Indicators (15 points)
        # Past patterns and preferences
        stability_score = self._score_stability(user_profile)
        score += stability_score
        if stability_score >= 10:
            factors.append("Stability indicators positive")
        
        # 5. Mutual Investment (10 points)
        # Both parties benefit long-term
        investment_score = self._score_mutual_investment(
            user_profile, job_posting, compatibility_score
        )
        score += investment_score
        if investment_score >= 6:
            factors.append("Strong mutual benefit")
        
        # Calculate confidence based on data availability
        confidence = self._calculate_confidence(user_profile, job_posting)
        
        return {
            "longevity_score": min(int(score), 100),
            "factors": factors,
            "confidence": confidence,
            "predicted_months": self._score_to_months(score)
        }
    
    def _score_capability_alignment(
        self,
        user_profile: Dict[str, Any],
        job_posting: Dict[str, Any]
    ) -> float:
        """
        Score capability alignment (0-30).
        Deep skill fit vs surface match.
        """
        user_skills = set(user_profile.get("skills", []))
        required_skills = set(job_posting.get("required_skills", []))
        preferred_skills = set(job_posting.get("preferred_skills", []))
        
        if not required_skills:
            return 15.0  # Neutral if no requirements
        
        # Core skills match
        required_match = len(user_skills & required_skills)
        required_ratio = required_match / len(required_skills)
        
        # Advanced skills bonus
        preferred_match = len(user_skills & preferred_skills) if preferred_skills else 0
        preferred_ratio = preferred_match / len(preferred_skills) if preferred_skills else 0
        
        # Deep alignment: covers requirements + extras
        base_score = required_ratio * 20
        bonus_score = preferred_ratio * 10
        
        return min(base_score + bonus_score, 30.0)
    
    def _score_growth_potential(
        self,
        user_profile: Dict[str, Any],
        job_posting: Dict[str, Any]
    ) -> float:
        """
        Score growth potential (0-25).
        Room for skill development and learning.
        """
        user_skills = set(user_profile.get("skills", []))
        required_skills = set(job_posting.get("required_skills", []))
        preferred_skills = set(job_posting.get("preferred_skills", []))
        
        # Learning goals alignment
        learning_goals = set(user_profile.get("learning_goals", []))
        all_job_skills = required_skills | preferred_skills
        
        # Skills user can learn on the job
        learnable_skills = all_job_skills - user_skills
        learning_overlap = learnable_skills & learning_goals
        
        score = 0
        
        # Has room to grow (not overqualified or underqualified)
        skill_coverage = len(user_skills & required_skills) / len(required_skills) if required_skills else 0
        if 0.6 <= skill_coverage <= 0.9:
            score += 12  # Sweet spot: knows enough, room to learn
        elif 0.4 <= skill_coverage < 0.6:
            score += 8  # Can learn, but steep curve
        elif skill_coverage >= 0.9:
            score += 5  # May be overqualified
        
        # Learning goals align with job
        if learning_overlap:
            learning_ratio = len(learning_overlap) / len(learnable_skills) if learnable_skills else 0
            score += learning_ratio * 13
        
        return min(score, 25.0)
    
    def _score_cultural_fit(
        self,
        user_profile: Dict[str, Any],
        job_posting: Dict[str, Any]
    ) -> float:
        """
        Score cultural compatibility (0-20).
        Work style and communication preferences.
        """
        score = 10.0  # Base neutral score
        
        # Work style preferences
        user_work_style = user_profile.get("work_style", {})
        job_work_style = job_posting.get("work_style", {})
        
        if user_work_style and job_work_style:
            # Remote/hybrid/office preference
            if user_work_style.get("remote") == job_work_style.get("remote"):
                score += 5
            
            # Collaboration style
            if user_work_style.get("collaboration") == job_work_style.get("collaboration"):
                score += 3
            
            # Communication frequency
            if user_work_style.get("communication") == job_work_style.get("communication"):
                score += 2
        
        return min(score, 20.0)
    
    def _score_stability(self, user_profile: Dict[str, Any]) -> float:
        """
        Score stability indicators (0-15).
        Past patterns and commitment indicators.
        """
        score = 8.0  # Base neutral score
        
        # Past engagement patterns (if available and user consented)
        past_engagements = user_profile.get("past_engagements", [])
        if past_engagements:
            # Average duration of past engagements
            durations = [e.get("duration_months", 0) for e in past_engagements]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            if avg_duration >= 12:
                score += 7  # Stable history
            elif avg_duration >= 6:
                score += 4  # Moderate stability
        
        # Career stage indicator
        career_stage = user_profile.get("career_stage")
        if career_stage in ["mid-career", "senior"]:
            score += 3  # More stability expected
        
        return min(score, 15.0)
    
    def _score_mutual_investment(
        self,
        user_profile: Dict[str, Any],
        job_posting: Dict[str, Any],
        compatibility_score: int
    ) -> float:
        """
        Score mutual investment potential (0-10).
        Both parties benefit long-term.
        """
        score = 5.0  # Base neutral score
        
        # High compatibility suggests mutual benefit
        if compatibility_score >= 80:
            score += 3
        elif compatibility_score >= 60:
            score += 1.5
        
        # Compensation alignment (if available)
        user_expectations = user_profile.get("compensation_expectations", {})
        job_offer = job_posting.get("compensation", {})
        
        if user_expectations and job_offer:
            user_min = user_expectations.get("min", 0)
            job_max = job_offer.get("max", float('inf'))
            
            if user_min <= job_max:
                score += 2  # Compensation aligned
        
        return min(score, 10.0)
    
    def _calculate_confidence(
        self,
        user_profile: Dict[str, Any],
        job_posting: Dict[str, Any]
    ) -> float:
        """Calculate confidence in prediction (0-1)."""
        data_points = 0
        total_possible = 10
        
        # Check data availability
        if user_profile.get("skills"):
            data_points += 2
        if user_profile.get("learning_goals"):
            data_points += 1
        if user_profile.get("work_style"):
            data_points += 2
        if user_profile.get("past_engagements"):
            data_points += 2
        if job_posting.get("required_skills"):
            data_points += 2
        if job_posting.get("work_style"):
            data_points += 1
        
        return min(data_points / total_possible, 1.0)
    
    def _score_to_months(self, score: float) -> int:
        """
        Convert longevity score to predicted months.
        0-100 score maps to 1-36 months.
        """
        if score >= 90:
            return 36  # 3+ years
        elif score >= 75:
            return 24  # 2 years
        elif score >= 60:
            return 18  # 1.5 years
        elif score >= 45:
            return 12  # 1 year
        elif score >= 30:
            return 6   # 6 months
        else:
            return 3   # 3 months minimum


def create_longevity_predictor() -> LongevityPredictor:
    """Factory function to create longevity predictor."""
    return LongevityPredictor()
