"""
Assessment API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from database.connection import get_db
from assessment.capability_assessment import create_assessment_engine

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


class PortfolioData(BaseModel):
    """Portfolio data model."""
    projects: List[Dict[str, Any]] = []
    skills: List[str] = []


class AssessmentRequest(BaseModel):
    """Request model for assessment."""
    user_id: str
    portfolio_data: PortfolioData
    challenge_responses: Optional[List[Dict[str, Any]]] = None


class AssessmentResponse(BaseModel):
    """Response model for assessment."""
    assessment_id: int
    user_id: str
    assessment_type: str
    results: Dict[str, Any]
    human_reviewed: bool
    checkpoint_id: Optional[int]
    created_at: str


@router.post("/assess", response_model=AssessmentResponse)
async def assess_capabilities(
    request: AssessmentRequest,
    db: Session = Depends(get_db)
):
    """Assess user AI capabilities."""
    engine = create_assessment_engine(db)
    
    assessment = engine.assess_ai_tool_proficiency(
        user_id=request.user_id,
        portfolio_data=request.portfolio_data.dict(),
        challenge_responses=request.challenge_responses
    )
    
    return AssessmentResponse(
        assessment_id=assessment.id,
        user_id=assessment.user_id,
        assessment_type=assessment.assessment_type,
        results=assessment.results,
        human_reviewed=assessment.human_reviewed,
        checkpoint_id=assessment.checkpoint_id,
        created_at=assessment.created_at.isoformat()
    )


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    """Get assessment by ID."""
    engine = create_assessment_engine(db)
    assessment = engine.get_assessment(assessment_id)
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return AssessmentResponse(
        assessment_id=assessment.id,
        user_id=assessment.user_id,
        assessment_type=assessment.assessment_type,
        results=assessment.results,
        human_reviewed=assessment.human_reviewed,
        checkpoint_id=assessment.checkpoint_id,
        created_at=assessment.created_at.isoformat()
    )


@router.get("/user/{user_id}", response_model=List[AssessmentResponse])
async def list_user_assessments(
    user_id: str,
    db: Session = Depends(get_db)
):
    """List all assessments for a user."""
    engine = create_assessment_engine(db)
    assessments = engine.list_user_assessments(user_id)
    
    return [
        AssessmentResponse(
            assessment_id=a.id,
            user_id=a.user_id,
            assessment_type=a.assessment_type,
            results=a.results,
            human_reviewed=a.human_reviewed,
            checkpoint_id=a.checkpoint_id,
            created_at=a.created_at.isoformat()
        )
        for a in assessments
    ]


@router.post("/{assessment_id}/review")
async def human_review_assessment(
    assessment_id: int,
    reviewer_id: str,
    review_decision: str,
    feedback: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Human reviewer validates/refines assessment."""
    engine = create_assessment_engine(db)
    
    try:
        assessment = engine.human_review_assessment(
            assessment_id=assessment_id,
            reviewer_id=reviewer_id,
            review_decision=review_decision,
            feedback=feedback
        )
        
        return {
            "assessment_id": assessment.id,
            "human_reviewed": assessment.human_reviewed,
            "reviewer_id": assessment.human_reviewer_id,
            "message": "Assessment reviewed successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


