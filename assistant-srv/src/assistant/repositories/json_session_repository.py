"""
JSON file-based session repository implementation.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

from ..core import config
from ..models.session import SessionStatus, UserSession
from .session_repository import SessionRepository


class JsonSessionRepository(SessionRepository):
    """JSON file-based session repository."""

    def __init__(self, data_dir: str | None = None):
        """Initialize repository with data directory."""
        self.data_dir = data_dir or config.data_dir
        self.sessions_file = os.path.join(self.data_dir, "sessions.json")
        self._ensure_data_dir()
        self._sessions_cache: Dict[str, UserSession] = {}
        self._load_sessions()

    def _ensure_data_dir(self) -> None:
        """Ensure data directory exists."""
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_sessions(self) -> None:
        """Load sessions from JSON file."""
        if not os.path.exists(self.sessions_file):
            self._sessions_cache = {}
            return

        try:
            with open(self.sessions_file, "r", encoding="utf-8") as f:
                sessions_data = json.load(f)

            self._sessions_cache = {}
            for session_data in sessions_data:
                session = UserSession.from_dict(session_data)
                self._sessions_cache[session.id] = session
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If file is corrupted, start fresh
            self._sessions_cache = {}
            print(f"Warning: Error loading sessions file {self.sessions_file}: {e}")

    def _save_sessions(self) -> None:
        """Save sessions to JSON file."""
        sessions_data = [session.to_dict() for session in self._sessions_cache.values()]

        with open(self.sessions_file, "w", encoding="utf-8") as f:
            json.dump(sessions_data, f, indent=2, ensure_ascii=False)

    async def create(self, entity: UserSession) -> UserSession:
        """Create a new session."""
        entity.created_at = datetime.now(tz=timezone.utc)
        entity.last_accessed = datetime.now(tz=timezone.utc)

        self._sessions_cache[entity.id] = entity
        self._save_sessions()

        return entity

    async def get_by_id(self, entity_id: str) -> Optional[UserSession]:
        """Get session by ID."""
        return self._sessions_cache.get(entity_id)

    async def get_all(self) -> List[UserSession]:
        """Get all sessions."""
        return list(self._sessions_cache.values())

    async def update(self, entity: UserSession) -> UserSession:
        """Update a session."""
        self._sessions_cache[entity.id] = entity
        self._save_sessions()

        return entity

    async def delete(self, entity_id: str) -> bool:
        """Delete a session."""
        if entity_id not in self._sessions_cache:
            return False

        del self._sessions_cache[entity_id]
        self._save_sessions()
        return True

    async def exists(self, entity_id: str) -> bool:
        """Check if session exists."""
        return entity_id in self._sessions_cache

    async def get_by_user_id(self, user_id: str) -> List[UserSession]:
        """Get all sessions for a user."""
        return [session for session in self._sessions_cache.values() if session.user_id == user_id]

    async def get_by_session_id_and_user_id(self, session_id: str, user_id: str) -> Optional[UserSession]:
        """Get session by ID and user ID."""
        session = self._sessions_cache.get(session_id)
        if session and session.user_id == user_id:
            return session
        return None

    async def get_active_sessions(self, user_id: str) -> List[UserSession]:
        """Get active sessions for a user."""
        return [
            session for session in self._sessions_cache.values() if session.user_id == user_id and session.is_active()
        ]

    async def terminate_user_sessions(self, user_id: str) -> int:
        """Terminate all sessions for a user."""
        count = 0
        for session in self._sessions_cache.values():
            if session.user_id == user_id and session.is_active():
                session.terminate()
                count += 1

        if count > 0:
            self._save_sessions()

        return count

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        expired_session_ids = []

        for session_id, session in self._sessions_cache.items():
            if session.is_expired() or session.status == SessionStatus.TERMINATED:
                expired_session_ids.append(session_id)

        for session_id in expired_session_ids:
            del self._sessions_cache[session_id]

        if expired_session_ids:
            self._save_sessions()

        return len(expired_session_ids)
