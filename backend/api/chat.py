"""
Chat API endpoint with AI-powered responses.
Integrates with conversations system and uses unified LLM client.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from database.connection import get_db
from llm import get_llm_client

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


class JobMatchChatRequest(BaseModel):
    """Job match chat request model."""
    message: str
    context: Dict[str, any]
    conversationHistory: Optional[List[Dict[str, str]]] = None


class JobMatchChatResponse(BaseModel):
    """Job match chat response model."""
    message: str
    suggestedJobs: Optional[List[str]] = None
    provider: str
    model: str


@router.post("/job-match", response_model=JobMatchChatResponse)
async def job_match_chat(
    request: JobMatchChatRequest,
    db: Session = Depends(get_db)
):
    """
    Personalized job matching chat for subscribed users.
    
    This endpoint provides AI-powered job search assistance focused ONLY on:
    - Finding matching job opportunities
    - Understanding user requirements
    - Suggesting relevant positions
    
    DOES NOT provide:
    - Interview preparation
    - Resume writing
    - Career coaching
    
    Example request:
    ```json
    {
        "message": "I'm looking for remote Python developer roles",
        "context": {
            "userId": "anonymous-123",
            "skills": ["Python", "FastAPI", "React"],
            "preferences": "remote",
            "location": "San Francisco"
        },
        "conversationHistory": [
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous response"}
        ]
    }
    ```
    """
    try:
        llm = get_llm_client()
        
        # Build system prompt for job matching focus
        skills_str = ", ".join(request.context.get("skills", [])) if request.context.get("skills") else "not specified"
        location = request.context.get("location", "not specified")
        preferences = request.context.get("preferences", "not specified")
        
        system_prompt = f"""You are a specialized job matching assistant for JobMatch. Your ONLY purpose is to help users find job opportunities that match their skills and preferences.

User Profile:
- Skills: {skills_str}
- Location: {location}
- Preferences: {preferences}

Your responsibilities:
1. Help users articulate what kind of roles they're looking for
2. Suggest job types, industries, or companies that match their profile
3. Ask clarifying questions to better understand their needs
4. Provide insights about job market trends relevant to their search

IMPORTANT RESTRICTIONS:
- DO NOT offer interview preparation advice
- DO NOT write or review resumes
- DO NOT provide career coaching beyond job matching
- Keep responses focused, helpful, and conversational
- If asked about non-job-matching topics, politely redirect to job search

Your goal is to help users discover opportunities they might not have considered and match them with roles where they can succeed."""
        
        # Build message history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided (last 10 messages for context)
        if request.conversationHistory:
            for msg in request.conversationHistory[-10:]:
                if msg.get("role") in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Get response from LLM
        response = llm.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        logger.info(f"Job match chat response generated for user {request.context.get('userId')}")
        
        # TODO: Extract any job IDs or suggestions from the response
        # This would require integration with job database
        suggested_jobs = None
        
        return JobMatchChatResponse(
            message=response,
            suggestedJobs=suggested_jobs,
            provider=llm.provider,
            model=llm.model
        )
    
    except Exception as e:
        logger.error(f"Job match chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate job match response: {str(e)}"
        )


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
