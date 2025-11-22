from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class Profile(BaseModel):
    anonymous_id: str
    skills: List[str]
    portfolio_url: Optional[str] = None
    work_preference: str
    bio: Optional[str] = None
    created_at: str
    updated_at: str

class ProfileUpdate(BaseModel):
    skills: Optional[List[str]] = None
    portfolio_url: Optional[str] = None
    work_preference: Optional[str] = None
    bio: Optional[str] = None

@router.get("/{anonymous_id}", response_model=Profile)
async def get_profile(anonymous_id: str):
    """
    Get anonymous profile.
    
    Invariants:
    - Anonymous-first: Only anonymous_id required
    - No PII: Profile contains only capabilities, no identity info
    """
    # TODO: Query from Postgres
    # TODO: Validate anonymous_id exists
    
    return Profile(
        anonymous_id=anonymous_id,
        skills=["Python", "FastAPI", "React"],
        portfolio_url="https://github.com/example",
        work_preference="Break it into smaller sub-problems",
        bio=None,
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-01T00:00:00Z"
    )

@router.put("/{anonymous_id}", response_model=Profile)
async def update_profile(anonymous_id: str, update: ProfileUpdate):
    """
    Update anonymous profile.
    
    Invariants:
    - Checkpoint: State saved before update
    - No PII: Cannot add identity information
    """
    # TODO: Checkpoint current state
    # TODO: Validate anonymous_id exists
    # TODO: Update in Postgres
    # TODO: Return updated profile
    
    return Profile(
        anonymous_id=anonymous_id,
        skills=update.skills or ["Python", "FastAPI", "React"],
        portfolio_url=update.portfolio_url,
        work_preference=update.work_preference or "Break it into smaller sub-problems",
        bio=update.bio,
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-01T12:00:00Z"
    )

@router.post("/create", response_model=Profile)
async def create_profile(anonymous_id: str):
    """Create new anonymous profile"""
    # TODO: Generate unique anonymous_id if not provided
    # TODO: Save to Postgres
    # TODO: Initialize in Redis
    
    return Profile(
        anonymous_id=anonymous_id,
        skills=[],
        portfolio_url=None,
        work_preference="",
        bio=None,
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-01T00:00:00Z"
    )
