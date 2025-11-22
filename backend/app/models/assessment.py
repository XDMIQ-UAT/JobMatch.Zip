from sqlalchemy import Column, String, DateTime, JSON, Boolean, Enum
from sqlalchemy.sql import func
import enum
from . import Base

class AssessmentStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    PENDING_REVIEW = "pending_review"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"

class Assessment(Base):
    """
    Capability assessment submission.
    
    Invariants:
    - Linked to anonymous_id, not identity
    - Human-in-the-loop: status tracks review state
    - Checkpoint before status changes
    """
    __tablename__ = "assessments"
    
    id = Column(String(64), primary_key=True, index=True)
    anonymous_id = Column(String(64), nullable=False, index=True)
    
    # Assessment data
    skills = Column(JSON, nullable=False)
    portfolio_url = Column(String(512), nullable=True)
    work_preference = Column(String(256), nullable=False)
    work_preference_reason = Column(String(2048), nullable=True)
    
    # Review workflow
    status = Column(Enum(AssessmentStatus), nullable=False, default=AssessmentStatus.SUBMITTED)
    reviewed_by = Column(String(64), nullable=True)  # Human reviewer ID (anonymous)
    review_notes = Column(String(4096), nullable=True)
    
    # AI analysis (queued for human review)
    ai_analysis = Column(JSON, nullable=True)
    ai_confidence = Column(String(16), nullable=True)  # low/medium/high
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Checkpoint metadata
    checkpoint_before_review = Column(String(64), nullable=True)
