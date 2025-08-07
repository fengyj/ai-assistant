"""
OAuth provider base classes and implementations.
"""

import base64
import logging
import time
import urllib.parse
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
import jwt
from cryptography.hazmat.primitives import serialization

from ..core.exceptions import ValidationError
from ..models import OAuthProvider

logger = logging.getLogger(__name__)


@dataclass
class OAuthConfig:
    """OAuth provider configuration."""

    client_id: str
    client_secret: str
    redirect_uri: str
    scope: List[str]
    authorization_url: str
    token_url: str
    user_info_url: str


@dataclass
class OAuthTokenResponse:
    """OAuth token response."""

    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    token_type: str = "Bearer"
    scope: Optional[str] = None


@dataclass
class OAuthUserProfile:
    """Standardized OAuth user profile."""

    provider_id: str
    email: str
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    avatar_url: Optional[str] = None
    locale: Optional[str] = None
    verified_email: bool = True


class BaseOAuthProvider(ABC):
    """Base class for OAuth providers."""

    def __init__(self, config: OAuthConfig):
        """Initialize OAuth provider with configuration."""
        self.config = config
        self.http_client = httpx.AsyncClient()

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name."""
        pass

    @property
    @abstractmethod
    def provider_enum(self) -> OAuthProvider:
        """Get provider enum value."""
        pass

    def generate_authorization_url(self, state: str, **kwargs: Any) -> str:
        """Generate OAuth authorization URL."""
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scope),
            "response_type": "code",
            "state": state,
            **kwargs,
        }

        # Add provider-specific parameters
        params.update(self._get_additional_auth_params())

        query_string = urllib.parse.urlencode(params)
        return f"{self.config.authorization_url}?{query_string}"

    @abstractmethod
    def _get_additional_auth_params(self) -> Dict[str, str]:
        """Get provider-specific authorization parameters."""
        pass

    async def exchange_code_for_token(self, code: str, state: str) -> OAuthTokenResponse:
        """Exchange authorization code for access token."""
        token_data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri,
        }

        # Add provider-specific token parameters
        token_data.update(self._get_additional_token_params())

        response = await self.http_client.post(
            self.config.token_url,
            data=token_data,
            headers={"Accept": "application/json"},
        )

        if response.status_code != 200:
            raise ValidationError(f"Token exchange failed: {response.text}")

        token_info = response.json()
        return self._parse_token_response(token_info)

    @abstractmethod
    def _get_additional_token_params(self) -> Dict[str, str]:
        """Get provider-specific token parameters."""
        pass

    @abstractmethod
    def _parse_token_response(self, token_info: Dict[str, Any]) -> OAuthTokenResponse:
        """Parse token response from provider."""
        pass

    async def get_user_profile(self, access_token: str) -> OAuthUserProfile:
        """Get user profile using access token."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        response = await self.http_client.get(self.config.user_info_url, headers=headers)

        if response.status_code != 200:
            raise ValidationError(f"Failed to get user profile: {response.text}")

        user_info = response.json()
        return self._parse_user_profile(user_info)

    @abstractmethod
    def _parse_user_profile(self, user_info: Dict[str, Any]) -> OAuthUserProfile:
        """Parse user profile from provider response."""
        pass

    async def close(self) -> None:
        """Close HTTP client."""
        await self.http_client.aclose()


