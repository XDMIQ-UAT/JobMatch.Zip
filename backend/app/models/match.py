from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from . import Base

class Match(Base):
    """
    Job match between anonymous profile and opportunity.
    
    Invariants:
    - Only human-approved matches shown to users
    - Match score based on capabilities, not credentials
    - No identity revealed until user chooses
    """
    __tablename__ = "matches"
    
    id = Column(String(64), primary_key=True, index=True)
    anonymous_id = Column(String(64), nullable=False, index=True)
    job_id = Column(String(64), nullable=False, index=True)
    
    # Match metadata
    match_score = Column(Integer, nullable=False)  # 0-100
    matching_capabilities = Column(JSON, nullable=False)  # List of matching skills
    required_capabilities = Column(JSON, nullable=False)  # All required skills
    
    # Job details (cached from jobs table)
    title = Column(String(256), nullable=False)
    company = Column(String(256), nullable=False)
    location = Column(String(256), nullable=False)
    description = Column(String(4096), nullable=False)
    is_remote = Column(Boolean, nullable=False, default=False)
    
    # Review workflow (human-in-the-loop)
    is_approved = Column(Boolean, nullable=False, default=False)
    approved_by = Column(String(64), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # AI-generated match (queued for approval)
    ai_rationale = Column(String(4096), nullable=True)
    ai_confidence = Column(String(16), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
