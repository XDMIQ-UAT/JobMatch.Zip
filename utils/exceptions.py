"""
Custom Exceptions

Custom exception classes for the agentic AI system.
"""


class AgenticAIError(Exception):
    """Base exception for all agentic AI system errors."""
    pass


class AgentError(AgenticAIError):
    """Exception raised for agent-related errors."""
    pass


class ToolError(AgenticAIError):
    """Exception raised for tool execution errors."""
    pass


class WorkflowError(AgenticAIError):
    """Exception raised for workflow execution errors."""
    pass


class ModelError(AgenticAIError):
    """Exception raised for model-related errors."""
    pass


class ConfigurationError(AgenticAIError):
    """Exception raised for configuration errors."""
    pass


class AuthenticationError(AgenticAIError):
    """Exception raised for authentication errors."""
    pass


class ExecutionError(AgenticAIError):
    """Exception raised for execution errors."""
    pass

