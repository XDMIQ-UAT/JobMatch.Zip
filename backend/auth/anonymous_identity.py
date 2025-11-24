"""
Anonymous identity system.
Generates persistent anonymous IDs without revealing real identity.
Zero-knowledge architecture: platform cannot link anonymous IDs to real identities.
"""
import secrets
import hashlib
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from backend.database.models import AnonymousUser

logger = logging.getLogger(__name__)


class AnonymousIdentityManager:
    """Manages anonymous user identities."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def generate_anonymous_id(self) -> str:
        """
        Generate a cryptographically secure anonymous ID.
        Uses secrets module for secure random generation.
        """
        # Generate 32 bytes of random data
        random_bytes = secrets.token_bytes(32)
        # Create a hash for consistent length
        anonymous_id = hashlib.sha256(random_bytes).hexdigest()
        return anonymous_id
    
    def create_anonymous_user(
        self,
        metadata: Optional[dict] = None
    ) -> AnonymousUser:
        """
        Create a new anonymous user.
        Platform cannot link this ID to real identity.
        """
        anonymous_id = self.generate_anonymous_id()
        
        # Ensure uniqueness (extremely unlikely collision, but check anyway)
        while self.db.query(AnonymousUser).filter(
            AnonymousUser.id == anonymous_id
        ).first():
            anonymous_id = self.generate_anonymous_id()
        
        user = AnonymousUser(
            id=anonymous_id,
            metadata=metadata or {}
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Created anonymous user: {anonymous_id[:8]}...")
        return user
    
    def get_user(self, anonymous_id: str) -> Optional[AnonymousUser]:
        """Get anonymous user by ID."""
        return self.db.query(AnonymousUser).filter(
            AnonymousUser.id == anonymous_id
        ).first()
    
    def update_last_active(self, anonymous_id: str) -> bool:
        """Update user's last active timestamp."""
        user = self.get_user(anonymous_id)
        if user:
            user.last_active = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def create_multiple_personas(
        self,
        base_metadata: Optional[dict] = None,
        count: int = 1
    ) -> list[AnonymousUser]:
        """
        Allow users to create multiple anonymous personas for different contexts.
        Each persona is completely independent.
        """
        personas = []
        for _ in range(count):
            persona_metadata = (base_metadata or {}).copy()
            persona_metadata["persona_index"] = len(personas) + 1
            persona = self.create_anonymous_user(metadata=persona_metadata)
            personas.append(persona)
        
        return personas
    
    def validate_anonymous_id(self, anonymous_id: str) -> bool:
        """Validate that an anonymous ID is properly formatted."""
        # Should be 64 character hex string (SHA256)
        if len(anonymous_id) != 64:
            return False
        try:
            int(anonymous_id, 16)
            return True
        except ValueError:
            return False


def create_identity_manager(db_session: Session) -> AnonymousIdentityManager:
    """Factory function to create AnonymousIdentityManager."""
    return AnonymousIdentityManager(db_session)


