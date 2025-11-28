# Tools Module

Agent-callable tools provide capabilities that agents can use to interact with the environment, perform computations, or execute actions.

## Structure

- `base_tool.py`: Base class for all tools
- `__init__.py`: Module exports and protocols

## Creating a Custom Tool

```python
from src.tools.base_tool import BaseTool
from typing import Any

class MyTool(BaseTool):
    name = "my_tool"
    description = "A tool that does something useful"
    
    def execute(self, input_param: str, **kwargs: Any) -> Any:
        # Tool implementation
        return {"result": "..."}
```

## Tool Registration

Tools must be registered with agents before they can be used. The tool schema is automatically generated from the `execute` method signature.

## Tool Categories

- **API Tools**: Interact with external APIs
- **Database Tools**: Query and modify databases
- **File Tools**: Read and write files
- **Computation Tools**: Perform calculations or transformations
- **Communication Tools**: Send messages, emails, etc.

