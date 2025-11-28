"""
Workflows Module

Predefined sequences or chains of agent interactions. Workflows orchestrate
multiple agents to accomplish complex tasks that require coordination.

Workflows define:
- Agent execution order
- Data flow between agents
- Error handling and recovery
- Conditional branching
"""

from typing import Protocol, Any, Dict, List

class Workflow(Protocol):
    """Base protocol for all workflows."""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow with given context."""
        ...

# Export all workflows
from src.workflows.base_workflow import BaseWorkflow
from src.workflows.job_matching_workflow import JobMatchingWorkflow

__all__ = [
    "Workflow",
    "BaseWorkflow",
    "JobMatchingWorkflow",
]

