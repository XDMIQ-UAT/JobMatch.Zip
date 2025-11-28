"""
Zero-Knowledge Matching API
Matches users based ONLY on public capabilities, never on personal information
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from collections import Counter

# Import from auth module
from .zero_knowledge_auth import CAPABILITIES_DB, verify_session_token

router = APIRouter(prefix="/api/zk-match", tags=["zero-knowledge-matching"])


# Request/Response Models
class MatchRequest(BaseModel):
    seeking_skills: List[str]
    experience_level: Optional[str] = None  # 'junior', 'mid', 'senior', etc.
    availability_type: Optional[str] = None  # 'full-time', 'part-time', etc.
    industries: Optional[List[str]] = None
    remote_ok: Optional[bool] = None
    max_results: int = 10


class MatchResult(BaseModel):
    user_id: str
    match_score: float
    matched_skills: List[str]
    capabilities: Dict[str, Any]
    # NO name, NO email, NO personal info


# Matching Engine
class CapabilityMatcher:
    """Match users based solely on capabilities, with zero knowledge of personal data"""
    
    @staticmethod
    def calculate_match_score(
        seeker: MatchRequest,
        candidate: Dict[str, Any]
    ) -> float:
        """
        Calculate match score (0.0 to 1.0) based on capabilities only
        NO personal information is used in scoring
        """
        score = 0.0
        max_score = 0.0
        
        # Skill matching (50% weight)
        skill_weight = 0.5
        max_score += skill_weight
        
        candidate_skills = set(candidate.get('skills', []))
        seeker_skills = set(seeker.seeking_skills)
        
        if seeker_skills:
            skill_overlap = len(seeker_skills & candidate_skills)
            skill_score = skill_overlap / len(seeker_skills)
            score += skill_score * skill_weight
        
        # Experience level matching (20% weight)
        exp_weight = 0.2
        max_score += exp_weight
        
        if seeker.experience_level:
            exp_levels = ['junior', 'mid', 'senior', 'staff', 'principal']
            try:
                seeker_idx = exp_levels.index(seeker.experience_level)
                candidate_level = candidate.get('rate_range', 'mid')
                candidate_idx = exp_levels.index(candidate_level)
                
                # Perfect match = 1.0, adjacent = 0.5, far = 0.0
                exp_diff = abs(seeker_idx - candidate_idx)
                if exp_diff == 0:
                    score += exp_weight
                elif exp_diff == 1:
                    score += exp_weight * 0.5
            except ValueError:
                pass  # Invalid level, skip
        
        # Availability matching (15% weight)
        avail_weight = 0.15
        max_score += avail_weight
        
        if seeker.availability_type:
            candidate_avail = candidate.get('availability', '')
            if seeker.availability_type == candidate_avail:
                score += avail_weight
        
        # Industry matching (10% weight)
        industry_weight = 0.1
        max_score += industry_weight
        
        if seeker.industries:
            candidate_industries = set(candidate.get('industries', []))
            seeker_industries = set(seeker.industries)
            if seeker_industries:
                industry_overlap = len(seeker_industries & candidate_industries)
                industry_score = industry_overlap / len(seeker_industries)
                score += industry_score * industry_weight
        
        # Currently available (5% weight)
        avail_now_weight = 0.05
        max_score += avail_now_weight
        
        if candidate.get('currently_available', False):
            score += avail_now_weight
        
        # Normalize score to 0-1 range
        return score / max_score if max_score > 0 else 0.0
    
    @staticmethod
    def find_matches(
        seeker: MatchRequest,
        max_results: int = 10
    ) -> List[MatchResult]:
        """
        Find matching candidates based on capabilities only
        Returns anonymous user IDs with match scores
        NO personal information in results
        """
        matches = []
        
        for user_id, capabilities in CAPABILITIES_DB.items():
            # Skip if no skills
            if not capabilities.get('skills'):
                continue
            
            # Calculate match score
            score = CapabilityMatcher.calculate_match_score(seeker, capabilities)
            
            # Only include if reasonable match (>20% score)
            if score >= 0.2:
                # Extract matched skills
                candidate_skills = set(capabilities.get('skills', []))
                seeker_skills = set(seeker.seeking_skills)
                matched_skills = list(seeker_skills & candidate_skills)
                
                # Remove email from capabilities before returning
                safe_capabilities = {
                    k: v for k, v in capabilities.items() 
                    if k != 'email'  # Strip email
                }
                
                matches.append(MatchResult(
                    user_id=user_id,
                    match_score=round(score, 3),
                    matched_skills=matched_skills,
                    capabilities=safe_capabilities
                ))
        
        # Sort by score (descending) and limit results
        matches.sort(key=lambda m: m.match_score, reverse=True)
        return matches[:max_results]


# Endpoints
@router.post("/find", response_model=List[MatchResult])
async def find_matches(request: MatchRequest):
    """
    Find matching candidates based on capabilities only
    
    This endpoint:
    - Works ONLY with public capability data
    - NEVER accesses encrypted profiles
    - Returns anonymous user IDs only
    - NO personal information in results
    """
    
    if not request.seeking_skills:
        raise HTTPException(
            status_code=400,
            detail="At least one skill must be specified"
        )
    
    matches = CapabilityMatcher.find_matches(request, request.max_results)
    
    return matches


@router.get("/my-matches")
async def get_my_matches(
    max_results: int = 10,
    session: Dict = Depends(verify_session_token)
):
    """
    Get matches for the logged-in user based on their capabilities
    Returns users looking for what you offer
    """
    
    user_id = session['user_id']
    
    # Get user's capabilities
    my_capabilities = CAPABILITIES_DB.get(user_id)
    if not my_capabilities:
        return []
    
    # Create a seeker request based on user's skills
    # (Show them people looking for what they have)
    seeker_request = MatchRequest(
        seeking_skills=my_capabilities.get('skills', []),
        experience_level=my_capabilities.get('rate_range'),
        availability_type=my_capabilities.get('availability'),
        max_results=max_results
    )
    
    # Find matches
    matches = CapabilityMatcher.find_matches(seeker_request, max_results)
    
    # Filter out self
    matches = [m for m in matches if m.user_id != user_id]
    
    return matches


@router.get("/stats")
async def matching_stats():
    """Get aggregate matching statistics (no personal data)"""
    
    if not CAPABILITIES_DB:
        return {
            "total_users": 0,
            "top_skills": [],
            "experience_distribution": {},
            "availability_distribution": {}
        }
    
    # Aggregate skill counts
    all_skills = []
    for cap in CAPABILITIES_DB.values():
        all_skills.extend(cap.get('skills', []))
    
    skill_counts = Counter(all_skills)
    top_skills = [
        {"skill": skill, "count": count}
        for skill, count in skill_counts.most_common(10)
    ]
    
    # Experience distribution
    exp_distribution = Counter(
        cap.get('rate_range', 'unknown')
        for cap in CAPABILITIES_DB.values()
    )
    
    # Availability distribution
    avail_distribution = Counter(
        cap.get('availability', 'unknown')
        for cap in CAPABILITIES_DB.values()
    )
    
    return {
        "total_users": len(CAPABILITIES_DB),
        "top_skills": top_skills,
        "experience_distribution": dict(exp_distribution),
        "availability_distribution": dict(avail_distribution),
        "note": "All data is aggregated and anonymous"
    }


@router.get("/debug/test-match")
async def debug_test_match():
    """Debug endpoint to test matching with sample query"""
    
    sample_request = MatchRequest(
        seeking_skills=['Python', 'FastAPI', 'React'],
        experience_level='senior',
        availability_type='contract',
        max_results=5
    )
    
    matches = CapabilityMatcher.find_matches(sample_request)
    
    return {
        "query": sample_request.dict(),
        "matches_found": len(matches),
        "matches": matches
    }
