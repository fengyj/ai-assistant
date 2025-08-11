"""
Session service for session management.
"""

from datetime import datetime, timezone
from typing import List, Optional

from ..core.exceptions import ValidationError
from ..models.session import UserSession
from ..repositories.session_repository import SessionRepository
from ..utils.security import TokenGenerator


class SessionService:
    """Session service for session management."""

    def __init__(self, session_repository: SessionRepository):
        """Initialize session service."""
        self.session_repository = session_repository
        self.token_generator = TokenGenerator()

    async def create_session(self, session: UserSession) -> UserSession:
        """
        Create a new user session. Accepts a fully constructed UserSession instance.
        The caller is responsible for setting all required fields and handling expiration/IP tracking as needed.
        """
        if not session.user_id:
            raise ValidationError("User ID is required")

        # Save to database (session.id is auto-generated)
        created_session = await self.session_repository.create(session)
        # Note: JWT token is generated separately using session.id when needed
        return created_session

    async def update_session_ip(
        self, session_id: str, user_id: str, current_ip: Optional[str]
    ) -> Optional[UserSession]:
        """Update session IP tracking for security analysis."""
        if not current_ip:
            return None

        if not session_id:
            return None

        # Get session by ID
        session = await self.session_repository.get_by_session_id_and_user_id(session_id, user_id)
        if session and session.is_active():
            # Update IP tracking
            session.update_ip_tracking(current_ip)
            session.last_accessed = datetime.now(timezone.utc)
            await self.session_repository.update(session)
            return session
        return None

    async def get_by_session_id_and_user_id(self, session_id: str, user_id: str) -> Optional[UserSession]:
        """Get session by ID and user ID."""
        return await self.session_repository.get_by_session_id_and_user_id(session_id, user_id)

    async def get_user_sessions(self, user_id: str, active_only: bool = False) -> List[UserSession]:
        """Get all sessions for a user."""
        if active_only:
            return await self.session_repository.get_active_sessions(user_id)
        else:
            return await self.session_repository.get_by_user_id(user_id)

    async def refresh_session(self, session_id: str, user_id: str, extend_hours: int = 24) -> Optional[UserSession]:
        """Refresh session expiration."""

        session = await self.session_repository.get_by_session_id_and_user_id(session_id, user_id)

        if session and session.is_active():
            session.refresh(extend_hours)
            return await self.session_repository.update(session)

        return None

    async def terminate_session(self, session_id: str, user_id: str) -> bool:
        """Terminate a session."""
        if not session_id:
            return False

        session = await self.session_repository.get_by_session_id_and_user_id(session_id, user_id)

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
