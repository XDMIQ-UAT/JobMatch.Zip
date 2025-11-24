"""
OAuth Provider Integrations.
Handles OAuth flows for Facebook, LinkedIn, Google, Microsoft, Apple.
"""
import logging
from typing import Dict, Any, Optional
import httpx

from backend.config import settings

logger = logging.getLogger(__name__)


class OAuthProviderManager:
    """Manages OAuth provider integrations."""
    
    def __init__(self):
        self.providers = {
            "facebook": {
                "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
                "user_info_url": "https://graph.facebook.com/me",
                "scopes": ["email", "public_profile"]
            },
            "linkedin": {
                "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
                "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
                "user_info_url": "https://api.linkedin.com/v2/userinfo",
                "scopes": ["openid", "profile", "email"]
            },
            "google": {
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scopes": ["openid", "profile", "email"]
            },
            "microsoft": {
                "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "user_info_url": "https://graph.microsoft.com/v1.0/me",
                "scopes": ["openid", "profile", "email"]
            },
            "apple": {
                "auth_url": "https://appleid.apple.com/auth/authorize",
                "token_url": "https://appleid.apple.com/auth/token",
                "user_info_url": None,  # Apple provides user info in token response
                "scopes": ["name", "email"]
            }
        }
    
    def get_authorization_url(
        self,
        provider: str,
        redirect_uri: str,
        state: Optional[str] = None
    ) -> str:
        """Get OAuth authorization URL for provider."""
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_config = self.providers[provider]
        
        # Get client ID from settings (would be configured per provider)
        client_id = getattr(settings, f"{provider.upper()}_CLIENT_ID", "")
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(provider_config["scopes"])
        }
        
        if state:
            params["state"] = state
        
        # Build URL
        url = f"{provider_config['auth_url']}?"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        
        return url
    
    async def exchange_code_for_token(
        self,
        provider: str,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_config = self.providers[provider]
        client_id = getattr(settings, f"{provider.upper()}_CLIENT_ID", "")
        client_secret = getattr(settings, f"{provider.upper()}_CLIENT_SECRET", "")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                provider_config["token_url"],
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed for {provider}: {response.text}")
                raise ValueError("Token exchange failed")
            
            return response.json()
    
    async def get_user_info(
        self,
        provider: str,
        access_token: str
    ) -> Dict[str, Any]:
        """Get user info from provider using access token."""
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_config = self.providers[provider]
        
        if not provider_config["user_info_url"]:
            # Apple provides user info in token response
            return {}
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(
                provider_config["user_info_url"],
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"User info fetch failed for {provider}: {response.text}")
                raise ValueError("Failed to fetch user info")
            
            return response.json()


def create_oauth_manager() -> OAuthProviderManager:
    """Factory function to create OAuth manager."""
    return OAuthProviderManager()


