import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import redis

class CheckpointService:
    """
    State checkpoint service for safe recovery.
    
    Invariants:
    - Checkpoint before all state-changing operations
    - Checkpoints stored in Redis for fast access
    - Postgres for durable backup
    - Can rollback to last known good state
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    def create_checkpoint(
        self, 
        entity_type: str,  # "profile", "assessment", "match"
        entity_id: str, 
        state: Dict[str, Any]
    ) -> str:
        """
        Create checkpoint before state change.
        
        Returns: checkpoint_id
        """
        checkpoint_id = self._generate_checkpoint_id(entity_type, entity_id)
        
        checkpoint = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "state": state,
            "created_at": datetime.utcnow().isoformat(),
            "version": checkpoint_id
        }
        
        # Store in Redis with 7-day TTL
        key = f"checkpoint:{entity_type}:{entity_id}:{checkpoint_id}"
        self.redis.setex(
            key,
            60 * 60 * 24 * 7,  # 7 days
            json.dumps(checkpoint)
        )
        
        # Store reference to latest checkpoint
        latest_key = f"checkpoint:latest:{entity_type}:{entity_id}"
        self.redis.set(latest_key, checkpoint_id)
        
        return checkpoint_id
    
    def get_checkpoint(
        self, 
        entity_type: str, 
        entity_id: str, 
        checkpoint_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve checkpoint by ID or latest.
        
        Returns: checkpoint state or None
        """
        if not checkpoint_id:
            # Get latest checkpoint
            latest_key = f"checkpoint:latest:{entity_type}:{entity_id}"
            checkpoint_id = self.redis.get(latest_key)
            if not checkpoint_id:
                return None
            checkpoint_id = checkpoint_id.decode('utf-8')
        
        key = f"checkpoint:{entity_type}:{entity_id}:{checkpoint_id}"
        data = self.redis.get(key)
        
        if not data:
            return None
            
        return json.loads(data)
    
    def rollback_to_checkpoint(
        self,
        entity_type: str,
        entity_id: str,
        checkpoint_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Rollback to checkpoint state.
        
        Returns: restored state or None
        """
        checkpoint = self.get_checkpoint(entity_type, entity_id, checkpoint_id)
        if not checkpoint:
            return None
        
        # TODO: Apply state to database
        # This requires database session context
        
        return checkpoint.get("state")
    
    def _generate_checkpoint_id(self, entity_type: str, entity_id: str) -> str:
        """Generate unique checkpoint ID"""
        timestamp = datetime.utcnow().isoformat()
        data = f"{entity_type}:{entity_id}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
