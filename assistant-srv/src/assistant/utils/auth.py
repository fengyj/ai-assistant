"""
Authentication and authorization utilities for API endpoints.
Session-based authentication system.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Import centralized dependencies
from ..core.dependencies import get_session_service, get_user_service
from ..models import UserRole, UserStatus
from ..models.api.exceptions import ForbiddenException, UnauthorizedException
from ..services.session_service import SessionService
from ..services.user_service import UserService
from .security import TokenGenerator


class CurrentUser(BaseModel):
    """Current authenticated user model."""

    id: str
    session_id: str
    username: str
    email: str
    role: UserRole
    status: UserStatus


credentials = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(credentials),
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service),
) -> CurrentUser:
    """Get current authenticated session from session token only (no JWT required)."""
    credentials_exception = UnauthorizedException(
        detail="Could not validate session",
        headers={"WWW-Authenticate": "Session"},
    )

    token_data = TokenGenerator.decode_jwt_token(credentials.credentials)

    if token_data is None:
        raise credentials_exception

    sid = TokenGenerator.extract_session_id_from_dict(token_data)
    user_id = TokenGenerator.extract_user_id_from_dict(token_data)
    user_name = TokenGenerator.extract_user_name_from_dict(token_data)
    user_role = TokenGenerator.extract_user_role_from_dict(token_data)
    user_email = TokenGenerator.extract_user_email_from_dict(token_data)
    user_status = TokenGenerator.extract_user_status_from_dict(token_data)

    if sid is None or user_id is None:
        raise credentials_exception

    # Get session by JWT token (this automatically updates last_accessed and extends expiry)
    session = await session_service.get_by_session_id_and_user_id(sid, user_id)
    if session is None:
        raise credentials_exception

    current_user = CurrentUser(
        id=user_id,
        session_id=sid,
        username=user_name if user_name else "Unknown",
        email=user_email if user_email else "Unknown",
        role=UserRole(user_role),
        status=UserStatus(user_status) if user_status else UserStatus.INACTIVE,
    )

    return current_user


def get_user_or_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Check if the current session user is a user or an admin."""
    if current_user.role not in [UserRole.USER, UserRole.ADMIN]:
        raise ForbiddenException(detail="Access denied: You must be a user or an admin")
    return current_user


def get_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Check if the current session user is an admin."""
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException(detail="Access denied: You must be an admin")
    return current_user


def get_owner_or_admin(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Check if the current session user is the owner or an admin."""
    if current_user.role != UserRole.ADMIN and user_id != current_user.id:
        raise ForbiddenException(detail="Access denied: You can only access your own resources")
    return current_user


def get_owner(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Check if the current session user is the owner."""
    if user_id != current_user.id:
        raise ForbiddenException(detail="Access denied: You can only access your own resources")
    return current_user
