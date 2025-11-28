"""
Production Environment Configuration
"""

import os
from typing import Dict, Any

# Load from environment variables (no defaults in production)
config: Dict[str, Any] = {
    "environment": "production",
    "debug": False,
    "api": {
        "host": os.getenv("API_HOST", "0.0.0.0"),
        "port": int(os.getenv("API_PORT", "8000")),
        "prefix": os.getenv("API_PREFIX", "/api/v1"),
    },
    "database": {
        "url": os.getenv("DATABASE_URL"),  # Required in production
        "pool_size": int(os.getenv("DATABASE_POOL_SIZE", "20")),
        "max_overflow": int(os.getenv("DATABASE_MAX_OVERFLOW", "40")),
    },
    "redis": {
        "host": os.getenv("REDIS_HOST"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "db": int(os.getenv("REDIS_DB", "0")),
    },
    "llm": {
        "provider": os.getenv("DEFAULT_LLM_PROVIDER", "openai"),
        "model": os.getenv("DEFAULT_MODEL", "gpt-4"),
        "api_key": os.getenv("OPENAI_API_KEY"),  # Required in production
    },
    "agents": {
        "max_concurrent": int(os.getenv("MAX_CONCURRENT_AGENTS", "50")),
        "timeout_seconds": int(os.getenv("AGENT_TIMEOUT_SECONDS", "600")),
        "memory_limit_mb": int(os.getenv("AGENT_MEMORY_LIMIT_MB", "1024")),
    },
    "security": {
        "secret_key": os.getenv("SECRET_KEY"),  # Required in production
        "jwt_secret": os.getenv("JWT_SECRET"),  # Required in production
        "jwt_algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
        "jwt_expiration_hours": int(os.getenv("JWT_EXPIRATION_HOURS", "24")),
    },
    "logging": {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "format": os.getenv("LOG_FORMAT", "json"),
        "file": os.getenv("LOG_FILE", "logs/prod.log"),
    },
    "monitoring": {
        "enable_metrics": os.getenv("ENABLE_METRICS", "true").lower() == "true",
        "metrics_port": int(os.getenv("METRICS_PORT", "9090")),
    },
}

