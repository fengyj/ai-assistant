"""
Session management models and services.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class SessionStatus(Enum):
    """Session status enumeration."""

    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


@dataclass
class SessionMetadata:
    """Session metadata with specific structure."""

    login_method: str  # 'password' | 'oauth'
    oauth_provider: Optional[str]
    device_type: str  # 'web' | 'mobile' | 'desktop'
    location: Optional[str]
    security_flags: List[str]


def _default_metadata() -> SessionMetadata:
    """Create default session metadata."""
    return SessionMetadata(
        login_method="password", oauth_provider=None, device_type="web", location=None, security_flags=[]
    )


@dataclass
class UserSession:
    """User session model."""

    # Session information
    id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    token: str = ""

    # Session metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[str] = None

    # Status and timing
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24))

    # Additional data
    metadata: SessionMetadata = field(default_factory=_default_metadata)

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == SessionStatus.ACTIVE and not self.is_expired()

    def refresh(self, extend_hours: int = 24) -> None:
        """Refresh session expiration."""
        self.last_accessed = datetime.now(timezone.utc)
        self.expires_at = datetime.now(timezone.utc) + timedelta(hours=extend_hours)

    def terminate(self) -> None:
        """Terminate the session."""
        self.status = SessionStatus.TERMINATED

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "device_info": self.device_info,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSession":
        """Create session from dictionary."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            token=data["token"],
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            device_info=data.get("device_info"),
            status=SessionStatus(data.get("status", "active")),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SessionCreateRequest:
    """Session creation request."""

    user_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[str] = None
    extend_hours: int = 24


@dataclass
class SessionResponse:
    """Session response."""

    id: str
    user_id: str
    token: str
    status: str
    created_at: str
    last_accessed: str
    expires_at: str
    device_info: Optional[str] = None

    @classmethod
    def from_session(cls, session: UserSession) -> "SessionResponse":
        """Create response from session."""
        return cls(
            id=session.id,
            user_id=session.user_id,
            token=session.token,
            status=session.status.value,
            created_at=session.created_at.isoformat(),
            last_accessed=session.last_accessed.isoformat(),
            expires_at=session.expires_at.isoformat(),
            device_info=session.device_info,
        )
