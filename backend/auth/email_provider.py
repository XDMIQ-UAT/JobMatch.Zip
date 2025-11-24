"""
Email Provider Integration.
Supports SMTP and Amazon SES email service providers.
"""
import logging
from typing import Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import boto3
from botocore.exceptions import ClientError

from config import settings
from security.pii_redaction import redact_email

logger = logging.getLogger(__name__)


class EmailProviderManager:
    """Manages email provider integrations."""
    
    def __init__(self):
        self.provider_mode = getattr(settings, "EMAIL_PROVIDER_MODE", "smtp").lower()
        
        # SMTP settings
        self.smtp_host = getattr(settings, "SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = getattr(settings, "SMTP_PORT", 587)
        self.smtp_user = getattr(settings, "SMTP_USER", "")
        self.smtp_password = getattr(settings, "SMTP_PASSWORD", "")
        
        # Amazon SES settings
        self.aws_access_key_id = getattr(settings, "AWS_ACCESS_KEY_ID", "")
        self.aws_secret_access_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", "")
        self.aws_region = getattr(settings, "AWS_REGION", "us-west-2")
        self.ses_region = getattr(settings, "SES_REGION", "us-west-2")
        self.ses_from_email = getattr(settings, "SES_FROM_EMAIL", "")
        
        # Default from email (SES takes precedence if set)
        self.from_email = self.ses_from_email or getattr(settings, "FROM_EMAIL", "noreply@xdmiq.com")
        
        # Initialize SES client if credentials are available
        self.ses_client = None
        if self.provider_mode == "ses" and self.aws_access_key_id and self.aws_secret_access_key:
            try:
                self.ses_client = boto3.client(
                    'ses',
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.ses_region
                )
                # Test connection by getting send quota (doesn't require verified email)
                try:
                    quota = self.ses_client.get_send_quota()
                    logger.info(f"Amazon SES client initialized for region: {self.ses_region} (Max 24h Send: {quota.get('Max24HourSend', 'N/A')})")
                except Exception as quota_error:
                    logger.warning(f"SES client created but quota check failed: {quota_error}. Email sending may still work.")
            except Exception as e:
                logger.error(f"Failed to initialize SES client: {e}", exc_info=True)
                self.ses_client = None
                logger.warning("Falling back to SMTP or simulated mode")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email using configured provider (SES or SMTP)."""
        # Use SES if configured
        if self.provider_mode == "ses" and self.ses_client:
            return await self._send_email_ses(to_email, subject, html_body, text_body)
        
        # Fallback to SMTP
        return await self._send_email_smtp(to_email, subject, html_body, text_body)
    
    async def _send_email_ses(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email using Amazon SES."""
        if not self.ses_client:
            logger.warning("SES client not initialized, falling back to SMTP")
            return await self._send_email_smtp(to_email, subject, html_body, text_body)
        
        try:
            # Prepare message
            message = {
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                }
            }
            
            # Add text body if provided
            if text_body:
                message['Body']['Text'] = {'Data': text_body, 'Charset': 'UTF-8'}
            
            # Send email via SES
            # Ensure from_email is set correctly
            source_email = self.from_email or self.ses_from_email or "info@jobmatch.zip"
            response = self.ses_client.send_email(
                Source=source_email,
                Destination={'ToAddresses': [to_email]},
                Message=message
            )
            
            message_id = response.get('MessageId', '')
            logger.info(f"SES email sent to {redact_email(to_email)}: {subject} (MessageId: {message_id})")
            
            return {
                "success": True,
                "message_id": message_id,
                "provider": "ses"
            }
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"SES email send failed ({error_code}): {error_message}")
            
            # Provide helpful error messages for common issues
            if error_code == 'MessageRejected':
                if 'Email address is not verified' in error_message:
                    if self.from_email in error_message:
                        error_message = "Unable to send email. Please contact support."
                    else:
                        error_message = f"Unable to send email to {to_email}. Please verify your email address or contact support."
                elif 'Account is in the sandbox' in error_message or 'sandbox' in error_message.lower():
                    error_message = f"Unable to send email to {to_email}. Please verify your email address or contact support."
                elif 'not verified' in error_message.lower():
                    error_message = "Email verification required. Please contact support."
            
            return {
                "success": False,
                "error": f"{error_code}: {error_message}",
                "provider": "ses"
            }
        except Exception as e:
            logger.error(f"SES email send failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "ses"
            }
    
    async def _send_email_smtp(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email using SMTP."""
        if not self.smtp_user:
            logger.warning("SMTP not configured, simulating email send")
            return {
                "success": True,
                "message_id": f"simulated_{hash(to_email)}",
                "provider": "simulated"
            }
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"SMTP email sent to {redact_email(to_email)}: {subject}")
            
            return {
                "success": True,
                "message_id": f"email_{hash(to_email)}",
                "provider": "smtp"
            }
        except Exception as e:
            logger.error(f"SMTP email send failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "smtp"
            }
    
    async def send_verification_email(
        self,
        email: str,
        code: str
    ) -> Dict[str, Any]:
        """Send verification code email."""
        subject = "Your XDMIQ Verification Code"
        html_body = f"""
        <html>
        <body>
            <h2>XDMIQ Verification Code</h2>
            <p>Your verification code is: <strong>{code}</strong></p>
            <p>This code is valid for 10 minutes.</p>
            <p>If you didn't request this code, please ignore this email.</p>
        </body>
        </html>
        """
        text_body = f"Your XDMIQ verification code is: {code}. Valid for 10 minutes."
        
        return await self.send_email(email, subject, html_body, text_body)
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


def create_email_manager() -> EmailProviderManager:
    """Factory function to create email manager."""
    return EmailProviderManager()


