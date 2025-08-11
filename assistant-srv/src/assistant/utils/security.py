"""
Password hashing and verification utilities.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
import jwt

from ..core.exceptions import TokenExpiredError


class PasswordHasher:
    """Password hashing utility using bcrypt with configurable rounds."""

    DEFAULT_ROUNDS = 12  # Good balance between security and performance

    @classmethod
    def hash_password(cls, password: str, rounds: Optional[int] = None) -> str:
        """
        Hash a password using bcrypt with salt.

        Args:
            password: The plain text password to hash
            rounds: The number of bcrypt rounds (cost factor). Higher = more secure but slower.
                   Defaults to value from config. Range: 4-31, each increment doubles the time.

        Returns:
            The hashed password string (includes salt)

        Note:
            bcrypt automatically generates a unique random salt for each password,
            so no manual salt management is needed.
        """
        if not password:
            raise ValueError("Password cannot be empty")

        # Use config default if not specified
        if rounds is None:
            from ..core.config import config

            rounds = config.bcrypt_rounds

        # Validate rounds parameter
        if not (4 <= rounds <= 31):
            raise ValueError("bcrypt rounds must be between 4 and 31")

        # Generate salt with specified rounds and hash the password
        salt = bcrypt.gensalt(rounds=rounds)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        if isinstance(hashed, bytes):
            return hashed.decode("utf-8")
        return str(hashed)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: The plain text password to verify
            hashed_password: The stored hash to verify against

        Returns:
            True if password matches, False otherwise

        Note:
            This is constant-time verification that prevents timing attacks.
        """
        if not password or not hashed_password:
            return False

        try:
            result = bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
            return bool(result)
        except (ValueError, TypeError):
            # Handle invalid hash format gracefully
            return False

    @classmethod
    def needs_rehash(cls, hashed_password: str, rounds: Optional[int] = None) -> bool:
        """
        Check if a password hash needs to be rehashed with current settings.

        This is useful for upgrading password security when changing the rounds parameter.

        Args:
            hashed_password: The stored hash to check
            rounds: The desired rounds (defaults to config value)

        Returns:
            True if the hash should be updated, False otherwise
        """
        if rounds is None:
            from ..core.config import config

            rounds = config.bcrypt_rounds

        try:
            # Extract the rounds from the existing hash
            # bcrypt hash format: $2b$rounds$salthash
            parts = hashed_password.split("$")
            if len(parts) >= 3:
                current_rounds = int(parts[2])
                return current_rounds < rounds
        except (ValueError, IndexError):
            # If we can't parse the hash, it probably needs rehashing
            return True

        return False


class TokenGenerator:
    """Secure token generation utility with JWT support."""

    @classmethod
    def _get_secret_key(cls) -> str:
        """Get secret key from config."""
        from ..core.config import config

        return config.session_secret_key

    @staticmethod
    def generate_session_id(length: int = 16) -> str:
        """Generate a random session ID (internal use)."""
        return secrets.token_urlsafe(length)

    @classmethod
    def generate_jwt_token(
        cls, session_id: str, user_id: str, user_info: Optional[Dict[str, Any]] = None, expire_hours: float = 0.25
    ) -> str:
        """Generate a JWT token with user information."""
        from ..core.config import config

        now = datetime.now(timezone.utc)

        # Base payload with standard claims
        payload = {
            "sub": user_id,
            "sid": session_id,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=expire_hours)).timestamp()),
            "jti": secrets.token_urlsafe(8),
            "iss": config.jwt_issuer,
        }

        # Add safe user fields to JWT
        safe_user_fields = [
            "username",
            "display_name",
            "role",
            "permissions",
            "status",
            "email",
            "department",
            "locale",
        ]
        if not user_info:
            user_info = {}
        for field in safe_user_fields:
            if field in user_info and user_info[field] is not None:
                payload[field] = user_info[field]

        secret_key = cls._get_secret_key()
        token = jwt.encode(payload, secret_key, algorithm=config.jwt_algorithm)
        if isinstance(token, bytes):
            return token.decode("utf-8")
        return str(token)

    @classmethod
    def decode_jwt_token(cls, token: str, verify_expiry: bool = True) -> Optional[Dict[str, Any]]:
        """Decode and verify a JWT token."""
        try:
            from ..core.config import config

            secret_key = cls._get_secret_key()
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[config.jwt_algorithm],
                options={"verify_exp": verify_expiry},  # Verify expiration
            )
            from typing import Any, Dict, cast

            return cast(Dict[str, Any], payload)
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.PyJWTError:
            # Any JWT error means invalid token
            return None

    @classmethod
    def extract_session_id_from_jwt(cls, token: str) -> Optional[str]:
        """Extract session_id from JWT token, ignoring expiration."""
        payload = cls.decode_jwt_token(token, verify_expiry=False)
        if payload:
            return cls.extract_session_id_from_dict(payload)
        return None

    @classmethod
    def extract_session_id_from_dict(cls, token_data: Dict[str, Any]) -> Optional[str]:
        """Extract session_id from JWT token, ignoring expiration."""
        if token_data:
            return token_data.get("sid")  # session ID claim (use 'sid' to match generation)
        return None

    @classmethod
    def extract_user_id_from_dict(cls, token_data: Dict[str, Any]) -> Optional[str]:
        """Extract session_id from JWT token, ignoring expiration."""
        if token_data:
            return token_data.get("sub")  # session ID claim (use 'sub' to match generation)
        return None

    @classmethod
    def extract_user_name_from_dict(cls, token_data: Dict[str, Any]) -> Optional[str]:
        """Extract session_id from JWT token, ignoring expiration."""
        if token_data:
            return token_data.get("username")
        return None

    @classmethod
    def extract_user_role_from_dict(cls, token_data: Dict[str, Any]) -> Optional[str]:
        """Extract session_id from JWT token, ignoring expiration."""
        if token_data:
            return token_data.get("role")
        return None

    @classmethod
    def extract_user_permissions_from_dict(cls, token_data: Dict[str, Any]) -> Optional[list[Any]]:
        """Extract user permissions from JWT token."""
        if token_data is None:
            return None
        permissions = token_data.get("permissions")
        if permissions is None:
            return []
        # Ensure the return type is always a list
        return list(permissions) if isinstance(permissions, (list, tuple, set)) else [permissions]

    @classmethod
    def extract_user_status_from_dict(cls, token_data: Dict[str, Any]) -> Optional[str]:
        """Extract user status from JWT token."""
        if token_data:
            return token_data.get("status")
        return None

    @classmethod
    def extract_user_email_from_dict(cls, token_data: Dict[str, Any]) -> Optional[str]:
        """Extract user email from JWT token."""
        if token_data:
            return token_data.get("email")
        return None

    @classmethod
    def generate_token(cls, length: int = 32) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(length)
