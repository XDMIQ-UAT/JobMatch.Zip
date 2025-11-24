"""
Example Chat Endpoint using unified LLM client.
This shows how to integrate OpenRouter/OpenAI/Ollama into your chat system.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import logging

from llm import get_llm_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str  # "user", "assistant", or "system"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 1000


class ChatResponse(BaseModel):
    message: str
    provider: str
    model: str


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a chat message and get AI response.
    
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
        
        # Convert Pydantic models to dicts
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        # Get response from LLM
        response = llm.chat(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return ChatResponse(
            message=response,
            provider=llm.provider,
            model=llm.model
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def chat_status():
    """Check LLM service status."""
    try:
        llm = get_llm_client()
        available = llm.is_available()
        
        return {
            "available": available,
            "provider": llm.provider,
            "model": llm.model
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {
            "available": False,
            "error": str(e)
        }
