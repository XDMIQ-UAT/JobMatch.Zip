#!/usr/bin/env python3
"""
Cloud Run Agent Service
HTTP API for executing stateless workflows and agent commands
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import workflow engine
# Try multiple paths for workflow engine
workflow_engine_paths = [
    Path(__file__).parent / "workflows" / "workflow-engine.py",  # Cloud Run (copied)
    Path(__file__).parent.parent / ".cursor" / "workflows" / "workflow-engine.py",  # Local dev
]

workflow_engine_path = None
for path in workflow_engine_paths:
    if path.exists():
        workflow_engine_path = path
        break

if workflow_engine_path:
    import importlib.util
    spec = importlib.util.spec_from_file_location("workflow_engine", workflow_engine_path)
    workflow_engine = importlib.util.module_from_spec(spec)
    # Add parent directory to sys.path for imports
    sys.path.insert(0, str(workflow_engine_path.parent))
    spec.loader.exec_module(workflow_engine)
    StatelessWorkflowEngine = workflow_engine.StatelessWorkflowEngine
    logger.info(f"Loaded workflow engine from {workflow_engine_path}")
else:
    # Mock for development/testing
    logger.warning("Workflow engine not found, using mock")
    class StatelessWorkflowEngine:
        def __init__(self):
            self.workflows = {}
        def list_workflows(self):
            return []
        def get_workflow(self, workflow_id):
            return None
        def execute_workflow(self, workflow_id, inputs=None):
            return {"status": "mock", "workflow_id": workflow_id, "message": "Workflow engine not available"}
        def get_agent_config(self, agent_id):
            return None
        def execute_agent_command(self, agent_id, command, inputs, agent_config):
            return {"status": "mock", "agent_id": agent_id, "command": command}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agent Service API",
    description="Cloud Run service for executing stateless workflows and agent commands",
    version="1.0.0"
)

# Initialize workflow engine
try:
    engine = StatelessWorkflowEngine()
    logger.info("Workflow engine initialized")
except Exception as e:
    logger.error(f"Failed to initialize workflow engine: {e}")
    engine = None

# Request/Response models
class WorkflowExecuteRequest(BaseModel):
    workflow_id: str = Field(..., description="ID of workflow to execute")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")
    
class AgentCommandRequest(BaseModel):
    agent_id: str = Field(..., description="ID of agent")
    command: str = Field(..., description="Command to execute")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    engine_available: bool

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Agent Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "workflows": "/workflows",
            "execute_workflow": "/workflows/execute",
            "agent_command": "/agents/command"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        engine_available=engine is not None
    )

@app.get("/workflows")
async def list_workflows():
    """List all available workflows"""
    if not engine:
        raise HTTPException(status_code=503, detail="Workflow engine not available")
    
    try:
        workflows = engine.list_workflows()
        return {
            "workflows": workflows,
            "count": len(workflows)
        }
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow definition"""
    if not engine:
        raise HTTPException(status_code=503, detail="Workflow engine not available")
    
    try:
        workflow = engine.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
        return workflow
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflows/execute")
async def execute_workflow(request: WorkflowExecuteRequest):
    """Execute a workflow"""
    if not engine:
        raise HTTPException(status_code=503, detail="Workflow engine not available")
    
    try:
        logger.info(f"Executing workflow: {request.workflow_id}")
        result = engine.execute_workflow(
            workflow_id=request.workflow_id,
            inputs=request.inputs or {}
        )
        return {
            "status": "success",
            "workflow_id": request.workflow_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        logger.error(f"Workflow execution error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/command")
async def execute_agent_command(request: AgentCommandRequest):
    """Execute an agent command"""
    if not engine:
        raise HTTPException(status_code=503, detail="Workflow engine not available")
    
    try:
        logger.info(f"Executing agent command: {request.agent_id}.{request.command}")
        
        # Get agent config
        agent_config = engine.get_agent_config(request.agent_id)
        if not agent_config:
            raise HTTPException(status_code=404, detail=f"Agent '{request.agent_id}' not found")
        
        # Execute command
        result = engine.execute_agent_command(
            agent_id=request.agent_id,
            command=request.command,
            inputs=request.inputs or {},
            agent_config=agent_config
        )
        
        return {
            "status": "success",
            "agent_id": request.agent_id,
            "command": request.command,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        logger.error(f"Agent command error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

