"""
Base Agent Implementation

Provides a foundation for creating custom agents with standard lifecycle methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None
    ):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or self.__class__.__name__
        self.description = description or ""
        self.capabilities = capabilities or []
        self.created_at = datetime.utcnow()
        self.state: Dict[str, Any] = {}
    
    @abstractmethod
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Perceive the current environment state."""
        pass
    
    @abstractmethod
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Make a decision based on perception."""
        pass
    
    @abstractmethod
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action based on decision."""
        pass
    
    def run(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the full agent lifecycle: perceive -> decide -> act."""
        perception = self.perceive(environment)
        decision = self.decide(perception)
        result = self.act(decision)
        return result
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current agent state."""
        return self.state.copy()
    
    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update the agent state."""
        self.state.update(updates)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id}, name={self.name})>"

