"""
Twilio Voice API endpoints for JobMatch.
Handles incoming voice calls and provides TwiML responses.
"""
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import Response
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])


def generate_twiml_response(message: str, gather: bool = False, 
                            gather_action: str = None, 
                            gather_num_digits: int = 1) -> str:
    """
    Generate TwiML response for Twilio with natural-sounding neural voice.
    
    Args:
        message: Text to speak to the caller
        gather: Whether to gather input from caller
        gather_action: URL to POST gathered input to
        gather_num_digits: Number of digits to gather
    
    Returns:
        TwiML XML string with neural voice for natural speech
    """
    # Use neural voice for more natural sound (Joanna-Neural sounds more natural than Matthew)
    # Neural voices have better intonation and natural pauses
    voice_attrs = 'language="en-US" voice="Polly.Joanna-Neural"'
    
    twiml = '<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n'
    
    if gather:
        twiml += f'  <Gather action="{gather_action}" numDigits="{gather_num_digits}" timeout="10">\n'
        twiml += f'    <Say {voice_attrs}>{message}</Say>\n'
        twiml += '  </Gather>\n'
        # Fallback if no input
        twiml += f'  <Say {voice_attrs}>We didn\'t receive any input. Goodbye!</Say>\n'
    else:
        twiml += f'  <Say {voice_attrs}>{message}</Say>\n'
    
    twiml += '</Response>'
    return twiml


@router.post("/incoming")
@router.get("/incoming")
async def handle_incoming_call(
    request: Request,
    From: Optional[str] = Form(None),
    To: Optional[str] = Form(None),
    CallSid: Optional[str] = Form(None),
    CallStatus: Optional[str] = Form(None)
):
    """
    Handle incoming Twilio voice calls.
    Twilio webhook URL: https://jobmatch.zip/api/voice/incoming
    
    Query params (from Twilio):
        From: Caller's phone number
        To: Called phone number
        CallSid: Unique call identifier
        CallStatus: Call status (ringing, in-progress, etc.)
    """
    # Log the incoming call
    logger.info(f"Incoming call - From: {From}, To: {To}, CallSid: {CallSid}, Status: {CallStatus}")
    
    # Generate welcome message with natural pronunciation
    # Fixed: "L L C" -> "LLC", "A I" -> "AI"
    # Improved phrasing for natural flow
    message = (
        "Welcome to Job Match dot zip, the AI powered job matching platform for LLC owners. "
        "Press 1 to learn about our services. "
        "Press 2 to speak with our AI assistant. "
        "Press 3 to schedule a callback. "
        "Press 9 to end this call."
    )
    
    # Generate TwiML with digit gathering
    twiml = generate_twiml_response(
        message=message,
        gather=True,
        gather_action="/api/voice/menu",
        gather_num_digits=1
    )
    
    return Response(content=twiml, media_type="application/xml")


@router.post("/menu")
async def handle_menu_selection(
    request: Request,
    Digits: Optional[str] = Form(None),
    CallSid: Optional[str] = Form(None)
):
    """
    Handle menu selection from caller.
    
    Args:
        Digits: The digit(s) pressed by caller
        CallSid: Unique call identifier
    """
    logger.info(f"Menu selection - CallSid: {CallSid}, Digits: {Digits}")
    
    if not Digits:
        message = "We didn't receive any input. Goodbye!"
        twiml = generate_twiml_response(message)
        return Response(content=twiml, media_type="application/xml")
    
    # Handle different menu options with natural pronunciation
    if Digits == "1":
        message = (
            "Job Match helps LLC owners find perfect job matches using AI. "
            "We analyze your skills, experience, and goals to match you with opportunities. "
            "Visit jobmatch dot zip to get started. Goodbye!"
        )
    elif Digits == "2":
        message = (
            "Our AI assistant is available on our website at jobmatch dot zip. "
            "You can chat with our intelligent matching system twenty four seven. "
            "Visit us online to get started. Goodbye!"
        )
    elif Digits == "3":
        message = (
            "To schedule a callback, please visit jobmatch dot zip and fill out our contact form. "
            "Our team will reach out within twenty four hours. Goodbye!"
        )
    elif Digits == "9":
        message = "Thank you for calling Job Match. Goodbye!"
    else:
        message = "Invalid selection. Please visit jobmatch dot zip for assistance. Goodbye!"
    
    twiml = generate_twiml_response(message)
    return Response(content=twiml, media_type="application/xml")


@router.post("/status")
async def handle_call_status(
    request: Request,
    CallSid: Optional[str] = Form(None),
    CallStatus: Optional[str] = Form(None),
    CallDuration: Optional[str] = Form(None)
):
    """
    Handle call status callbacks from Twilio.
    Optional webhook for tracking call completion, duration, etc.
    
    Args:
        CallSid: Unique call identifier
        CallStatus: completed, busy, no-answer, failed, canceled
        CallDuration: Duration in seconds
    """
    logger.info(f"Call status update - CallSid: {CallSid}, Status: {CallStatus}, Duration: {CallDuration}")
    
    # You could store call logs in database here
    # await store_call_log(CallSid, CallStatus, CallDuration)
    
    return {"status": "received"}


@router.get("/health")
async def voice_health_check():
    """Health check for voice service."""
    return {
        "status": "healthy",
        "service": "voice",
        "endpoints": {
            "incoming": "/api/voice/incoming",
            "menu": "/api/voice/menu",
            "status": "/api/voice/status"
        }
    }
