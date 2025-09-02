"""
Session management API endpoints.
Focused on HTTP layer concerns only, business logic delegated to services.
These APIs are primarily for session management purposes:
- Users can view and manage their active sessions
- Admins can manage sessions for maintenance
Note: Session creation happens via /auth/login, token refresh via /auth/refresh-token
"""

from typing import List

from fastapi import APIRouter, Depends, status

# Import centralized dependencies
from ..core.dependencies import get_session_service
from ..models.api.exceptions import NotFoundException
from ..models.api.session_api import (
    SessionCleanupResponseData,
    SessionTerminateResponseData,
)
from ..models.session import SessionResponse
from ..services.session_service import SessionService
from ..utils.auth import (
    CurrentUser,
    get_admin,
    get_owner_or_admin,
)

# Router
router = APIRouter(prefix="/api/sessions", tags=["sessions"])


# Deprecated: Get session by session ID (use /auth/login for session creation)
# @router.get("/user/{user_id}", response_model=SessionResponse)
# async def get_session(
#     user_id: str,
#     session_service: SessionService = Depends(get_session_service),
#     current_user: CurrentUser = Depends(get_owner_or_admin),
# ) -> SessionResponse:
#     """Get session by session ID."""
#     session = await session_service.get_session_by_id(current_user.session_id)
#     if not session:
#         raise NotFoundException(detail="Session not found or expired")
#     return SessionResponse.from_session(session)


@router.get("/user/{user_id}", response_model=List[SessionResponse])
async def get_sessions(
    user_id: str,
    active_only: bool = False,
    session_service: SessionService = Depends(get_session_service),
    current_user: CurrentUser = Depends(get_owner_or_admin),
) -> List[SessionResponse]:
    """
    Get all sessions for a user by user_id.
    If active_only is True, only return active sessions.
    """
    sessions = await session_service.get_user_sessions(user_id, active_only)
    return [SessionResponse.from_session(session) for session in sessions]


@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def terminate_session(
    user_id: str,
    session_service: SessionService = Depends(get_session_service),
    current_user: CurrentUser = Depends(get_owner_or_admin),
) -> None:
    """
    Terminate the current user's session (by session_id).
    Note: user_id is for permission check, actual termination uses current_user.session_id.
    """
    success = await session_service.terminate_session(current_user.session_id, user_id)
    if not success:
        raise NotFoundException(detail="Session not found")


@router.delete("/user/{user_id}/all", status_code=status.HTTP_200_OK)
async def terminate_user_sessions(
    user_id: str,
    session_service: SessionService = Depends(get_session_service),
    current_user: CurrentUser = Depends(get_owner_or_admin),
) -> SessionTerminateResponseData:
    """
    Terminate all sessions for a user by user_id.
    Only owner or admin can perform this operation.
    """
    count = await session_service.terminate_user_sessions(user_id)
    return SessionTerminateResponseData(message=f"Terminated {count} sessions")


@router.post("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_expired_sessions(
    session_service: SessionService = Depends(get_session_service),
    current_user: CurrentUser = Depends(get_admin),
) -> SessionCleanupResponseData:
    """Clean up expired sessions."""
    count = await session_service.cleanup_expired_sessions()

    return SessionCleanupResponseData(message=f"Cleaned up {count} expired sessions")
