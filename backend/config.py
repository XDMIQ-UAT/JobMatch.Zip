"""
Application configuration using Pydantic settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
from typing import List, Union
import json
import sys
import os


class Settings(BaseSettings):
    """Application settings."""
    # Accept extra env keys gracefully (so a shared .env can include unrelated entries)
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )
    
    # Database
    DATABASE_URL: str = "postgresql://jobfinder:jobfinder@localhost:5432/jobfinder"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    
    # OpenAI / OpenRouter
    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    
    # LLM Configuration
    LLM_PROVIDER: str = "openrouter"  # "openrouter", "openai", or "ollama"
    LLM_MODEL: str = "anthropic/claude-3.5-sonnet"  # Model to use (varies by provider)
    LLM_BASE_URL: str = "https://openrouter.ai/api/v1"  # Override for custom endpoints
    
    # Ollama (fallback for local development)
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.2"
    
    # Application
    # SECRET_KEY must be set via environment variable in production
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @model_validator(mode='after')
    def validate_secret_key(self):
        """Validate SECRET_KEY is not using default value in production."""
        # Only enforce in production or when ENVIRONMENT is not development
        if self.ENVIRONMENT.lower() not in ["development", "dev", "test"]:
            if self.SECRET_KEY == "change-me-in-production":
                print("\n" + "="*80, file=sys.stderr)
                print("CRITICAL SECURITY ERROR: SECRET_KEY is using default value!", file=sys.stderr)
                print("="*80, file=sys.stderr)
                print("\nSECRET_KEY must be set via environment variable.", file=sys.stderr)
                print("Generate a secure key with:", file=sys.stderr)
                print("  python -c 'import secrets; print(secrets.token_urlsafe(32))'\n", file=sys.stderr)
                print("Then set it in your .env file:", file=sys.stderr)
                print("  SECRET_KEY=<your-generated-key>\n", file=sys.stderr)
                print("="*80 + "\n", file=sys.stderr)
                sys.exit(1)
        return self
    
    # Development mode - log verification codes to console
    DEV_MODE: bool = True
    
    # CORS - Accept as string, parse in property
    _CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:8000,https://localhost:8443"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS_ORIGINS from string (comma-separated or JSON) to list."""
        cors_str = getattr(self, '_CORS_ORIGINS_STR', '')
        if not cors_str:
            return ["http://localhost:3000", "http://localhost:8000", "https://localhost:8443"]
        # Try JSON first
        if cors_str.strip().startswith('['):
            try:
                return json.loads(cors_str)
            except json.JSONDecodeError:
                pass
        # Fall back to comma-separated
        return [origin.strip() for origin in cors_str.split(',') if origin.strip()]
    
    # CDN
    CDN_URL: str = ""
    
    # OAuth Providers
    FACEBOOK_CLIENT_ID: str = ""
    FACEBOOK_CLIENT_SECRET: str = ""
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    GOOGLE_CLIENT_ID: str = ""  # Legacy name - also check GOOGLE_OAUTH_CLIENT_ID
    GOOGLE_CLIENT_SECRET: str = ""  # Legacy name - also check GOOGLE_OAUTH_CLIENT_SECRET
    GOOGLE_OAUTH_CLIENT_ID: str = ""  # Preferred name
    GOOGLE_OAUTH_CLIENT_SECRET: str = ""  # Preferred name
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    APPLE_CLIENT_ID: str = ""
    APPLE_CLIENT_SECRET: str = ""
    
    # SMS/VoIP (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@xdmiq.com"
    
    # Amazon SES
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-west-2"
    SES_REGION: str = "us-west-2"
    SES_FROM_EMAIL: str = ""
    EMAIL_PROVIDER_MODE: str = "smtp"  # "smtp" or "ses"
    
    # GCP CLI Backdoor (Documented Feature)
    GCP_CLI_ENABLED: bool = True
    GCP_ALLOWED_USERS: str = ""  # Comma-separated list
    GCP_ALLOWED_PROJECTS: str = ""  # Comma-separated list
    
    # Google Search Console API
    GOOGLE_SEARCH_CONSOLE_CREDENTIALS: str = ""  # JSON string of service account credentials
    GOOGLE_SEARCH_CONSOLE_SITE_URL: str = "https://jobmatch.zip"


settings = Settings()

