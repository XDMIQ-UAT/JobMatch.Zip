"""
Base Tool Implementation

Provides a foundation for creating custom tools that agents can use.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import inspect


class BaseTool(ABC):
    """Base class for all tools in the system."""
    
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None
    ):
        self.name = name or self.__class__.__name__
        self.description = description or self.__doc__ or ""
        self._validate_tool()
    
    def _validate_tool(self) -> None:
        """Validate that the tool has required attributes."""
        if not self.name:
            raise ValueError("Tool must have a name")
        if not self.description:
            raise ValueError("Tool must have a description")
    
    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema for agent consumption."""
        sig = inspect.signature(self.execute)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_info = {
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                "required": param.default == inspect.Parameter.empty
            }
            
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
            
            parameters[param_name] = param_info
        
        return {
            "name": self.name,
            "description": self.description,
            "parameters": parameters
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"

