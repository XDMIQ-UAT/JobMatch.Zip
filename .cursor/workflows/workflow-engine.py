#!/usr/bin/env python3
"""
Stateless Workflow Engine
Executes workflows defined in stateless-workflows.yaml
No persistent state - each execution is independent
"""

import os
import sys
import yaml
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
WORKFLOWS_DIR = Path(__file__).parent
WORKFLOWS_FILE = WORKFLOWS_DIR / "stateless-workflows.yaml"
AGENTS_REGISTRY = Path(__file__).parent.parent / "agents" / "agents-registry.json"
AGENTS_DIR = Path(__file__).parent.parent / "agents"
LOG_DIR = Path(__file__).parent.parent.parent / "workflow-logs"

class StatelessWorkflowEngine:
    """Stateless workflow execution engine"""
    
    def __init__(self):
        self.workflows: Dict[str, Any] = {}
        self.agents_registry: Dict[str, Any] = {}
        self.load_workflows()
        self.load_agents_registry()
        self.ensure_log_dir()
    
    def ensure_log_dir(self):
        """Ensure log directory exists"""
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    def load_workflows(self):
        """Load workflow definitions from YAML"""
        if not WORKFLOWS_FILE.exists():
            logger.warning(f"Workflows file not found: {WORKFLOWS_FILE}")
            return
        
        try:
            with open(WORKFLOWS_FILE, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.workflows = data.get('workflows', {})
                logger.info(f"Loaded {len(self.workflows)} workflows")
        except Exception as e:
            logger.error(f"Failed to load workflows: {e}")
    
    def load_agents_registry(self):
        """Load agents registry"""
        if not AGENTS_REGISTRY.exists():
            logger.warning(f"Agents registry not found: {AGENTS_REGISTRY}")
            return
        
        try:
            with open(AGENTS_REGISTRY, 'r', encoding='utf-8') as f:
                self.agents_registry = json.load(f)
                logger.info(f"Loaded {len(self.agents_registry.get('agents', []))} agents")
        except Exception as e:
            logger.error(f"Failed to load agents registry: {e}")
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all available workflows"""
        workflows_list = []
        for workflow_id, workflow_def in self.workflows.items():
            workflows_list.append({
                "id": workflow_id,
                "name": workflow_def.get("name", workflow_id),
                "description": workflow_def.get("description", ""),
                "enabled": workflow_def.get("enabled", False),
                "version": workflow_def.get("version", "1.0.0")
            })
        return workflows_list
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow definition by ID"""
        return self.workflows.get(workflow_id)
    
    def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a workflow statelessly
        
        Args:
            workflow_id: ID of workflow to execute
            inputs: Input parameters for workflow
        
        Returns:
            Execution results
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        
        if not workflow.get("enabled", False):
            raise ValueError(f"Workflow '{workflow_id}' is disabled")
        
        logger.info(f"Executing workflow: {workflow_id}")
        
        # Initialize execution context (stateless - no persistence)
        context = {
            "workflow_id": workflow_id,
            "started_at": datetime.now().isoformat(),
            "inputs": inputs or {},
            "steps": {},
            "outputs": {}
        }
        
        # Execute steps sequentially
        steps = workflow.get("steps", [])
        for step in steps:
            step_id = step.get("id")
            logger.info(f"  Executing step: {step_id}")
            
            try:
                # Check condition if present
                condition = step.get("condition")
                if condition:
                    if not self.evaluate_condition(condition, context):
                        logger.info(f"    Condition not met, skipping step")
                        continue
                
                # Execute step
                step_result = self.execute_step(step, context)
                context["steps"][step_id] = step_result
                
            except Exception as e:
                logger.error(f"    Step {step_id} failed: {e}")
                context["steps"][step_id] = {
                    "status": "failed",
                    "error": str(e)
                }
                # Continue with next step (or break on critical failure)
        
        # Collect final outputs
        workflow_outputs = workflow.get("outputs", {})
        for output_key, output_template in workflow_outputs.items():
            try:
                context["outputs"][output_key] = self.resolve_template(output_template, context)
            except Exception as e:
                logger.warning(f"Failed to resolve output {output_key}: {e}")
        
        context["completed_at"] = datetime.now().isoformat()
        context["status"] = "completed"
        
        # Log execution (monitoring only, not for state)
        self.log_execution(context)
        
        return context
    
    def execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        agent_id = step.get("agent")
        command = step.get("command")
        
        # Get agent configuration
        agent_config = self.get_agent_config(agent_id)
        if not agent_config:
            raise ValueError(f"Agent '{agent_id}' not found")
        
        # Resolve inputs
        step_inputs = {}
        for input_key, input_template in step.get("inputs", {}).items():
            step_inputs[input_key] = self.resolve_template(input_template, context)
        
        # Execute agent command
        result = self.execute_agent_command(agent_id, command, step_inputs, agent_config)
        
        # Extract outputs
        step_outputs = {}
        for output_key, output_template in step.get("outputs", {}).items():
            step_outputs[output_key] = self.resolve_template(output_template, {
                **context,
                "result": result
            })
        
        return {
            "status": "success",
            "agent": agent_id,
            "command": command,
            "inputs": step_inputs,
            "outputs": step_outputs,
            "result": result
        }
    
    def get_agent_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent configuration from registry"""
        agents = self.agents_registry.get("agents", [])
        for agent in agents:
            if agent.get("id") == agent_id:
                # Load full agent config
                agent_file = AGENTS_DIR / agent.get("file")
                if agent_file.exists():
                    try:
                        with open(agent_file, 'r', encoding='utf-8') as f:
                            return json.load(f)
                    except Exception as e:
                        logger.warning(f"Failed to load agent config {agent_file}: {e}")
                return agent
        return None
    
    def execute_agent_command(self, agent_id: str, command: str, 
                              inputs: Dict[str, Any], 
                              agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent command"""
        commands = agent_config.get("commands", {})
        command_def = commands.get(command)
        
        if not command_def:
            raise ValueError(f"Command '{command}' not found in agent '{agent_id}'")
        
        script = command_def.get("script") if isinstance(command_def, dict) else command_def
        
        if not script:
            raise ValueError(f"No script defined for command '{command}'")
        
        # Execute script (simplified - in production would handle Python imports, etc.)
        logger.info(f"    Executing: {script}")
        
        # For now, return mock result
        # In production, would actually execute the script with inputs
        return {
            "command": command,
            "agent": agent_id,
            "executed": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def resolve_template(self, template: str, context: Dict[str, Any]) -> Any:
        """Resolve template variables (simplified)"""
        # Simple template resolution: {{ variable.path }}
        # In production, use Jinja2 or similar
        result = template
        if isinstance(template, str) and "{{" in template:
            # Extract variable path
            import re
            matches = re.findall(r'\{\{([^}]+)\}\}', template)
            for match in matches:
                var_path = match.strip()
                value = self.get_nested_value(context, var_path)
                result = result.replace(f"{{{{ {match} }}}}", str(value))
        return result
    
    def get_nested_value(self, obj: Any, path: str) -> Any:
        """Get nested value from object using dot notation"""
        parts = path.split(".")
        current = obj
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    current = current[int(part)]
                except (ValueError, IndexError):
                    return None
            else:
                return None
            if current is None:
                return None
        return current
    
    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition expression (simplified)"""
        # Simple condition evaluation
        # In production, use a proper expression evaluator
        try:
            # Replace variables with values
            resolved = self.resolve_template(condition, context)
            # Evaluate as Python expression (simplified - use safe eval in production)
            return eval(resolved, {"__builtins__": {}}, {})
        except:
            return False
    
    def log_execution(self, execution_context: Dict[str, Any]):
        """Log workflow execution (monitoring only)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = LOG_DIR / f"{execution_context['workflow_id']}-{timestamp}.json"
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(execution_context, f, indent=2)
            logger.info(f"Execution logged to: {log_file}")
        except Exception as e:
            logger.warning(f"Failed to log execution: {e}")


def main():
    """CLI interface for workflow engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Stateless Workflow Engine")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # List workflows
    list_parser = subparsers.add_parser("list", help="List all workflows")
    
    # Show workflow
    show_parser = subparsers.add_parser("show", help="Show workflow details")
    show_parser.add_argument("workflow_id", help="Workflow ID")
    
    # Execute workflow
    execute_parser = subparsers.add_parser("execute", help="Execute workflow")
    execute_parser.add_argument("workflow_id", help="Workflow ID")
    execute_parser.add_argument("--inputs", help="JSON inputs", default="{}")
    
    args = parser.parse_args()
    
    engine = StatelessWorkflowEngine()
    
    if args.command == "list":
        workflows = engine.list_workflows()
        print("\nAvailable Workflows:")
        print("=" * 60)
        for wf in workflows:
            status = "✓ Enabled" if wf["enabled"] else "✗ Disabled"
            print(f"{status} | {wf['id']:20} | {wf['name']}")
        print()
    
    elif args.command == "show":
        workflow = engine.get_workflow(args.workflow_id)
        if workflow:
            print(f"\nWorkflow: {args.workflow_id}")
            print("=" * 60)
            print(f"Name: {workflow.get('name')}")
            print(f"Description: {workflow.get('description')}")
            print(f"Enabled: {workflow.get('enabled')}")
            print(f"Version: {workflow.get('version')}")
            print(f"\nSteps: {len(workflow.get('steps', []))}")
            print()
        else:
            print(f"Workflow '{args.workflow_id}' not found")
    
    elif args.command == "execute":
        try:
            inputs = json.loads(args.inputs)
            result = engine.execute_workflow(args.workflow_id, inputs)
            print("\nExecution Result:")
            print("=" * 60)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

