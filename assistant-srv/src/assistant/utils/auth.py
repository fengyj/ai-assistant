"""
Authentication and authorization utilities for API endpoints.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from ..models import UserRole, UserStatus
from ..services.user_service import UserService
from ..repositories.json_user_repository import JsonUserRepository
from ..core.config import config


# JWT Configuration
SECRET_KEY = config.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class TokenData(BaseModel):
    """Token data model."""

    user_id: Optional[str] = None
    username: Optional[str] = None


class CurrentUser(BaseModel):
    """Current authenticated user model."""

    id: str
    username: str
    email: str
    role: UserRole
    status: UserStatus


# Security scheme
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_service() -> UserService:
    """Get user service instance."""
    user_repository = JsonUserRepository()
    return UserService(user_repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service),
) -> CurrentUser:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    if token_data.user_id is None:
        raise credentials_exception

    user = await user_service.get_user_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception

    # Check if user is active
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
        )

    return CurrentUser(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        status=user.status,
    )


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Get current active user."""
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: CurrentUser = Depends(get_current_active_user),
) -> CurrentUser:
    """Get current admin user (requires admin role)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


def require_user_or_admin():
    """
    Create a dependency that requires user to be accessing their own data
    or be an admin. The actual user_id will be checked in the endpoint.
    """

    async def check_user_permission(
        current_user: CurrentUser = Depends(get_current_active_user),
    ) -> CurrentUser:
        # This will be used in the endpoint to check the specific user_id
        return current_user

    return check_user_permission


class RoleChecker:
    """Role-based access control checker."""

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: CurrentUser = Depends(get_current_active_user)):
        if current_user.role not in self.allowed_roles:
            allowed_roles_str = [role.value for role in self.allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires one of {allowed_roles_str}",
            )
        return current_user


# Common role checkers
admin_only = RoleChecker([UserRole.ADMIN])
user_or_admin = RoleChecker([UserRole.USER, UserRole.ADMIN])
