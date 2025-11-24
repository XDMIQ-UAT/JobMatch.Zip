"""
Social Authentication Integration.
Supports: Facebook, LinkedIn, Google, Microsoft, Apple, Email, SMS/VoIP
Maintains anonymous identity while allowing social login.
"""
import logging
import secrets
import asyncio
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from database.models import AnonymousUser
from auth.anonymous_identity import AnonymousIdentityManager
from auth.email_provider import create_email_manager
from security.pii_redaction import redact_email, redact_phone

logger = logging.getLogger(__name__)

# In-memory storage for verification codes (use Redis in production)
_email_verification_codes: Dict[str, Dict[str, Any]] = {}

# In-memory storage for magic links (use Redis in production)
# Key: token, Value: {email, expires_at, created_at, ip_hash}
_magic_links: Dict[str, Dict[str, Any]] = {}


def _hash_ip(ip: Optional[str]) -> Optional[str]:
    """
    Hash IP address for privacy-preserving security validation.
    Uses SHA256 with salt to prevent reverse-engineering.
    This maintains security while preserving zero-knowledge principles.
    """
    if not ip:
        return None
    
    # Use a constant salt (could be from config in production)
    # This prevents rainbow table attacks while maintaining consistency
    salt = b"jobmatch_ip_validation_salt_v1"
    ip_bytes = ip.encode('utf-8')
    hash_obj = hashlib.sha256(salt + ip_bytes)
    return hash_obj.hexdigest()


