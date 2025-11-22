from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from . import Base

class AnonymousProfile(Base):
    """
    Anonymous user profile.
    
    Invariants:
    - anonymous_id is cryptographically random, cannot reverse to identity
    - No PII fields allowed (no name, email, phone, address)
    - Only capability and preference data
    """
    __tablename__ = "anonymous_profiles"
    
    anonymous_id = Column(String(64), primary_key=True, index=True)
    
    # Capability data (NOT credentials)
    skills = Column(JSON, nullable=False, default=list)  # List of skill strings
    portfolio_url = Column(String(512), nullable=True)
    
    # Work preferences (XDMIQ-style)
    work_preference = Column(String(256), nullable=True)
    work_preference_reason = Column(String(2048), nullable=True)
    bio = Column(String(2048), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
    
    # Checkpoint metadata
    last_checkpoint_at = Column(DateTime(timezone=True), nullable=True)
    checkpoint_version = Column(String(32), nullable=True)
