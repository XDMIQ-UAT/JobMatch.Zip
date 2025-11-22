from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class AssessmentSubmission(BaseModel):
    anonymous_id: str
    skills: List[str]
    portfolio_url: Optional[str] = None
    work_preference: str
    work_preference_reason: Optional[str] = None

class AssessmentResponse(BaseModel):
    success: bool
    anonymous_id: str
    message: str

@router.post("/submit", response_model=AssessmentResponse)
async def submit_assessment(assessment: AssessmentSubmission):
    """
    Submit capability assessment.
    
    Invariants:
    - Anonymous-first: No personal identifiable information required
    - Checkpoint: State saved before processing
    - Human-in-the-loop: Results queued for human review
    """
    # TODO: Checkpoint current state
    # TODO: Validate anonymous_id format
    # TODO: Save to Postgres
    # TODO: Queue for human review
    # TODO: Trigger AI analysis with Ollama
    
    return AssessmentResponse(
        success=True,
        anonymous_id=assessment.anonymous_id,
        message="Assessment submitted successfully. Results will be available after human review."
    )

@router.get("/status/{anonymous_id}")
async def get_assessment_status(anonymous_id: str):
    """Get assessment status for anonymous ID"""
    # TODO: Query from database
    return {
        "anonymous_id": anonymous_id,
        "status": "pending_review",
        "submitted_at": "2025-01-01T00:00:00Z"
    }
