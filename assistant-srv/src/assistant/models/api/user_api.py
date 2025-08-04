"""
API request and response models for user management.
Separated from core domain models following separation of concerns.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreateAPI(BaseModel):
    """User creation API model."""

    username: str
    email: EmailStr
    password: Optional[str] = None
    display_name: Optional[str] = None
    role: str = "user"


class UserUpdateAPI(BaseModel):
    """User update API model - basic profile information only."""

    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class EmailChangeAPI(BaseModel):
    """Email change API model."""

    new_email: EmailStr
    password: str


class RoleChangeAPI(BaseModel):
    """Role change API model."""

    new_role: str
    reason: Optional[str] = None


class LoginAPI(BaseModel):
    """Login API model."""

    username: str
    password: str


class PasswordChangeAPI(BaseModel):
    """Password change API model."""

    old_password: str
    new_password: str


class OAuthLoginAPI(BaseModel):
    """OAuth login API model."""

    provider: str
    provider_id: str
    email: str
    username: str
    display_name: Optional[str] = None
    avatar: Optional[str] = None


class UserResponseAPI(BaseModel):
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


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str
    user: UserResponseAPI
