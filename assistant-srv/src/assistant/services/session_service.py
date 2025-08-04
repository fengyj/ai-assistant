"""
Session service for session management.
"""

from datetime import datetime, timezone
from typing import Optional, List
from ..models.session import (
    UserSession,
    SessionCreateRequest,
    SessionResponse,
    SessionStatus,
)
from ..repositories.session_repository import SessionRepository
from ..utils.security import TokenGenerator
from ..core.exceptions import ValidationError


class SessionService:
    """Session service for session management."""

    def __init__(self, session_repository: SessionRepository):
        """Initialize session service."""
        self.session_repository = session_repository

    async def create_session(self, request: SessionCreateRequest) -> UserSession:
        """Create a new user session."""
        if not request.user_id:
            raise ValidationError("User ID is required")

        # Generate session token
        token = TokenGenerator.generate_token(32)

        # Create session
        session = UserSession(
            user_id=request.user_id,
            token=token,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            device_info=request.device_info,
        )

        # Set expiration
        if request.extend_hours > 0:
            session.refresh(request.extend_hours)

        return await self.session_repository.create(session)

    async def get_session_by_token(self, token: str) -> Optional[UserSession]:
        """Get session by token."""
        session = await self.session_repository.get_by_token(token)

        if session and session.is_active():
            # Update last accessed time
            session.last_accessed = datetime.now(timezone.utc)
            await self.session_repository.update(session)
            return session

        return None

    async def get_session_by_id(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID."""
        return await self.session_repository.get_by_id(session_id)

    async def get_user_sessions(
        self, user_id: str, active_only: bool = False
    ) -> List[UserSession]:
        """Get all sessions for a user."""
        if active_only:
            return await self.session_repository.get_active_sessions(user_id)
        else:
            return await self.session_repository.get_by_user_id(user_id)

    async def refresh_session(
        self, token: str, extend_hours: int = 24
    ) -> Optional[UserSession]:
        """Refresh session expiration."""
        session = await self.session_repository.get_by_token(token)

        if session and session.is_active():
            session.refresh(extend_hours)
            return await self.session_repository.update(session)

        return None

    async def terminate_session(self, token: str) -> bool:
        """Terminate a session."""
        session = await self.session_repository.get_by_token(token)

        if session:
            session.terminate()
            await self.session_repository.update(session)
            return True

        return False

    async def terminate_user_sessions(self, user_id: str) -> int:
        """Terminate all sessions for a user."""
        return await self.session_repository.terminate_user_sessions(user_id)

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        return await self.session_repository.cleanup_expired_sessions()

    async def validate_session(self, token: str) -> Optional[UserSession]:
        """Validate session token and return session if valid."""
        return await self.get_session_by_token(token)
