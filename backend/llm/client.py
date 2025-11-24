"""
LLM Client Abstraction Layer.
Supports OpenRouter, OpenAI, and Ollama with unified interface.
"""
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client supporting multiple providers."""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.model = settings.LLM_MODEL
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client based on provider."""
        try:
            if self.provider == "openrouter":
                if not settings.OPENROUTER_API_KEY:
                    logger.warning("OPENROUTER_API_KEY not set, falling back to Ollama")
                    self.provider = "ollama"
                    self._initialize_ollama()
                    return
                
                self._client = OpenAI(
                    base_url=settings.LLM_BASE_URL,
                    api_key=settings.OPENROUTER_API_KEY
                )
                logger.info(f"Initialized OpenRouter client with model: {self.model}")
            
            elif self.provider == "openai":
                if not settings.OPENAI_API_KEY:
                    logger.warning("OPENAI_API_KEY not set, falling back to Ollama")
                    self.provider = "ollama"
                    self._initialize_ollama()
                    return
                
                self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info(f"Initialized OpenAI client with model: {self.model}")
            
            elif self.provider == "ollama":
                self._initialize_ollama()
            
            else:
                raise ValueError(f"Unknown LLM provider: {self.provider}")
        
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} client: {e}")
            logger.info("Falling back to Ollama")
            self.provider = "ollama"
            self._initialize_ollama()
    
    def _initialize_ollama(self):
        """Initialize Ollama client."""
        try:
            from ollama import Client
            self._client = Client(host=settings.OLLAMA_BASE_URL)
            self.model = settings.OLLAMA_MODEL
            logger.info(f"Initialized Ollama client with model: {self.model}")
        except ImportError:
            logger.error("ollama package not installed. Install with: pip install ollama")
            raise
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Generated text response
        """
        if self.provider == "ollama":
            return self._chat_ollama(messages, temperature, **kwargs)
        else:
            return self._chat_openai_compatible(messages, temperature, max_tokens, **kwargs)
    
    def _chat_openai_compatible(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> str:
        """Chat using OpenAI-compatible API (OpenAI, OpenRouter)."""
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            # Add OpenRouter-specific headers
            if self.provider == "openrouter":
                extra_headers = kwargs.pop("extra_headers", {})
                extra_headers.update({
                    "HTTP-Referer": "https://jobmatch.zip",  # Optional, for rankings
                    "X-Title": "JobMatch AI",  # Optional, for rankings
                })
                params["extra_headers"] = extra_headers
            
            params.update(kwargs)
            
            response = self._client.chat.completions.create(**params)
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"LLM API error ({self.provider}): {e}")
            raise
    
    def _chat_ollama(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        **kwargs
    ) -> str:
        """Chat using Ollama API."""
        try:
            response = self._client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    **kwargs
                }
            )
            return response["message"]["content"]
        
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if LLM service is available."""
        try:
            test_messages = [{"role": "user", "content": "test"}]
            self.chat(test_messages, max_tokens=5)
            return True
        except Exception as e:
            logger.error(f"LLM availability check failed: {e}")
            return False


# Global client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
