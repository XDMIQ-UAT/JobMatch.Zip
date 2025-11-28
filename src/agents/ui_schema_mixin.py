"""
UI Schema Mixin for Agents

Enables agents to generate declarative UI schemas instead of HTML.
"""

from typing import Dict, Any, List, Optional
from src.schemas.ui_schema import (
    UISchemaBuilder,
    Component,
    ComponentType,
    Layout,
    Action
)


class UISchemaMixin:
    """Mixin that adds UI schema generation capabilities to agents."""
    
    def get_ui_schema(self, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate UI schema for this agent.
        
        Override this method in subclasses to customize UI.
        """
        state = state or self.get_state()
        
        builder = UISchemaBuilder(
            agent_id=self.agent_id,
            agent_name=self.name
        )
        
        # Default layout
        builder.set_layout({
            "type": "stack",
            "gap": 16
        })
        
        # Add components based on agent state
        self._build_ui_components(builder, state)
        
        # Add actions
        self._build_ui_actions(builder)
        
        # Set state
        builder.setState(state)
        
        return builder.build()
    
    def _build_ui_components(
        self,
        builder: UISchemaBuilder,
        state: Dict[str, Any]
    ) -> None:
        """Build UI components. Override in subclasses."""
        # Default: show agent status
        builder.addComponent({
            "id": "status",
            "type": "text",
            "props": {
                "content": f"Agent: {self.name}",
                "fontSize": "18px",
                "fontWeight": "bold"
            }
        })
    
    def _build_ui_actions(self, builder: UISchemaBuilder) -> None:
        """Build UI actions. Override in subclasses."""
        pass
    
    def get_ui_updates(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get incremental UI updates (for real-time updates).
        Returns only changed components.
        """
        return {
            "agentId": self.agent_id,
            "state": state,
            "timestamp": self.created_at.isoformat()
        }

