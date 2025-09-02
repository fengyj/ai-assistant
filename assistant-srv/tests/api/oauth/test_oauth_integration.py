"""
OAuth system integration tests.
"""

import shutil
import tempfile
from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from assistant.core.exceptions import ValidationError
from assistant.services.oauth_providers import GoogleOAuthProvider, MicrosoftOAuthProvider, OAuthConfig
from assistant.services.oauth_service import OAuthServiceManager
from assistant.services.oauth_state_manager import OAuthStateManager


class TestOAuthProviders:
    """Test OAuth provider implementations."""

    @pytest.fixture()
    def google_config(self) -> OAuthConfig:
        """Create Google OAuth config for testing."""
        return OAuthConfig(
            client_id="test_google_client_id",
            client_secret="test_google_client_secret",
            redirect_uri="http://localhost:8000/api/oauth/google/callback",
            scope=["openid", "email", "profile"],
            authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
        )

    @pytest.fixture()
    def google_provider(self, google_config: OAuthConfig) -> GoogleOAuthProvider:
        """Create Google OAuth provider for testing."""
        return GoogleOAuthProvider(google_config)

    def test_google_provider_initialization(self, google_provider: GoogleOAuthProvider) -> None:
        """Test Google provider initialization."""
        assert google_provider.provider_name == "google"
        assert google_provider.config.client_id == "test_google_client_id"

    def test_authorization_url_generation(self, google_provider: GoogleOAuthProvider) -> None:
        """Test authorization URL generation."""
        state = "test_state_token"
        auth_url = google_provider.generate_authorization_url(state)

        assert "accounts.google.com" in auth_url
        assert "client_id=test_google_client_id" in auth_url
        assert "state=test_state_token" in auth_url
        assert "scope=openid+email+profile" in auth_url

    @pytest.mark.asyncio
    async def test_token_exchange_success(self, google_provider: GoogleOAuthProvider) -> None:
        """Test successful token exchange."""
        mock_response_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

        with patch.object(google_provider.http_client, "post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response

            token_response = await google_provider.exchange_code_for_token("test_code", "test_state")

            assert token_response.access_token == "test_access_token"
            assert token_response.refresh_token == "test_refresh_token"
            assert token_response.expires_in == 3600

    @pytest.mark.asyncio
    async def test_user_profile_retrieval(self, google_provider: GoogleOAuthProvider) -> None:
        """Test user profile retrieval."""
        mock_user_data = {
            "sub": "google_user_123",
            "email": "test@gmail.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://example.com/avatar.jpg",
            "email_verified": True,
        }

        with patch.object(google_provider.http_client, "get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_user_data
            mock_get.return_value = mock_response

            user_profile = await google_provider.get_user_profile("test_token")

            assert user_profile.provider_id == "google_user_123"
            assert user_profile.email == "test@gmail.com"
            assert user_profile.name == "Test User"
            assert user_profile.verified_email is True


class TestOAuthStateManager:
    """Test OAuth state management."""

    @pytest.fixture()
    def temp_dir(self) -> Iterator[str]:
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture()
    def state_manager(self, temp_dir: str) -> OAuthStateManager:
        """Create state manager for testing."""
        return OAuthStateManager(temp_dir)

    def test_state_creation(self, state_manager: OAuthStateManager) -> None:
        """Test OAuth state creation."""
        state_token = state_manager.create_state(
            provider="google",
            redirect_uri="http://localhost:8000/callback",
            metadata={"test": True},
        )

        assert len(state_token) > 20  # Should be a long random token
        assert state_token in state_manager._states_cache

    def test_state_validation_and_consumption(self, state_manager: OAuthStateManager) -> None:
        """Test state validation and consumption."""
        state_token = state_manager.create_state(provider="google", redirect_uri="http://localhost:8000/callback")

        # First validation should succeed
        oauth_state = state_manager.validate_and_consume_state(state_token, "google")
        assert oauth_state is not None
        assert oauth_state.provider == "google"

        # Second validation should fail (state consumed)
        oauth_state = state_manager.validate_and_consume_state(state_token, "google")
        assert oauth_state is None

    def test_state_provider_mismatch(self, state_manager: OAuthStateManager) -> None:
        """Test state validation with wrong provider."""
        state_token = state_manager.create_state(provider="google", redirect_uri="http://localhost:8000/callback")

        # Validation with wrong provider should fail
        oauth_state = state_manager.validate_and_consume_state(state_token, "microsoft")
        assert oauth_state is None

    def test_invalid_state_token(self, state_manager: OAuthStateManager) -> None:
        """Test validation with invalid state token."""
        oauth_state = state_manager.validate_and_consume_state("invalid_token", "google")
        assert oauth_state is None


class TestOAuthServiceManager:
    """Test OAuth service manager."""

    @pytest.fixture()
    def mock_config(self) -> Iterator[MagicMock | AsyncMock]:
        """Mock configuration with OAuth credentials."""
        with patch("assistant.services.oauth_service.config") as mock_config:
            mock_config.google_client_id = "test_google_id"
            mock_config.google_client_secret = "test_google_secret"
            mock_config.microsoft_client_id = "test_microsoft_id"
            mock_config.microsoft_client_secret = "test_microsoft_secret"
            mock_config.apple_client_id = None
            mock_config.apple_client_secret = None
            mock_config.host = "localhost"
            mock_config.port = 8000
            yield mock_config

    def test_service_manager_initialization(self, mock_config: MagicMock | AsyncMock) -> None:
        """Test service manager initialization."""
        manager = OAuthServiceManager()

        available_providers = manager.get_available_providers()
        assert "google" in available_providers
        assert "microsoft" in available_providers
        assert "apple" not in available_providers  # Not configured

    def test_provider_availability(self, mock_config: MagicMock | AsyncMock) -> None:
        """Test provider availability checking."""
        manager = OAuthServiceManager()

        assert manager.is_provider_available("google")
        assert manager.is_provider_available("microsoft")
        assert not manager.is_provider_available("apple")
        assert not manager.is_provider_available("invalid")

    def test_get_provider(self, mock_config: MagicMock | AsyncMock) -> None:
        """Test getting specific providers."""
        manager = OAuthServiceManager()

        google_provider = manager.get_provider("google")
        assert isinstance(google_provider, GoogleOAuthProvider)

        microsoft_provider = manager.get_provider("microsoft")
        assert isinstance(microsoft_provider, MicrosoftOAuthProvider)

        with pytest.raises(ValidationError):
            manager.get_provider("invalid")

    def test_authorization_url_generation(self, mock_config: MagicMock | AsyncMock) -> None:
        """Test authorization URL generation through manager."""
        manager = OAuthServiceManager()

        auth_url, state_token = manager.generate_authorization_url("google")

        assert "accounts.google.com" in auth_url
        assert len(state_token) > 20
        assert state_token in manager.state_manager._states_cache

    @pytest.mark.asyncio
    async def test_callback_handling_invalid_state(self, mock_config: MagicMock | AsyncMock) -> None:
        """Test callback handling with invalid state."""
        manager = OAuthServiceManager()

        with pytest.raises(ValidationError, match="Invalid or expired OAuth state"):
            await manager.handle_callback("google", "test_code", "invalid_state")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