class GoogleOAuthProvider(BaseOAuthProvider):
    """Google OAuth provider implementation."""

    @property
    def provider_name(self) -> str:
        return "google"

    @property
    def provider_enum(self) -> OAuthProvider:
        return OAuthProvider.GOOGLE

    def _get_additional_auth_params(self) -> Dict[str, str]:
        return {"access_type": "offline", "prompt": "consent"}

    def _get_additional_token_params(self) -> Dict[str, str]:
        return {}

    def _parse_token_response(self, token_info: Dict[str, Any]) -> OAuthTokenResponse:
        return OAuthTokenResponse(
            access_token=token_info["access_token"],
            refresh_token=token_info.get("refresh_token"),
            expires_in=token_info.get("expires_in"),
            token_type=token_info.get("token_type", "Bearer"),
            scope=token_info.get("scope"),
        )

    def _parse_user_profile(self, user_info: Dict[str, Any]) -> OAuthUserProfile:
        return OAuthUserProfile(
            provider_id=user_info["sub"],
            email=user_info["email"],
            name=user_info.get("name"),
            given_name=user_info.get("given_name"),
            family_name=user_info.get("family_name"),
            avatar_url=user_info.get("picture"),
            locale=user_info.get("locale"),
            verified_email=user_info.get("email_verified", True),
        )


class MicrosoftOAuthProvider(BaseOAuthProvider):
    """Microsoft OAuth provider implementation."""

    @property
    def provider_name(self) -> str:
        return "microsoft"

    @property
    def provider_enum(self) -> OAuthProvider:
        return OAuthProvider.MICROSOFT

    def _get_additional_auth_params(self) -> Dict[str, str]:
        return {"response_mode": "query"}

    def _get_additional_token_params(self) -> Dict[str, str]:
        return {}

    def _parse_token_response(self, token_info: Dict[str, Any]) -> OAuthTokenResponse:
        return OAuthTokenResponse(
            access_token=token_info["access_token"],
            refresh_token=token_info.get("refresh_token"),
            expires_in=token_info.get("expires_in"),
            token_type=token_info.get("token_type", "Bearer"),
            scope=token_info.get("scope"),
        )

    def _parse_user_profile(self, user_info: Dict[str, Any]) -> OAuthUserProfile:
        return OAuthUserProfile(
            provider_id=user_info["id"],
            email=user_info["mail"] or user_info.get("userPrincipalName") or "",
            name=user_info.get("displayName"),
            given_name=user_info.get("givenName"),
            family_name=user_info.get("surname"),
            avatar_url=None,  # Microsoft Graph API requires separate call for photo
            locale=user_info.get("preferredLanguage"),
            verified_email=True,  # Microsoft accounts are typically verified
        )

    async def get_user_profile(self, access_token: str) -> OAuthUserProfile:
        """Get user profile with avatar from Microsoft Graph API."""
        # First get basic user info
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        response = await self.http_client.get(self.config.user_info_url, headers=headers)

        if response.status_code != 200:
            raise ValidationError(f"Failed to get user profile: {response.text}")

        user_info = response.json()

        # Try to get user photo from Microsoft Graph
        avatar_url = None
        try:
            photo_response = await self.http_client.get(
                "https://graph.microsoft.com/v1.0/me/photo/$value", headers=headers
            )
            if photo_response.status_code == 200:
                # Microsoft returns the actual image data, not a URL
                # For production, you'd save this to a file storage service
                # For now, we'll use a placeholder or skip it
                logger.info("Microsoft user photo retrieved successfully")
                # In a real implementation, you'd upload this to your storage
                # and return the URL to your stored image
                avatar_url = f"data:image/jpeg;base64,{base64.b64encode(photo_response.content).decode()}"
        except Exception as e:
            logger.warning(f"Failed to get Microsoft user photo: {e}")

        return OAuthUserProfile(
            provider_id=user_info["id"],
            email=user_info["mail"] or user_info.get("userPrincipalName") or "",
            name=user_info.get("displayName"),
            given_name=user_info.get("givenName"),
            family_name=user_info.get("surname"),
            avatar_url=avatar_url,
            locale=user_info.get("preferredLanguage"),
            verified_email=True,
        )


