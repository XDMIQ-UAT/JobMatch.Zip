# Agents Module

This module defines agent behaviors and types. Agents are autonomous entities that can perceive their environment, make decisions, and take actions to achieve goals.

## Structure

- `base_agent.py`: Base class for all agents
- `__init__.py`: Module exports and protocols

## Creating a Custom Agent

```python
from src.agents.base_agent import BaseAgent
from typing import Dict, Any

class MyAgent(BaseAgent):
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        # Extract relevant information from environment
        return {"observation": "..."}
    
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        # Make decision based on perception
        return {"action": "..."}
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        # Execute action
        return {"result": "..."}
```

## Agent Types

- **Task-Oriented Agents**: Focus on completing specific tasks
- **Conversational Agents**: Engage in dialogue with users
- **Tool-Using Agents**: Utilize external tools to accomplish goals
- **Multi-Agent Systems**: Coordinate with other agents

