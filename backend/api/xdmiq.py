"""
XDMIQ Assessment API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from backend.database.connection import get_db
from backend.assessment.xdmiq_assessment import create_xdmiq_assessment_engine

router = APIRouter(prefix="/api/xdmiq", tags=["xdmiq"])


class XDMIQStartRequest(BaseModel):
    """Request to start XDMIQ assessment."""
    user_id: str


class XDMIQAnswerRequest(BaseModel):
    """Request to answer XDMIQ preference question."""
    user_id: str
    question_number: int
    preference: str
    reasoning: str
    previous_answers: Optional[List[Dict[str, Any]]] = None
    is_custom: Optional[bool] = False  # Indicates if preference is a custom/freetext response


class XDMIQQuestionResponse(BaseModel):
    """Response with XDMIQ question."""
    assessment_id: Optional[int]
    question_number: int
    question: str
    options: List[str]
    status: str
    progress: Optional[str] = None


class XDMIQScoreResponse(BaseModel):
    """Response with XDMIQ score."""
    assessment_id: int
    xdmiq_score: Dict[str, Any]
    status: str
    message: str


@router.post("/start", response_model=XDMIQQuestionResponse)
async def start_xdmiq_assessment(
    request: XDMIQStartRequest,
    db: Session = Depends(get_db)
):
    """Start XDMIQ assessment with first preference question."""
    engine = create_xdmiq_assessment_engine(db)
    
    assessment = engine.start_xdmiq_assessment(request.user_id)
    
    return XDMIQQuestionResponse(
        assessment_id=assessment.get("assessment_id"),
        question_number=assessment["question_number"],
        question=assessment["question"],
        options=assessment["options"],
        status=assessment["status"]
    )


@router.post("/answer", response_model=Dict[str, Any])
async def answer_xdmiq_question(
    request: XDMIQAnswerRequest,
    db: Session = Depends(get_db)
):
    """Answer XDMIQ preference question."""
    engine = create_xdmiq_assessment_engine(db)
    
    result = engine.answer_preference_question(
        user_id=request.user_id,
        question_number=request.question_number,
        preference=request.preference,
        reasoning=request.reasoning,
        previous_answers=request.previous_answers,
        is_custom=request.is_custom or False
    )
    
    if result.get("status") == "complete":
        return XDMIQScoreResponse(
            assessment_id=result["assessment_id"],
            xdmiq_score=result["xdmiq_score"],
            status=result["status"],
            message=result["message"]
        ).dict()
    else:
        return XDMIQQuestionResponse(
            assessment_id=result.get("assessment_id"),
            question_number=result["question_number"],
            question=result["question"],
            options=result["options"],
            status=result["status"],
            progress=result.get("progress")
        ).dict()


@router.get("/assessment/{assessment_id}")
async def get_xdmiq_assessment(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    """Get XDMIQ assessment by ID."""
    engine = create_xdmiq_assessment_engine(db)
    assessment = engine.get_xdmiq_assessment(assessment_id)
    
    if not assessment:
        raise HTTPException(status_code=404, detail="XDMIQ assessment not found")
    
    return {
        "assessment_id": assessment.id,
        "user_id": assessment.user_id,
        "xdmiq_score": assessment.results.get("xdmiq_score"),
        "answers": assessment.results.get("answers"),
        "created_at": assessment.created_at.isoformat()
    }


