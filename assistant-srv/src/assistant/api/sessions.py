"""
Session management API endpoints.
Focused on HTTP layer concerns only, business logic delegated to services.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel

from ..models.session import SessionCreateRequest, SessionResponse
from ..services.session_service import SessionService
from ..repositories.json_session_repository import JsonSessionRepository
from ..core.exceptions import ValidationError
from ..utils.auth import get_current_active_user, CurrentUser
from ..utils.permissions import require_admin, require_owner_or_admin


# Pydantic models for Session API (temporary, will be moved to models/api/)
from ..models.api.session_api import SessionCreateRequestData, SessionRefreshRequestData


# Dependency injection
def get_session_service() -> SessionService:
    """Get session service instance."""
    session_repository = JsonSessionRepository()
    return SessionService(session_repository)


# Router
router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
@require_owner_or_admin
async def create_session(
    session_data: SessionCreateRequestData,
    request: Request,
    session_service: SessionService = Depends(get_session_service),
    current_user: CurrentUser = Depends(get_current_active_user),
) -> SessionResponse:
    """Create a new session."""
    try:
        # Extract client information from request
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Create session request
        request_obj = SessionCreateRequest(
            user_id=session_data.user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=session_data.device_info,
            extend_hours=session_data.extend_hours,
        )

        session = await session_service.create_session(request_obj)

        return SessionResponse.from_session(session)

    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{token}", response_model=SessionResponse)
async def get_session(
    token: str, session_service: SessionService = Depends(get_session_service)
) -> SessionResponse:
    """Get session by token."""
    session = await session_service.get_session_by_token(token)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or expired"
        )

    return SessionResponse.from_session(session)


@router.get("/user/{user_id}", response_model=List[SessionResponse])
@require_owner_or_admin
async def get_user_sessions(
    user_id: str,
    active_only: bool = False,
    session_service: SessionService = Depends(get_session_service),
    current_user: CurrentUser = Depends(get_current_active_user),
) -> List[SessionResponse]:
    """Get all sessions for a user."""
    sessions = await session_service.get_user_sessions(user_id, active_only)

    return [SessionResponse.from_session(session) for session in sessions]


@router.post("/{token}/refresh", response_model=SessionResponse)
async def refresh_session(
    token: str,
    refresh_data: SessionRefreshRequestData,
    session_service: SessionService = Depends(get_session_service),
) -> SessionResponse:
    """Refresh session expiration."""
    session = await session_service.refresh_session(token, refresh_data.extend_hours)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or expired"
        )

    return SessionResponse.from_session(session)


@router.delete("/{token}", status_code=status.HTTP_204_NO_CONTENT)
async def terminate_session(
    token: str, session_service: SessionService = Depends(get_session_service)
) -> None:
    """Terminate a session."""
    success = await session_service.terminate_session(token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )


@router.delete("/user/{user_id}/all", status_code=status.HTTP_200_OK)
@require_owner_or_admin
async def terminate_user_sessions(
    user_id: str,
    session_service: SessionService = Depends(get_session_service),
    current_user: CurrentUser = Depends(get_current_active_user),
) -> dict:
    """Terminate all sessions for a user."""
    count = await session_service.terminate_user_sessions(user_id)

    return {"message": f"Terminated {count} sessions"}


@router.post("/cleanup", status_code=status.HTTP_200_OK)
@require_admin
async def cleanup_expired_sessions(
    session_service: SessionService = Depends(get_session_service),
    current_user: CurrentUser = Depends(get_current_active_user),
) -> dict:
    """Clean up expired sessions."""
    count = await session_service.cleanup_expired_sessions()

    return {"message": f"Cleaned up {count} expired sessions"}


@router.post("/{token}/validate", response_model=SessionResponse)
async def validate_session(
    token: str, session_service: SessionService = Depends(get_session_service)
) -> SessionResponse:
    """Validate session token."""
    session = await session_service.validate_session(token)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    return SessionResponse.from_session(session)
