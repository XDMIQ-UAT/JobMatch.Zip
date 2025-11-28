"""
Tools Module

Agent-callable tools provide capabilities that agents can use to interact with
the environment, perform computations, or execute actions.

Tools are registered with agents and can be invoked dynamically during agent execution.
"""

from typing import Protocol, Any, Dict, List, Optional

class Tool(Protocol):
    """Base protocol for all tools."""
    
    name: str
    description: str
    
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with given parameters."""
        ...

# Export all tools
from src.tools.base_tool import BaseTool
from src.tools.web_scraper import WebScraperTool
from src.tools.file_reader import FileReaderTool
from src.tools.vector_db_storage import VectorDBStorageTool

__all__ = [
    "Tool",
    "BaseTool",
    "WebScraperTool",
    "FileReaderTool",
    "VectorDBStorageTool",
]