class AppleOAuthProvider(BaseOAuthProvider):
    """Apple OAuth provider implementation."""

    @property
    def provider_name(self) -> str:
        return "apple"

    @property
    def provider_enum(self) -> OAuthProvider:
        return OAuthProvider.APPLE

    def _get_additional_auth_params(self) -> Dict[str, str]:
        return {"response_mode": "form_post"}

    def _get_additional_token_params(self) -> Dict[str, str]:
        # Apple requires client_secret to be a JWT signed with your private key
        # For production, implement proper JWT generation with Apple private key
        return {}

    def _parse_token_response(self, token_info: Dict[str, Any]) -> OAuthTokenResponse:
        return OAuthTokenResponse(
            access_token=token_info["access_token"],
            refresh_token=token_info.get("refresh_token"),
            expires_in=token_info.get("expires_in"),
            token_type=token_info.get("token_type", "Bearer"),
        )

    async def exchange_code_for_token(self, code: str, state: str) -> OAuthTokenResponse:
        """Exchange authorization code for access token and parse ID token."""
        token_data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri,
        }

        # Add provider-specific token parameters
        token_data.update(self._get_additional_token_params())

        response = await self.http_client.post(
            self.config.token_url,
            data=token_data,
            headers={"Accept": "application/json"},
        )

        if response.status_code != 200:
            raise ValidationError(f"Token exchange failed: {response.text}")

        token_info = response.json()

        # Parse and store ID token for user info extraction
        if "id_token" in token_info:
            self._id_token = token_info["id_token"]

        return self._parse_token_response(token_info)

    def _decode_apple_id_token(self, id_token: str) -> Dict[str, Any]:
        """Decode Apple ID token (JWT) to extract user information."""
        try:
            # Apple ID tokens are signed JWTs
            # For production, you should verify the signature using Apple's public keys
            # For demo purposes, we'll decode without verification
            # SECURITY WARNING: Never use unverified tokens in production!

            # Decode header to get key information
            header = jwt.get_unverified_header(id_token)  # noqa: F841

            # In production, fetch Apple's public keys and verify signature:
            # 1. Get Apple's public keys from https://appleid.apple.com/auth/keys
            # 2. Find the key matching the 'kid' in the header
            # 3. Verify the token signature

            # For demo, decode without verification (UNSAFE for production)
            payload = jwt.decode(id_token, options={"verify_signature": False}, algorithms=["RS256"])

            logger.warning(
                "Apple ID token decoded WITHOUT signature verification. " "This is unsafe for production use!"
            )

            return payload  # type: ignore[no-any-return]

        except jwt.InvalidTokenError as e:
            logger.error(f"Failed to decode Apple ID token: {e}")
            raise ValidationError(f"Invalid Apple ID token: {e}")

    async def get_user_profile(self, access_token: str) -> OAuthUserProfile:
        """Get user profile from Apple ID token."""
        # Apple doesn't provide a standard user info endpoint
        # User information is embedded in the ID token received during token exchange

        if not hasattr(self, "_id_token") or not self._id_token:
            raise ValidationError("Apple ID token not available. " "Call exchange_code_for_token first.")

        user_info = self._decode_apple_id_token(self._id_token)
        return self._parse_user_profile(user_info)

    def _parse_user_profile(self, user_info: Dict[str, Any]) -> OAuthUserProfile:
        """Parse user profile from Apple ID token payload."""
        # Apple ID token contains limited user information
        # Additional user data (name, etc.) is only provided on first authorization
        return OAuthUserProfile(
            provider_id=user_info["sub"],
            email=user_info.get("email", ""),
            name=user_info.get("name"),
            verified_email=user_info.get("email_verified", True),
        )


