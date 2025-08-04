"""
Password hashing and verification utilities.
"""

import bcrypt


class PasswordHasher:
    """Password hashing utility."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


class TokenGenerator:
    """Token generation utility."""

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a random token."""
        import secrets

        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """Generate an API key."""
        import secrets

        return f"ak_{secrets.token_urlsafe(length)}"
