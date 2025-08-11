"""
Session management models and services.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..core.config import config


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
    # IP tracking for security analysis (not for validation)
    initial_ip: Optional[str] = None  # IP address when session was created
    last_known_ips: List[str] = field(default_factory=list)  # Recent IP addresses for analysis


def _default_metadata() -> SessionMetadata:
    """Create default session metadata."""
    return SessionMetadata(
        login_method="password",
        oauth_provider=None,
        device_type="web",
        location=None,
        security_flags=[],
        initial_ip=None,
        last_known_ips=[],
    )


@dataclass
class UserSession:
    """User session model."""

    # Session information
    id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""

    # Session metadata
    # Note: IP address removed - users can legitimately change IP during session lifetime
    # IP tracking should be handled in separate audit logs if needed for security analysis
    user_agent: Optional[str] = None
    device_info: Optional[str] = None

    # Status and timing
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=config.session_expire_hours)
    )

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

    def update_ip_tracking(self, current_ip: Optional[str], max_ips: int = 5) -> None:
        """Update IP tracking for security analysis (not validation)."""
        if not current_ip:
            return

        # Set initial IP if not set
        if not self.metadata.initial_ip:
            self.metadata.initial_ip = current_ip

        # Add to recent IPs if different from last known
        if not self.metadata.last_known_ips or self.metadata.last_known_ips[-1] != current_ip:
            self.metadata.last_known_ips.append(current_ip)

            # Keep only the most recent IPs
            if len(self.metadata.last_known_ips) > max_ips:
                self.metadata.last_known_ips = self.metadata.last_known_ips[-max_ips:]

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            # Note: ip_address removed - users can legitimately change IP during session
            "user_agent": self.user_agent,
            "device_info": self.device_info,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "metadata": {
                "login_method": self.metadata.login_method,
                "oauth_provider": self.metadata.oauth_provider,
                "device_type": self.metadata.device_type,
                "location": self.metadata.location,
                "security_flags": self.metadata.security_flags,
                "initial_ip": self.metadata.initial_ip,
                "last_known_ips": self.metadata.last_known_ips,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSession":
        """Create session from dictionary."""
        metadata_data = data.get("metadata", {})
        metadata = SessionMetadata(
            login_method=metadata_data.get("login_method", "password"),
            oauth_provider=metadata_data.get("oauth_provider"),
            device_type=metadata_data.get("device_type", "web"),
            location=metadata_data.get("location"),
            security_flags=metadata_data.get("security_flags", []),
            initial_ip=metadata_data.get("initial_ip"),
            last_known_ips=metadata_data.get("last_known_ips", []),
        )

        return cls(
            id=data["id"],
            user_id=data["user_id"],
            # Note: ip_address removed - users can legitimately change IP during session
            user_agent=data.get("user_agent"),
            device_info=data.get("device_info"),
            status=SessionStatus(data.get("status", "active")),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            metadata=metadata,
        )


@dataclass
class SessionCreateRequest:
    """Session creation request."""

    user_id: str
    user_agent: Optional[str] = None
    device_info: Optional[str] = None
    extend_hours: int = 24
    # IP address for security tracking (not validation)
    initial_ip: Optional[str] = None


@dataclass
class SessionResponse:
    """Session response."""

    id: str
    user_id: str
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
            status=session.status.value,
            created_at=session.created_at.isoformat(),
            last_accessed=session.last_accessed.isoformat(),
            expires_at=session.expires_at.isoformat(),
            device_info=session.device_info,
        )
