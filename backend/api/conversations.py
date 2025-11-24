"""
Conversation API endpoints for saving and retrieving conversations.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import secrets
import hashlib
from datetime import datetime

from database.connection import get_db
from database.models import Conversation, AnonymousUser

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


class Message(BaseModel):
    """Message model."""
    id: str
    type: str  # 'bot' | 'user'
    content: str
    timestamp: str
    questionId: Optional[str] = None
    quickReplies: Optional[List[str]] = None
    authProviders: Optional[List[Dict[str, Any]]] = None


class ConversationSaveRequest(BaseModel):
    """Request model for saving a conversation."""
    session_id: Optional[str] = None  # If not provided, will generate one
    user_id: Optional[str] = None  # Anonymous ID
    conversation_type: str = "assessment"
    messages: List[Message]
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Response model for conversation."""
    session_id: str
    user_id: Optional[str]
    conversation_type: str
    messages: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


def generate_session_id() -> str:
    """Generate a unique session ID."""
    random_bytes = secrets.token_bytes(32)
    session_id = hashlib.sha256(random_bytes).hexdigest()
    return session_id


@router.post("/save", response_model=ConversationResponse)
async def save_conversation(
    request: ConversationSaveRequest,
    db: Session = Depends(get_db)
):
    """Save a conversation."""
    # Generate session_id if not provided
    session_id = request.session_id or generate_session_id()
    
    # Validate user_id if provided
    if request.user_id:
        user = db.query(AnonymousUser).filter(AnonymousUser.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    
    # Convert messages to dict format for storage
    messages_data = [msg.dict() for msg in request.messages]
    
    # Check if conversation already exists
    existing = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    
    if existing:
        # Update existing conversation
        existing.messages = messages_data
        existing.meta_data = request.meta_data or existing.meta_data
        existing.updated_at = datetime.utcnow()
        if request.user_id:
            existing.user_id = request.user_id
    else:
        # Create new conversation
        conversation = Conversation(
            session_id=session_id,
            user_id=request.user_id,
            conversation_type=request.conversation_type,
            messages=messages_data,
            metadata=request.meta_data or {}
        )
        db.add(conversation)
    
    db.commit()
    
    if existing:
        db.refresh(existing)
        conversation = existing
    else:
        db.refresh(conversation)
    
    return ConversationResponse(
        session_id=conversation.session_id,
        user_id=conversation.user_id,
        conversation_type=conversation.conversation_type,
        messages=conversation.messages,
        metadata=conversation.meta_data,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat()
    )


@router.get("/{session_id}", response_model=ConversationResponse)
async def get_conversation(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get conversation by session ID."""
    conversation = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationResponse(
        session_id=conversation.session_id,
        user_id=conversation.user_id,
        conversation_type=conversation.conversation_type,
        messages=conversation.messages,
        metadata=conversation.meta_data,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat()
    )


@router.get("/user/{user_id}", response_model=List[ConversationResponse])
async def list_user_conversations(
    user_id: str,
    conversation_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all conversations for a user."""
    query = db.query(Conversation).filter(Conversation.user_id == user_id)
    
    if conversation_type:
        query = query.filter(Conversation.conversation_type == conversation_type)
    
    conversations = query.order_by(Conversation.created_at.desc()).limit(limit).all()
    
    return [
        ConversationResponse(
            session_id=c.session_id,
            user_id=c.user_id,
            conversation_type=c.conversation_type,
            messages=c.messages,
            metadata=c.meta_data,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat()
        )
        for c in conversations
    ]

