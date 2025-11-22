from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class Match(BaseModel):
    id: str
    title: str
    company: str
    location: str
    match_score: int
    required_capabilities: List[str]
    description: str
    is_remote: bool

class MatchesResponse(BaseModel):
    matches: List[Match]
    total: int
    anonymous_id: str

@router.get("/{anonymous_id}", response_model=MatchesResponse)
async def get_matches(
    anonymous_id: str,
    remote_only: bool = Query(False),
    min_score: int = Query(0, ge=0, le=100)
):
    """
    Get job matches for anonymous user.
    
    Invariants:
    - Anonymous-first: No identity required
    - Capability-based: Matches based on skills, not credentials
    - Human-reviewed: Only show human-approved matches
    """
    # TODO: Query from Postgres with filters
    # TODO: Filter by remote_only, min_score
    # TODO: Only return human-approved matches
    
    # Mock response
    matches = [
        Match(
            id="1",
            title="Senior Full Stack Developer",
            company="TechCorp",
            location="San Francisco, CA",
            match_score=95,
            required_capabilities=["Python", "FastAPI", "React", "PostgreSQL"],
            description="Build scalable web applications with modern tech stack.",
            is_remote=True
        )
    ]
    
    return MatchesResponse(
        matches=matches,
        total=len(matches),
        anonymous_id=anonymous_id
    )

@router.get("/{anonymous_id}/{match_id}")
async def get_match_details(anonymous_id: str, match_id: str):
    """Get detailed information about a specific match"""
    # TODO: Query from database
    # TODO: Verify anonymous_id has access to this match
    
    return {
        "id": match_id,
        "title": "Senior Full Stack Developer",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "match_score": 95,
        "required_capabilities": ["Python", "FastAPI", "React", "PostgreSQL"],
        "description": "Build scalable web applications with modern tech stack.",
        "is_remote": True,
        "full_description": "Detailed job description goes here...",
        "benefits": ["Health insurance", "401k", "Remote work"],
        "salary_range": "$120k - $180k"
    }
