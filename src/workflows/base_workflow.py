"""
Base Workflow Implementation

Provides a foundation for creating custom workflows that orchestrate agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid


class BaseWorkflow(ABC):
    """Base class for all workflows in the system."""
    
    def __init__(
        self,
        workflow_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        steps: Optional[List[Dict[str, Any]]] = None
    ):
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.name = name or self.__class__.__name__
        self.description = description or ""
        self.steps = steps or []
        self.created_at = datetime.utcnow()
        self.context: Dict[str, Any] = {}
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow with given context."""
        pass
    
    def add_step(self, step: Dict[str, Any]) -> None:
        """Add a step to the workflow."""
        self.steps.append(step)
    
    def get_steps(self) -> List[Dict[str, Any]]:
        """Get all workflow steps."""
        return self.steps.copy()
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.workflow_id}, name={self.name})>"

