"""
OAuth service manager for handling multiple providers.
"""

from typing import Dict, Optional, Type
from ..models import OAuthProvider
from ..core import config
from ..core.exceptions import ValidationError
from .oauth_providers import (
    BaseOAuthProvider,
    OAuthConfig,
    GoogleOAuthProvider,
    MicrosoftOAuthProvider,
    AppleOAuthProvider,
)
from .oauth_state_manager import OAuthStateManager


class OAuthServiceManager:
    """Manages OAuth providers and their configurations."""

    def __init__(self):
        """Initialize OAuth service manager."""
        self.state_manager = OAuthStateManager()
        self._providers: Dict[str, BaseOAuthProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all configured OAuth providers."""
        # Google OAuth
        if config.google_client_id and config.google_client_secret:
            google_config = OAuthConfig(
                client_id=config.google_client_id,
                client_secret=config.google_client_secret,
                redirect_uri=self._get_redirect_uri("google"),
                scope=["openid", "email", "profile"],
                authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
                token_url="https://oauth2.googleapis.com/token",
                user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
            )
            self._providers["google"] = GoogleOAuthProvider(google_config)

        # Microsoft OAuth
        if config.microsoft_client_id and config.microsoft_client_secret:
            microsoft_config = OAuthConfig(
                client_id=config.microsoft_client_id,
                client_secret=config.microsoft_client_secret,
                redirect_uri=self._get_redirect_uri("microsoft"),
                scope=["openid", "email", "profile", "User.Read"],
                authorization_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
                user_info_url="https://graph.microsoft.com/v1.0/me",
            )
            self._providers["microsoft"] = MicrosoftOAuthProvider(microsoft_config)

        # Apple OAuth
        if config.apple_client_id and config.apple_client_secret:
            apple_config = OAuthConfig(
                client_id=config.apple_client_id,
                client_secret=config.apple_client_secret,
                redirect_uri=self._get_redirect_uri("apple"),
                scope=["email", "name"],
                authorization_url="https://appleid.apple.com/auth/authorize",
                token_url="https://appleid.apple.com/auth/token",
                user_info_url="",  # Apple doesn't have a separate user info endpoint
            )
            self._providers["apple"] = AppleOAuthProvider(apple_config)

    def _get_redirect_uri(self, provider: str) -> str:
        """Get redirect URI for a provider."""
        base_url = getattr(config, "base_url", f"http://{config.host}:{config.port}")
        return f"{base_url}/api/oauth/{provider}/callback"

    def get_available_providers(self) -> list[str]:
        """Get list of available OAuth providers."""
        return list(self._providers.keys())

    def get_provider(self, provider_name: str) -> BaseOAuthProvider:
        """Get OAuth provider by name."""
        if provider_name not in self._providers:
            raise ValidationError(f"OAuth provider '{provider_name}' is not configured")
        return self._providers[provider_name]

    def is_provider_available(self, provider_name: str) -> bool:
        """Check if a provider is available and configured."""
        return provider_name in self._providers

    def generate_authorization_url(
        self, provider_name: str, metadata: Dict = None
    ) -> tuple[str, str]:
        """Generate authorization URL for a provider."""
        if not self.is_provider_available(provider_name):
            raise ValidationError(f"OAuth provider '{provider_name}' is not available")

        provider = self.get_provider(provider_name)
        redirect_uri = self._get_redirect_uri(provider_name)

        # Create state token
        state_token = self.state_manager.create_state(
            provider=provider_name, redirect_uri=redirect_uri, metadata=metadata or {}
        )

        # Generate authorization URL
        auth_url = provider.generate_authorization_url(state_token)

        return auth_url, state_token

    async def handle_callback(
        self, provider_name: str, code: str, state: str
    ) -> "OAuthUserProfile":
        """Handle OAuth callback and return user profile."""
        if not self.is_provider_available(provider_name):
            raise ValidationError(f"OAuth provider '{provider_name}' is not available")

        # Validate state token
        oauth_state = self.state_manager.validate_and_consume_state(
            state, provider_name
        )
        if not oauth_state:
            raise ValidationError("Invalid or expired OAuth state")

        provider = self.get_provider(provider_name)

        # Exchange code for token
        token_response = await provider.exchange_code_for_token(code, state)

        # Get user profile
        user_profile = await provider.get_user_profile(token_response.access_token)

        return user_profile

    async def cleanup_expired_states(self) -> int:
        """Clean up expired OAuth states."""
        return self.state_manager.cleanup_expired_states()

    async def close_all_providers(self):
        """Close all provider HTTP clients."""
        for provider in self._providers.values():
            await provider.close()


# Global OAuth service manager instance
oauth_manager = OAuthServiceManager()
