"""
API endpoints for agent UI schemas and real-time updates
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime

router = APIRouter(prefix="/api/agents", tags=["agent-ui"])

# Store agent instances (in production, use proper dependency injection)
agent_registry: Dict[str, Any] = {}


@router.get("/{agent_id}/ui-schema")
async def get_ui_schema(agent_id: str) -> Dict[str, Any]:
    """Get UI schema for an agent."""
    agent = agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    if not hasattr(agent, 'get_ui_schema'):
        raise HTTPException(
            status_code=400,
            detail=f"Agent {agent_id} does not support UI schema"
        )
    
    state = agent.get_state()
    schema = agent.get_ui_schema(state)
    return schema


@router.get("/{agent_id}/state")
async def get_agent_state(agent_id: str) -> Dict[str, Any]:
    """Get current state of an agent."""
    agent = agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return {
        "agentId": agent_id,
        "state": agent.get_state(),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/{agent_id}/state/stream")
async def stream_agent_state(agent_id: str):
    """Stream agent state updates via Server-Sent Events."""
    agent = agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    async def event_generator():
        last_state = None
        
        while True:
            current_state = agent.get_state()
            
            # Only send if state changed
            if current_state != last_state:
                update = {
                    "agentId": agent_id,
                    "state": current_state,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                yield f"data: {json.dumps(update)}\n\n"
                last_state = current_state
            
            await asyncio.sleep(1)  # Check every second
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in nginx
        }
    )


@router.post("/{agent_id}/action/{action_id}")
async def execute_agent_action(
    agent_id: str,
    action_id: str,
    payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute an action on an agent."""
    agent = agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    # Execute action (implementation depends on agent)
    try:
        result = await agent.execute_action(action_id, payload or {})
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}/ui-schema")
async def get_workflow_ui_schema(workflow_id: str) -> Dict[str, Any]:
    """Get combined UI schema for all agents in a workflow."""
    # This would fetch the workflow and combine schemas from all agents
    # Implementation depends on your workflow structure
    return {
        "workflowId": workflow_id,
        "components": [],
        "layout": {"type": "grid", "columns": 2},
        "agents": []
    }


@router.post("/register")
async def register_agent_endpoint(agent_id: str) -> Dict[str, Any]:
    """
    Register a test agent for SSE testing.
    In production, agents should be registered at startup.
    """
    # Simple agent class that doesn't require imports
    class SimpleAgent:
        def __init__(self, agent_id: str, name: str):
            self.agent_id = agent_id
            self.name = name
            self.state: Dict[str, Any] = {}
        
        def get_state(self) -> Dict[str, Any]:
            return self.state.copy()
        
        def update_state(self, updates: Dict[str, Any]) -> None:
            self.state.update(updates)
    
    # Create and register test agent
    test_agent = SimpleAgent(agent_id=agent_id, name=f"Test Agent {agent_id}")
    test_agent.update_state({
        "count": 0,
        "status": "ready",
        "created_at": datetime.utcnow().isoformat()
    })
    
    register_agent(agent_id, test_agent)
    
    return {
        "success": True,
        "agentId": agent_id,
        "message": f"Agent {agent_id} registered successfully",
        "state": test_agent.get_state()
    }


def register_agent(agent_id: str, agent: Any):
    """Register an agent instance."""
    agent_registry[agent_id] = agent


def unregister_agent(agent_id: str):
    """Unregister an agent instance."""
    if agent_id in agent_registry:
        del agent_registry[agent_id]

