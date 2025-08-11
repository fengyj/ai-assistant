from pydantic import BaseModel

from .user_api import UserResponseData  # Import UserResponseData model


class LoginRequestData(BaseModel):
    """Login API request model."""

    username: str
    password: str


class LoginResponseData(BaseModel):
    """Login response API model."""

    access_token: str
    token_type: str
    expires_in: int  # in seconds
    session_id: str
    user: UserResponseData


# Request/Response models
class RefreshTokenRequestData(BaseModel):
    """Request model for token refresh."""

    extend_session: bool = True


class RefreshTokenResponseData(BaseModel):
    """Response model for token refresh."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int  # in seconds
    session_id: str


class LogoutResponseData(BaseModel):
    """Response model for logout."""

    message: str
