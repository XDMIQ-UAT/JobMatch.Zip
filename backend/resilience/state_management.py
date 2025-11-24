"""
State management and recovery system.
Implements checkpoint system for all AI decisions with rollback capabilities.
"""
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlalchemy import Column, String, DateTime, Text, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()

logger = logging.getLogger(__name__)


class CheckpointType(str, Enum):
    """Types of checkpoints."""
    MATCHING = "matching"
    ASSESSMENT = "assessment"
    ARTICULATION = "articulation"
    MODERATION = "moderation"
    SYSTEM = "system"


class StateCheckpoint(Base):
    """Database model for state checkpoints."""
    __tablename__ = "state_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    checkpoint_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(255), nullable=False, index=True)
    state_data = Column(JSON, nullable=False)
    meta_data = Column("metadata", JSON, nullable=True)  # Database column name stays 'metadata', but Python attribute is 'meta_data' to avoid SQLAlchemy reserved name conflict
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=True)  # Human reviewer ID if applicable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary."""
        return {
            "id": self.id,
            "checkpoint_type": self.checkpoint_type,
            "entity_id": self.entity_id,
            "state_data": self.state_data,
            "metadata": self.meta_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by
        }


class StateManager:
    """Manages state checkpoints and recovery."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_checkpoint(
        self,
        checkpoint_type: CheckpointType,
        entity_id: str,
        state_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> StateCheckpoint:
        """Create a new state checkpoint."""
        checkpoint = StateCheckpoint(
            checkpoint_type=checkpoint_type.value,
            entity_id=entity_id,
            state_data=state_data,
            metadata=metadata or {},
            created_by=created_by
        )
        self.db.add(checkpoint)
        self.db.commit()
        self.db.refresh(checkpoint)
        logger.info(f"Created checkpoint {checkpoint.id} for {checkpoint_type.value}:{entity_id}")
        return checkpoint
    
    def get_latest_checkpoint(
        self,
        checkpoint_type: CheckpointType,
        entity_id: str
    ) -> Optional[StateCheckpoint]:
        """Get the latest checkpoint for an entity."""
        checkpoint = self.db.query(StateCheckpoint).filter(
            StateCheckpoint.checkpoint_type == checkpoint_type.value,
            StateCheckpoint.entity_id == entity_id
        ).order_by(StateCheckpoint.created_at.desc()).first()
        return checkpoint
    
    def get_checkpoint_by_id(self, checkpoint_id: int) -> Optional[StateCheckpoint]:
        """Get checkpoint by ID."""
        return self.db.query(StateCheckpoint).filter(
            StateCheckpoint.id == checkpoint_id
        ).first()
    
    def list_checkpoints(
        self,
        checkpoint_type: Optional[CheckpointType] = None,
        entity_id: Optional[str] = None,
        limit: int = 100
    ) -> List[StateCheckpoint]:
        """List checkpoints with optional filters."""
        query = self.db.query(StateCheckpoint)
        
        if checkpoint_type:
            query = query.filter(StateCheckpoint.checkpoint_type == checkpoint_type.value)
        if entity_id:
            query = query.filter(StateCheckpoint.entity_id == entity_id)
        
        return query.order_by(StateCheckpoint.created_at.desc()).limit(limit).all()
    
    def restore_to_checkpoint(self, checkpoint_id: int) -> Dict[str, Any]:
        """
        Restore system to a previous checkpoint.
        Returns the restored state data.
        """
        checkpoint = self.get_checkpoint_by_id(checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        logger.info(f"Restoring to checkpoint {checkpoint_id} ({checkpoint.checkpoint_type}:{checkpoint.entity_id})")
        return checkpoint.state_data
    
    def delete_checkpoint(self, checkpoint_id: int) -> bool:
        """Delete a checkpoint (use with caution)."""
        checkpoint = self.get_checkpoint_by_id(checkpoint_id)
        if checkpoint:
            self.db.delete(checkpoint)
            self.db.commit()
            logger.warning(f"Deleted checkpoint {checkpoint_id}")
            return True
        return False
    
    def create_system_checkpoint(self, system_state: Dict[str, Any]) -> StateCheckpoint:
        """Create a system-wide checkpoint."""
        return self.create_checkpoint(
            checkpoint_type=CheckpointType.SYSTEM,
            entity_id="system",
            state_data=system_state,
            metadata={"system_checkpoint": True}
        )


def create_checkpoint_manager(db_session: Session) -> StateManager:
    """Factory function to create StateManager."""
    return StateManager(db_session)


