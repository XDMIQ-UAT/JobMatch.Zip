"""
Matching API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database.connection import get_db
from ai.matching_engine import create_matching_engine

router = APIRouter(prefix="/api/matching", tags=["matching"])


class MatchResponse(BaseModel):
    """Response model for match."""
    match_id: int
    user_id: str
    job_posting_id: int
    match_score: int
    compatibility_score: Optional[int] = None
    longevity_score: Optional[int] = None
    predicted_months: Optional[int] = None
    longevity_factors: Optional[List[str]] = None
    match_reasons: Optional[List[str]]
    human_reviewed: bool
    checkpoint_id: Optional[int]
    created_at: str


class ReviewRequest(BaseModel):
    """Request model for human review."""
    reviewer_id: str
    decision: str  # approved, rejected, needs_revision
    feedback: Optional[str] = None


@router.post("/generate/{user_id}", response_model=List[MatchResponse])
async def generate_matches(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Generate matches for a user."""
    engine = create_matching_engine(db)
    
    try:
        matches = engine.generate_matches(user_id, limit=limit)
        
        return [
            MatchResponse(
                match_id=m.id,
                user_id=m.user_id,
                job_posting_id=m.job_posting_id,
                match_score=m.match_score,
                compatibility_score=m.compatibility_score,
                longevity_score=m.longevity_score,
                predicted_months=m.predicted_months,
                longevity_factors=m.longevity_factors,
                match_reasons=m.match_reasons,
                human_reviewed=m.human_reviewed,
                checkpoint_id=m.checkpoint_id,
                created_at=m.created_at.isoformat()
            )
            for m in matches
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    """Get match by ID."""
    engine = create_matching_engine(db)
    match = engine.get_match(match_id)
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    return MatchResponse(
        match_id=match.id,
        user_id=match.user_id,
        job_posting_id=match.job_posting_id,
        match_score=match.match_score,
        compatibility_score=match.compatibility_score,
        longevity_score=match.longevity_score,
        predicted_months=match.predicted_months,
        longevity_factors=match.longevity_factors,
        match_reasons=match.match_reasons,
        human_reviewed=match.human_reviewed,
        checkpoint_id=match.checkpoint_id,
        created_at=match.created_at.isoformat()
    )


@router.get("/user/{user_id}", response_model=List[MatchResponse])
async def list_user_matches(
    user_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List matches for a user."""
    engine = create_matching_engine(db)
    matches = engine.list_user_matches(user_id, limit=limit)
    
    return [
        MatchResponse(
            match_id=m.id,
            user_id=m.user_id,
            job_posting_id=m.job_posting_id,
            match_score=m.match_score,
            compatibility_score=m.compatibility_score,
            longevity_score=m.longevity_score,
            predicted_months=m.predicted_months,
            longevity_factors=m.longevity_factors,
            match_reasons=m.match_reasons,
            human_reviewed=m.human_reviewed,
            checkpoint_id=m.checkpoint_id,
            created_at=m.created_at.isoformat()
        )
        for m in matches
    ]


@router.post("/{match_id}/review")
async def review_match(
    match_id: int,
    request: ReviewRequest,
    db: Session = Depends(get_db)
):
    """Human reviewer validates/refines match."""
    engine = create_matching_engine(db)
    
    try:
        match = engine.human_review_match(
            match_id=match_id,
            reviewer_id=request.reviewer_id,
            decision=request.decision,
            feedback=request.feedback
        )
        
        return {
            "match_id": match.id,
            "human_reviewed": match.human_reviewed,
            "reviewer_id": match.human_reviewer_id,
            "decision": request.decision,
            "message": "Match reviewed successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