class AppleJWTGenerator:
    """Generate JWTs for Apple OAuth client authentication."""

    def __init__(self, team_id: str, key_id: str, private_key_path: str):
        """
        Initialize Apple JWT generator.

        Args:
            team_id: Your Apple Developer Team ID
            key_id: Your Apple Sign In Key ID
            private_key_path: Path to your Apple private key file (.p8)
        """
        self.team_id = team_id
        self.key_id = key_id
        self.private_key = self._load_private_key(private_key_path)

    from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes

    def _load_private_key(self, private_key_path: str) -> PrivateKeyTypes:
        """Load Apple private key from .p8 file."""
        try:
            with open(private_key_path, "rb") as key_file:
                private_key = serialization.load_pem_private_key(key_file.read(), password=None)
            return private_key
        except Exception as e:
            raise ValueError(f"Failed to load Apple private key: {e}")

    def generate_client_secret(self, client_id: str, audience: str = "https://appleid.apple.com") -> str:
        """
        Generate client secret JWT for Apple OAuth.

        Args:
            client_id: Your Apple OAuth client ID (bundle identifier)
            audience: JWT audience (usually Apple's auth server)

        Returns:
            Signed JWT string for use as client_secret
        """
        now = datetime.now(timezone.utc)

        headers = {"alg": "ES256", "kid": self.key_id}

        payload = {
            "iss": self.team_id,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=5)).timestamp()),  # Short expiry
            "aud": audience,
            "sub": client_id,
        }

        return jwt.encode(payload=payload, key=self.private_key, algorithm="ES256", headers=headers)  # type: ignore


class AppleTokenVerifier:
    """Verify Apple ID tokens in production."""

    def __init__(self) -> None:
        """Initialize Apple token verifier."""
        self._public_keys: Optional[Dict[str, Any]] = None
        self._keys_last_fetched: Optional[float] = None

    async def verify_id_token(self, id_token: str, client_id: str) -> Dict[str, Any]:
        """
        Verify Apple ID token signature and claims.

        Args:
            id_token: The ID token to verify
            client_id: Expected client ID (audience)

        Returns:
            Verified token payload

        Raises:
            ValidationError: If token is invalid
        """
        import httpx  # noqa: F401

        from ..core.exceptions import ValidationError

        try:
            # Get token header
            header = jwt.get_unverified_header(id_token)
            key_id = header.get("kid")

            if not key_id:
                raise ValidationError("Missing key ID in token header")

            # Fetch Apple's public keys if needed
            public_key = await self._get_public_key(key_id)

            # Verify token
            payload = jwt.decode(
                id_token,
                key=public_key,
                algorithms=["RS256"],
                audience=client_id,
                issuer="https://appleid.apple.com",
            )

            # Additional validation
            self._validate_token_claims(payload)

            return payload  # type: ignore[no-any-return]

        except jwt.InvalidTokenError as e:
            raise ValidationError(f"Invalid Apple ID token: {e}")

    async def _get_public_key(self, key_id: str) -> Any:
        """Fetch Apple's public key for token verification."""
        import httpx

        # Cache keys for 1 hour
        if self._public_keys is None or self._keys_last_fetched is None or time.time() - self._keys_last_fetched > 3600:

            async with httpx.AsyncClient() as client:
                response = await client.get("https://appleid.apple.com/auth/keys")
                response.raise_for_status()
                keys_data = response.json()

                self._public_keys = {key["kid"]: key for key in keys_data["keys"]}
                self._keys_last_fetched = time.time()

        if key_id not in self._public_keys:
            raise ValueError(f"Unknown key ID: {key_id}")

        # Convert JWK to PEM format for PyJWT
        from jwt.algorithms import RSAAlgorithm

        return RSAAlgorithm.from_jwk(self._public_keys[key_id])

    def _validate_token_claims(self, payload: Dict[str, Any]) -> None:
        """Validate additional token claims."""
        now = time.time()

        # Check expiration
        if payload.get("exp", 0) < now:
            raise jwt.ExpiredSignatureError("Token has expired")

        # Check issued at
        if payload.get("iat", 0) > now + 60:  # Allow 60s clock skew
            raise jwt.InvalidIssuedAtError("Token issued in the future")

        # Validate auth_time if present
        if "auth_time" in payload and payload["auth_time"] > now + 60:
            raise jwt.InvalidKeyError("Invalid auth_time")
