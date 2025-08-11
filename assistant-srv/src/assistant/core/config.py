"""
Core configuration settings for the assistant server.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration."""

    # Server settings
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    base_url: Optional[str] = None  # Base URL for OAuth redirects

    # Data storage
    data_dir: str = "data"
    users_file: str = "users.json"

    # Authentication
    secret_key: str = "your-secret-key-change-this-in-production"
    access_token_expire_minutes: int = 30

    # Password security settings
    bcrypt_rounds: int = 12  # bcrypt cost factor (4-31, higher = more secure but slower)

    # Session security settings
    session_secret_key: str = "your-session-secret-key-change-this-in-production-32bytes!"
    session_expire_hours: float = 24
    enable_token_encryption: bool = True

    # JWT settings
    jwt_issuer: str = "assistant-server"
    jwt_algorithm: str = "HS256"
    jwt_secret_key: str = "your-jwt-secret-key-change-this-in-production"
    jwt_expire_hours: float = 0.5  # 30 minutes default expiration

    # OAuth settings
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    apple_client_id: Optional[str] = None
    apple_client_secret: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            host=os.getenv("HOST", "localhost"),
            port=int(os.getenv("PORT", "8000")),
            debug=os.getenv("DEBUG", "False").lower() == "true",
            data_dir=os.getenv("DATA_DIR", "data"),
            users_file=os.getenv("USERS_FILE", "users.json"),
            secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            bcrypt_rounds=int(os.getenv("BCRYPT_ROUNDS", "12")),
            session_secret_key=os.getenv(
                "SESSION_SECRET_KEY", "your-session-secret-key-change-this-in-production-32bytes!"
            ),
            session_expire_hours=float(os.getenv("SESSION_EXPIRE_HOURS", "24")),
            enable_token_encryption=os.getenv("ENABLE_TOKEN_ENCRYPTION", "true").lower() == "true",
            jwt_issuer=os.getenv("JWT_ISSUER", "assistant-server"),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            jwt_expire_hours=float(os.getenv("JWT_EXPIRE_HOURS", "0.5")),
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-this-in-production"),
            google_client_id=os.getenv("GOOGLE_CLIENT_ID"),
            google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            microsoft_client_id=os.getenv("MICROSOFT_CLIENT_ID"),
            microsoft_client_secret=os.getenv("MICROSOFT_CLIENT_SECRET"),
            apple_client_id=os.getenv("APPLE_CLIENT_ID"),
            apple_client_secret=os.getenv("APPLE_CLIENT_SECRET"),
        )


# Global configuration instance
config = Config.from_env()