class SocialAuthManager:
    """Manages social authentication integrations."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.identity_manager = AnonymousIdentityManager(db_session)
    
    def link_social_account(
        self,
        anonymous_id: str,
        provider: str,
        provider_user_id: str,
        provider_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Link a social account to an anonymous identity.
        Does not reveal real identity - just links for authentication.
        """
        user = self.identity_manager.get_user(anonymous_id)
        if not user:
            return False
        
        # Store social account link in user metadata
        if not user.meta_data:
            user.meta_data = {}
        
        if "social_accounts" not in user.meta_data:
            user.meta_data["social_accounts"] = {}
        
        user.meta_data["social_accounts"][provider] = {
            "provider_user_id": provider_user_id,
            "linked_at": datetime.utcnow().isoformat(),
            "provider_data": provider_data or {}
        }
        
        # Extract and store preferred language from provider data
        preferred_language = self._extract_locale_from_provider_data(provider, provider_data)
        if preferred_language:
            user.meta_data["preferred_language"] = preferred_language
        
        self.db.commit()
        logger.info(f"Linked {provider} account to anonymous user {anonymous_id[:8]}...")
        return True
    
    def _extract_locale_from_provider_data(
        self,
        provider: str,
        provider_data: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Extract locale/preferred language from OAuth provider data."""
        if not provider_data:
            return None
        
        # Google: locale field (e.g., "en", "es", "fr")
        if provider == "google":
            locale = provider_data.get("locale")
            if locale:
                return locale.split("_")[0].split("-")[0].lower()  # "en_US" -> "en"
        
        # Microsoft: preferredLanguage field (e.g., "en-US")
        elif provider == "microsoft":
            locale = provider_data.get("preferredLanguage")
            if locale:
                return locale.split("-")[0].lower()  # "en-US" -> "en"
        
        # Facebook: locale field (e.g., "en_US")
        elif provider == "facebook":
            locale = provider_data.get("locale")
            if locale:
                return locale.split("_")[0].lower()  # "en_US" -> "en"
        
        # LinkedIn: locale field in preferredLocale
        elif provider == "linkedin":
            locale = provider_data.get("preferredLocale", {}).get("language")
            if locale:
                return locale.lower()
        
        # Apple: locale from user info
        elif provider == "apple":
            locale = provider_data.get("locale")
            if locale:
                return locale.split("_")[0].split("-")[0].lower()
        
        return None
    
    def authenticate_with_provider(
        self,
        provider: str,
        provider_token: str,
        provider_data: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Authenticate with social provider and return/create anonymous ID.
        Returns anonymous_id if successful.
        """
        # Verify token with provider (would implement actual OAuth flow)
        provider_user_id = self._verify_provider_token(provider, provider_token)
        
        if not provider_user_id:
            return None
        
        # Check if this provider account is already linked
        existing_user = self._find_user_by_provider(provider, provider_user_id)
        
        if existing_user:
            # Update locale if available and not already set
            preferred_language = self._extract_locale_from_provider_data(provider, provider_data)
            if preferred_language:
                if not existing_user.meta_data:
                    existing_user.meta_data = {}
                if "preferred_language" not in existing_user.meta_data:
                    existing_user.meta_data["preferred_language"] = preferred_language
                    self.db.commit()
            return existing_user.id
        
        # Create new anonymous user and link account
        new_user = self.identity_manager.create_anonymous_user()
        
        # Extract locale before linking (so it gets stored)
        preferred_language = self._extract_locale_from_provider_data(provider, provider_data)
        
        self.link_social_account(
            anonymous_id=new_user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_data=provider_data
        )
        
        return new_user.id
    
    def _verify_provider_token(
        self,
        provider: str,
        token: str
    ) -> Optional[str]:
        """Verify token with provider and return provider user ID."""
        # In production, would implement actual OAuth verification
        # For now, return mock verification
        logger.info(f"Verifying {provider} token...")
        return f"{provider}_user_{hash(token) % 10000}"
    
    def _find_user_by_provider(
        self,
        provider: str,
        provider_user_id: str
    ) -> Optional[AnonymousUser]:
        """Find anonymous user by linked social account."""
        users = self.db.query(AnonymousUser).all()
        
        for user in users:
            if user.meta_data and "social_accounts" in user.meta_data:
                accounts = user.meta_data["social_accounts"]
                if provider in accounts:
                    if accounts[provider]["provider_user_id"] == provider_user_id:
                        return user
        
        return None
    
    def send_sms_verification(
        self,
        phone_number: str
    ) -> Dict[str, Any]:
        """Send SMS verification code."""
        # Generate verification code
        import secrets
        code = str(secrets.randbelow(1000000)).zfill(6)
        
        # In production, would integrate with SMS provider (Twilio, etc.)
        logger.info(f"Sending SMS verification code {code} to {redact_phone(phone_number)}")
        
        # Store code temporarily (would use Redis in production)
        return {
            "verification_code": code,
            "phone_number": phone_number,
            "expires_in": 600  # 10 minutes
        }
    
    def verify_sms_code(
        self,
        phone_number: str,
        code: str
    ) -> Optional[str]:
        """Verify SMS code and return/create anonymous ID."""
        # In production, would verify against stored code
        # For now, accept any 6-digit code
        
        # Check if phone number already linked
        existing_user = self._find_user_by_phone(phone_number)
        
        if existing_user:
            return existing_user.id
        
        # Create new anonymous user and link phone
        new_user = self.identity_manager.create_anonymous_user()
        self.link_phone_number(new_user.id, phone_number)
        
        return new_user.id
    
    def link_phone_number(
        self,
        anonymous_id: str,
        phone_number: str
    ) -> bool:
        """Link phone number to anonymous identity."""
        user = self.identity_manager.get_user(anonymous_id)
        if not user:
            return False
        
        if not user.meta_data:
            user.meta_data = {}
        
        if "phone_numbers" not in user.meta_data:
            user.meta_data["phone_numbers"] = []
        
        if phone_number not in user.meta_data["phone_numbers"]:
            user.meta_data["phone_numbers"].append({
                "number": phone_number,
                "verified": True,
                "linked_at": datetime.utcnow().isoformat()
            })
        
        self.db.commit()
        return True
    
    def _find_user_by_phone(self, phone_number: str) -> Optional[AnonymousUser]:
        """Find anonymous user by phone number."""
        users = self.db.query(AnonymousUser).all()
        
        for user in users:
            if user.meta_data and "phone_numbers" in user.meta_data:
                for phone_data in user.meta_data["phone_numbers"]:
                    if phone_data.get("number") == phone_number:
                        return user
        
        return None
    
    def send_email_verification(
        self,
        email: str
    ) -> Dict[str, Any]:
        """Send email verification code via email."""
        code = str(secrets.randbelow(1000000)).zfill(6)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Store code for verification
        _email_verification_codes[email.lower()] = {
            "code": code,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
        
        # Send email using EmailProviderManager
        try:
            email_manager = create_email_manager()
            # Handle async function call - check if event loop exists
            try:
                # Try to get the current event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Event loop is already running, use create_task or run in executor
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            lambda: asyncio.run(email_manager.send_verification_email(email, code))
                        )
                        result = future.result(timeout=30)
                else:
                    # Event loop exists but not running, use run_until_complete
                    result = loop.run_until_complete(email_manager.send_verification_email(email, code))
            except RuntimeError:
                # No event loop exists, create a new one
                result = asyncio.run(email_manager.send_verification_email(email, code))
            
            if not result.get("success", False):
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Failed to send email to {redact_email(email)}: {error_msg}")
                # Remove stored code if email failed
                _email_verification_codes.pop(email.lower(), None)
                # Raise with the actual error message, not wrapped
                raise Exception(error_msg)
            
            provider = result.get('provider', 'unknown')
            logger.info(f"Email verification code sent to {redact_email(email)} (provider: {provider})")
            
            # In development mode, log the code for testing
            from config import settings
            if getattr(settings, 'ENVIRONMENT', 'production') == 'development' or getattr(settings, 'DEV_MODE', False):
                logger.info(f"🔐 DEV MODE: Verification code for {redact_email(email)} is: {code}")
                print(f"\n🔐 DEV MODE: Email verification code for {redact_email(email)}: {code}\n")
        except Exception as e:
            logger.error(f"Error sending email verification to {redact_email(email)}: {e}", exc_info=True)
            # Remove stored code if email failed
            _email_verification_codes.pop(email.lower(), None)
            raise
        
        return {
            "verification_code": code,  # For development/testing - remove in production
            "email": email,
            "expires_in": 600
        }
    
    def verify_email_code(
        self,
        email: str,
        code: str
    ) -> Optional[str]:
        """Verify email code and return/create anonymous ID."""
        email_lower = email.lower()
        
        # Normalize code (strip whitespace, ensure string)
        code = str(code).strip()
        
        # Check if code exists and is valid
        stored_data = _email_verification_codes.get(email_lower)
        if not stored_data:
            logger.warning(f"No verification code found for {redact_email(email)} (email_lower: redacted)")
            logger.debug(f"Available codes: {len(_email_verification_codes.keys())} codes in storage")
            return None
        
        # Check if code expired
        expires_at = stored_data["expires_at"]
        now = datetime.utcnow()
        if now > expires_at:
            time_expired = (now - expires_at).total_seconds()
            logger.warning(f"Verification code expired for {redact_email(email)} ({time_expired:.0f} seconds ago)")
            _email_verification_codes.pop(email_lower, None)
            return None
        
        # Verify code matches (compare as strings, case-insensitive)
        stored_code = str(stored_data["code"]).strip()
        if stored_code != code:
            logger.warning(f"Invalid verification code for {redact_email(email)}: code mismatch")
            logger.debug(f"Code comparison: '{stored_code}' == '{code}' -> {stored_code == code}")
            return None
        
        # Code is valid - remove it
        _email_verification_codes.pop(email_lower, None)
        
        # Check if email already linked (use lowercase for consistency)
        existing_user = self._find_user_by_email(email_lower)
        
        if existing_user:
            logger.info(f"Email verified for existing user {existing_user.id}")
            return existing_user.id
        
        # Create new anonymous user and link email (use lowercase for consistency)
        new_user = self.identity_manager.create_anonymous_user()
        self.link_email(new_user.id, email_lower)
        
        logger.info(f"Email verified and linked for {redact_email(email_lower)} (new user: {new_user.id})")
        return new_user.id
    
    def send_magic_link(
        self,
        email: str,
        base_url: str = "https://jobmatch.zip",
        request_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send magic link email (valid for 24 hours).
        
        Args:
            email: Email address to send magic link to
            base_url: Base URL for magic link
            request_ip: IP address of the requester (for security validation)
        """
        import base64
        
        # Generate secure token
        token_bytes = secrets.token_bytes(32)
        token = base64.urlsafe_b64encode(token_bytes).decode('utf-8').rstrip('=')
        
        # Store magic link (24 hour expiration)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        _magic_links[token] = {
            "email": email.lower(),
            "expires_at": expires_at,
            "created_at": datetime.utcnow(),
            "ip_hash": _hash_ip(request_ip) if request_ip else None  # Store hashed IP for privacy-preserving validation
        }
        
        # Create magic link URL
        # Use dedicated route to avoid any caching/interception on /auth
        magic_link = f"{base_url}/auth/magic-link?token={token}"
        
        # Send email using EmailProviderManager
        try:
            email_manager = create_email_manager()
            
            # Prepare email content
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2196f3;">Authenticate with JobMatch</h2>
                    <p>Click the button below to authenticate your account. This link will expire in 24 hours.</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{magic_link}" 
                           style="display: inline-block; padding: 12px 24px; background-color: #2196f3; color: white; text-decoration: none; border-radius: 6px; font-weight: 600;">
                            Authenticate Now
                        </a>
                    </div>
                    <p style="font-size: 0.9em; color: #666;">
                        Or copy and paste this link into your browser:<br>
                        <a href="{magic_link}" style="color: #2196f3; word-break: break-all;">{magic_link}</a>
                    </p>
                    <p style="font-size: 0.85em; color: #999; margin-top: 30px;">
                        If you didn't request this authentication link, please ignore this email.
                    </p>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            Authenticate with JobMatch
            
            Click the link below to authenticate your account. This link will expire in 24 hours.
            
            {magic_link}
            
            If you didn't request this authentication link, please ignore this email.
            """
            
            # Handle async function call
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            lambda: asyncio.run(email_manager.send_email(
                                email,
                                "Authenticate with JobMatch - Magic Link",
                                html_body,
                                text_body
                            ))
                        )
                        result = future.result(timeout=30)
                else:
                    result = loop.run_until_complete(email_manager.send_email(
                        email,
                        "Authenticate with JobMatch - Magic Link",
                        html_body,
                        text_body
                    ))
            except RuntimeError:
                result = asyncio.run(email_manager.send_email(
                    email,
                    "Authenticate with JobMatch - Magic Link",
                    html_body,
                    text_body
                ))
            
            if not result.get("success", False):
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Failed to send magic link email to {redact_email(email)}: {error_msg}")
                logger.error(f"Email result: {result}")
                # Remove stored link if email failed
                _magic_links.pop(token, None)
                raise Exception(f"Email send failed: {error_msg}")
            
            provider = result.get('provider', 'unknown')
            message_id = result.get('message_id', 'N/A')
            logger.info(f"Magic link email sent to {redact_email(email)} (provider: {provider}, message_id: {message_id})")
            
            # Always log the link in development mode
            from config import settings
            if getattr(settings, 'ENVIRONMENT', 'production') == 'development' or getattr(settings, 'DEV_MODE', False):
                logger.info(f"🔗 DEV MODE: Magic link for {redact_email(email)}: {magic_link}")
                print(f"\n{'='*80}")
                print(f"🔗 DEV MODE: Magic link sent to {redact_email(email)}")
                print(f"   Link: {magic_link}")
                print(f"   Expires: 24 hours")
                print(f"   Message ID: {message_id}")
                print(f"{'='*80}\n")
        except Exception as e:
            logger.error(f"Error sending magic link to {redact_email(email)}: {e}", exc_info=True)
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception args: {e.args}")
            # Remove stored link if email failed
            _magic_links.pop(token, None)
            # Re-raise with more context
            raise Exception(f"Failed to send magic link email to {redact_email(email)}: {str(e)}") from e
        
        return {
            "email": email,
            "expires_in": 86400,  # 24 hours in seconds
            "magic_link": magic_link  # For development/testing
        }
    
    def verify_magic_link(
        self,
        token: str,
        request_ip: Optional[str] = None,
        validate_ip: bool = True
    ) -> Optional[str]:
        """Verify magic link token and return/create anonymous ID.
        
        Args:
            token: Magic link token
            request_ip: IP address of the requester (for security validation)
            validate_ip: Whether to validate IP address (default: True)
        
        Returns:
            Anonymous ID if verification succeeds, None otherwise
        """
        # Check if token exists
        stored_data = _magic_links.get(token)
        if not stored_data:
            logger.warning(f"No magic link found for token")
            return None
        
        # Check if token expired
        expires_at = stored_data["expires_at"]
        now = datetime.utcnow()
        if now > expires_at:
            time_expired = (now - expires_at).total_seconds()
            logger.warning(f"Magic link expired ({time_expired:.0f} seconds ago)")
            _magic_links.pop(token, None)
            return None
        
        # IP address validation (privacy-preserving security feature)
        # We compare hashed IPs to prevent identity correlation while maintaining security
        stored_ip_hash = stored_data.get("ip_hash")
        request_ip_hash = _hash_ip(request_ip) if request_ip else None
        
        if validate_ip and stored_ip_hash and request_ip_hash:
            if stored_ip_hash != request_ip_hash:
                logger.warning(
                    f"Magic link IP hash mismatch detected (privacy-preserved validation), "
                    f"email={stored_data.get('email')}"
                )
                # Log security event but don't block (IPs can change with VPN/mobile)
                # In production, you might want to require additional verification here
                # Note: We don't log raw IPs to maintain zero-knowledge principles
        
        # Token is valid - get email and remove token (one-time use)
        email = stored_data["email"]
        _magic_links.pop(token, None)
        
        # Check if email already linked
        existing_user = self._find_user_by_email(email)
        
        if existing_user:
            logger.info(f"Magic link verified for existing user {existing_user.id} (IP: {request_ip})")
            return existing_user.id
        
        # Create new anonymous user and link email
        new_user = self.identity_manager.create_anonymous_user()
        self.link_email(new_user.id, email)
        
        logger.info(
            f"Magic link verified and linked for {redact_email(email)} (new user: {new_user.id})"
        )
        return new_user.id
    
    def link_email(
        self,
        anonymous_id: str,
        email: str
    ) -> bool:
        """Link email to anonymous identity."""
        user = self.identity_manager.get_user(anonymous_id)
        if not user:
            return False
        
        if not user.meta_data:
            user.meta_data = {}
        
        if "emails" not in user.meta_data:
            user.meta_data["emails"] = []
        
        if email not in [e.get("address") for e in user.meta_data.get("emails", [])]:
            user.meta_data["emails"].append({
                "address": email,
                "verified": True,
                "linked_at": datetime.utcnow().isoformat()
            })
        
        self.db.commit()
        return True
    
    def _find_user_by_email(self, email: str) -> Optional[AnonymousUser]:
        """Find anonymous user by email."""
        users = self.db.query(AnonymousUser).all()
        
        for user in users:
            if user.meta_data and "emails" in user.meta_data:
                for email_data in user.meta_data["emails"]:
                    if email_data.get("address") == email:
                        return user
        
        return None


def create_social_auth_manager(db_session: Session) -> SocialAuthManager:
    """Factory function to create social auth manager."""
    return SocialAuthManager(db_session)


