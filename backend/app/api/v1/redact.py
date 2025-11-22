from fastapi import APIRouter
from pydantic import BaseModel

from app.services.pii_redactor import PIIRedactor

router = APIRouter()
redactor = PIIRedactor()

class RedactRequest(BaseModel):
    text: str

class RedactResponse(BaseModel):
    original_text: str
    redacted_text: str
    removed_items: list
    is_safe: bool
    redaction_summary: str

@router.post("/text", response_model=RedactResponse)
async def redact_pii(request: RedactRequest):
    """
    Detect and redact PII from text.
    
    Returns original, redacted version, and list of removed items for user verification.
    """
    result = redactor.redact_pii(request.text)
    
    return RedactResponse(
        original_text=result["original_text"],
        redacted_text=result["redacted_text"],
        removed_items=result["removed_items"],
        is_safe=result["is_safe"],
        redaction_summary=result["redaction_summary"]
    )
