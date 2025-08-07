"""
API request and response models for user management.
Separated from core domain models following separation of concerns.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreateRequestData(BaseModel):
    """User creation API request model."""

    username: str
    email: EmailStr
    password: Optional[str] = None
    display_name: Optional[str] = None
    role: str = "user"


class UserUpdateRequestData(BaseModel):
    """User update API request model - basic profile information only."""

    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class EmailChangeRequestData(BaseModel):
    """Email change API request model."""

    new_email: EmailStr
    password: str


class RoleChangeRequestData(BaseModel):
    """Role change API request model."""

    new_role: str
    reason: Optional[str] = None


class LoginRequestData(BaseModel):
    """Login API request model."""

    username: str
    password: str


class PasswordChangeRequestData(BaseModel):
    """Password change API request model."""

    old_password: str
    new_password: str


class OAuthLoginRequestData(BaseModel):
    """OAuth login API request model."""

    provider: str
    provider_id: str
    email: str
    username: str
    display_name: Optional[str] = None
    avatar: Optional[str] = None


class UserResponseData(BaseModel):
    """User response API model."""

    id: str
    username: str
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    status: str
    created_at: str
    last_login: Optional[str] = None


class TokenResponseData(BaseModel):
    """Token response API model."""

    access_token: str
    token_type: str
    user: UserResponseData


class PasswordChangeResponseData(BaseModel):
    """Password change response API model."""

    success: bool = True
    message: str = "Password changed successfully"
