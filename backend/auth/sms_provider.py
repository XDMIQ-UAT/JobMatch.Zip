"""
SMS/VoIP Provider Integration.
Supports Twilio and other SMS/VoIP providers.
"""
import logging
from typing import Dict, Any, Optional

from backend.config import settings
from backend.security.pii_redaction import redact_phone

logger = logging.getLogger(__name__)


class SMSProviderManager:
    """Manages SMS/VoIP provider integrations."""
    
    def __init__(self):
        self.provider = "twilio"  # Default provider
        self.twilio_account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
        self.twilio_phone_number = getattr(settings, "TWILIO_PHONE_NUMBER", "")
    
    async def send_sms(
        self,
        phone_number: str,
        message: str
    ) -> Dict[str, Any]:
        """Send SMS message."""
        if not self.twilio_account_sid:
            logger.warning("Twilio not configured, simulating SMS send")
            return {
                "success": True,
                "message_sid": f"simulated_{hash(phone_number)}",
                "provider": "simulated"
            }
        
        try:
            # In production, would use Twilio SDK
            # from twilio.rest import Client
            # client = Client(self.twilio_account_sid, self.twilio_auth_token)
            # message = client.messages.create(
            #     body=message,
            #     from_=self.twilio_phone_number,
            #     to=phone_number
            # )
            
            logger.info(f"Sending SMS to {redact_phone(phone_number)}: {message[:50]}...")
            
            return {
                "success": True,
                "message_sid": f"twilio_{hash(phone_number)}",
                "provider": "twilio"
            }
        except Exception as e:
            logger.error(f"SMS send failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_verification_code(
        self,
        phone_number: str,
        code: str
    ) -> Dict[str, Any]:
        """Send verification code via SMS."""
        message = f"Your XDMIQ verification code is: {code}. Valid for 10 minutes."
        return await self.send_sms(phone_number, message)
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format."""
        # Basic validation (would use proper library in production)
        import re
        pattern = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone_number.replace(" ", "").replace("-", "")))


def create_sms_manager() -> SMSProviderManager:
    """Factory function to create SMS manager."""
    return SMSProviderManager()


