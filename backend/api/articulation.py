"""
Articulation API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from backend.database.connection import get_db
from backend.ai.articulation_assistant import create_articulation_assistant

router = APIRouter(prefix="/api/articulation", tags=["articulation"])


class ArticulationRequest(BaseModel):
    """Request model for articulation."""
    user_id: str
    original_text: str
    context: Optional[Dict[str, Any]] = None


class ArticulationResponse(BaseModel):
    """Response model for articulation."""
    suggestion_id: int
    user_id: str
    original_text: str
    suggested_text: str
    version: int
    human_refined: bool
    checkpoint_id: Optional[int]
    created_at: str


class RefineRequest(BaseModel):
    """Request model for refinement."""
    refined_text: str


@router.post("/suggest", response_model=ArticulationResponse)
async def suggest_articulation(
    request: ArticulationRequest,
    db: Session = Depends(get_db)
):
    """Generate articulation suggestion."""
    assistant = create_articulation_assistant(db)
    
    suggestion = assistant.suggest_articulation(
        user_id=request.user_id,
        original_text=request.original_text,
        context=request.context
    )
    
    return ArticulationResponse(
        suggestion_id=suggestion.id,
        user_id=suggestion.user_id,
        original_text=suggestion.original_text,
        suggested_text=suggestion.suggested_text,
        version=suggestion.version,
        human_refined=suggestion.human_refined,
        checkpoint_id=suggestion.checkpoint_id,
        created_at=suggestion.created_at.isoformat()
    )


@router.post("/{suggestion_id}/refine", response_model=ArticulationResponse)
async def refine_suggestion(
    suggestion_id: int,
    request: RefineRequest,
    db: Session = Depends(get_db)
):
    """Human refines AI suggestion."""
    assistant = create_articulation_assistant(db)
    
    try:
        suggestion = assistant.human_refine_suggestion(
            suggestion_id=suggestion_id,
            refined_text=request.refined_text
        )
        
        return ArticulationResponse(
            suggestion_id=suggestion.id,
            user_id=suggestion.user_id,
            original_text=suggestion.original_text,
            suggested_text=suggestion.suggested_text,
            version=suggestion.version,
            human_refined=suggestion.human_refined,
            checkpoint_id=suggestion.checkpoint_id,
            created_at=suggestion.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{suggestion_id}", response_model=ArticulationResponse)
async def get_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db)
):
    """Get suggestion by ID."""
    assistant = create_articulation_assistant(db)
    suggestion = assistant.get_suggestion(suggestion_id)
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    return ArticulationResponse(
        suggestion_id=suggestion.id,
        user_id=suggestion.user_id,
        original_text=suggestion.original_text,
        suggested_text=suggestion.suggested_text,
        version=suggestion.version,
        human_refined=suggestion.human_refined,
        checkpoint_id=suggestion.checkpoint_id,
        created_at=suggestion.created_at.isoformat()
    )


@router.get("/user/{user_id}", response_model=List[ArticulationResponse])
async def list_user_suggestions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """List all suggestions for a user."""
    assistant = create_articulation_assistant(db)
    suggestions = assistant.list_user_suggestions(user_id)
    
    return [
        ArticulationResponse(
            suggestion_id=s.id,
            user_id=s.user_id,
            original_text=s.original_text,
            suggested_text=s.suggested_text,
            version=s.version,
            human_refined=s.human_refined,
            checkpoint_id=s.checkpoint_id,
            created_at=s.created_at.isoformat()
        )
        for s in suggestions
    ]


