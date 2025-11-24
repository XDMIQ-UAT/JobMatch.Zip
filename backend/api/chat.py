"""
Chat API endpoint with AI-powered responses.
Integrates with conversations system and uses unified LLM client.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from backend.database.connection import get_db
from backend.llm import get_llm_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # "user", "assistant", or "system"
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 1000
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    provider: str
    model: str
    session_id: Optional[str] = None


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Send a chat message and get AI response.
    
    This endpoint uses the configured LLM provider (OpenRouter, OpenAI, or Ollama)
    to generate intelligent responses based on conversation context.
    
    Example request:
    ```json
    {
        "messages": [
            {"role": "system", "content": "You are a helpful job matching assistant."},
            {"role": "user", "content": "What authentication methods do you support?"}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    ```
    """
    try:
        llm = get_llm_client()
        
        # Convert Pydantic models to dicts for LLM client
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        # Get response from LLM
        response = llm.chat(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        logger.info(f"Chat response generated using {llm.provider}/{llm.model}")
        
        return ChatResponse(
            message=response,
            provider=llm.provider,
            model=llm.model,
            session_id=request.session_id
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate chat response: {str(e)}"
        )


@router.get("/status")
async def chat_status():
    """
    Check LLM service status and configuration.
    
    Returns information about the active LLM provider and whether it's available.
    """
    try:
        llm = get_llm_client()
        
        # Quick availability check (will be False if service is down)
        available = True
        try:
            # Don't do full test on every status check for performance
            # Just check if client initialized
            available = llm._client is not None
        except Exception:
            available = False
        
        return {
            "available": available,
            "provider": llm.provider,
            "model": llm.model,
            "status": "operational" if available else "unavailable"
        }
    
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {
            "available": False,
            "error": str(e),
            "status": "error"
        }


@router.post("/test")
async def test_chat():
    """
    Test endpoint to verify LLM integration is working.
    
    Sends a simple test message and returns the response.
    """
    try:
        llm = get_llm_client()
        
        test_messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Respond briefly."
            },
            {
                "role": "user",
                "content": "Say 'Hello! I am working correctly.' in a friendly way."
            }
        ]
        
        response = llm.chat(
            messages=test_messages,
            temperature=0.7,
            max_tokens=50
        )
        
        return {
            "success": True,
            "response": response,
            "provider": llm.provider,
            "model": llm.model
        }
    
    except Exception as e:
        logger.error(f"Test chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Test failed: {str(e)}"
        )
