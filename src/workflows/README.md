# Workflows Module

Predefined sequences or chains of agent interactions. Workflows orchestrate multiple agents to accomplish complex tasks that require coordination.

## Structure

- `base_workflow.py`: Base class for all workflows
- `__init__.py`: Module exports and protocols

## Creating a Custom Workflow

```python
from src.workflows.base_workflow import BaseWorkflow
from typing import Dict, Any

class MyWorkflow(BaseWorkflow):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Define workflow steps
        step1_result = self.execute_step_1(context)
        step2_result = self.execute_step_2(step1_result)
        return {"final_result": step2_result}
```

## Workflow Patterns

- **Sequential**: Steps execute one after another
- **Parallel**: Steps execute simultaneously
- **Conditional**: Steps execute based on conditions
- **Loop**: Steps repeat until condition met

## Error Handling

Workflows should include error handling and recovery mechanisms to handle failures gracefully.

