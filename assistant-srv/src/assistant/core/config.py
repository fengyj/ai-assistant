"""
Core configuration settings for the assistant server.
"""

import os
from typing import Optional
from dataclasses import dataclass


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
    jwt_secret_key: str = "your-jwt-secret-key-change-this-in-production"
    access_token_expire_minutes: int = 30

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
            secret_key=os.getenv(
                "SECRET_KEY", "your-secret-key-change-this-in-production"
            ),
            jwt_secret_key=os.getenv(
                "JWT_SECRET_KEY", "your-jwt-secret-key-change-this-in-production"
            ),
            access_token_expire_minutes=int(
                os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
            ),
            google_client_id=os.getenv("GOOGLE_CLIENT_ID"),
            google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            microsoft_client_id=os.getenv("MICROSOFT_CLIENT_ID"),
            microsoft_client_secret=os.getenv("MICROSOFT_CLIENT_SECRET"),
            apple_client_id=os.getenv("APPLE_CLIENT_ID"),
            apple_client_secret=os.getenv("APPLE_CLIENT_SECRET"),
        )


# Global configuration instance
config = Config.from_env()
