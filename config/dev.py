"""
Development Environment Configuration
"""

import os
from typing import Dict, Any

# Load from environment variables with defaults
config: Dict[str, Any] = {
    "environment": "development",
    "debug": True,
    "api": {
        "host": os.getenv("API_HOST", "0.0.0.0"),
        "port": int(os.getenv("API_PORT", "8000")),
        "prefix": os.getenv("API_PREFIX", "/api/v1"),
    },
    "database": {
        "url": os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/agentic_ai_dev"),
        "pool_size": int(os.getenv("DATABASE_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("DATABASE_MAX_OVERFLOW", "10")),
    },
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "db": int(os.getenv("REDIS_DB", "0")),
    },
    "llm": {
        "provider": os.getenv("DEFAULT_LLM_PROVIDER", "openai"),
        "model": os.getenv("DEFAULT_MODEL", "gpt-4"),
        "api_key": os.getenv("OPENAI_API_KEY", ""),
    },
    "agents": {
        "max_concurrent": int(os.getenv("MAX_CONCURRENT_AGENTS", "5")),
        "timeout_seconds": int(os.getenv("AGENT_TIMEOUT_SECONDS", "300")),
        "memory_limit_mb": int(os.getenv("AGENT_MEMORY_LIMIT_MB", "256")),
    },
    "logging": {
        "level": os.getenv("LOG_LEVEL", "DEBUG"),
        "format": os.getenv("LOG_FORMAT", "text"),
        "file": os.getenv("LOG_FILE", "logs/dev.log"),
    },
}

