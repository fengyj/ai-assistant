"""
User data models and enums.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from uuid import uuid4


class UserRole(Enum):
    """User role enumeration."""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserStatus(Enum):
    """User status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class OAuthProvider(Enum):
    """OAuth provider enumeration."""

    GOOGLE = "google"
    MICROSOFT = "microsoft"
    APPLE = "apple"


@dataclass
class UserProfile:
    """User profile information."""

    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: str = "en"
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OAuthInfo:
    """OAuth information."""

    provider: OAuthProvider
    provider_id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass
class UsageStats:
    """User usage statistics."""

    model_api_usage: List["ModelAPIUsage"] = field(default_factory=list)
    last_activity: Optional[datetime] = None
    total_sessions: int = 0
    created_prompts: int = 0
    uploaded_files: int = 0


@dataclass
class ModelAPIUsage:
    """LLM usage information."""

    name: str = ""
    tokens_consumed: int = 0
    api_calls_count: int = 0
    last_used: Optional[datetime] = None


@dataclass
class User:
    """User model."""

    # Basic information
    id: str = field(default_factory=lambda: str(uuid4()))
    username: str = ""
    email: str = ""
    password_hash: Optional[str] = None

    # Profile
    profile: UserProfile = field(default_factory=UserProfile)

    # OAuth information
    oauth_info: List[OAuthInfo] = field(default_factory=list)

    # Role and permissions
    role: UserRole = UserRole.USER
    permissions: List[str] = field(default_factory=list)

    # Status
    status: UserStatus = UserStatus.ACTIVE

    # Usage statistics
    usage_stats: UsageStats = field(default_factory=UsageStats)

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    last_login: Optional[datetime] = None

    # Quota and limits (for future enhancement)
    quota_limits: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "profile": {
                "display_name": self.profile.display_name,
                "avatar_url": self.profile.avatar_url,
                "bio": self.profile.bio,
                "timezone": self.profile.timezone,
                "language": self.profile.language,
                "preferences": self.profile.preferences,
            },
            "oauth_info": [
                {
                    "provider": oauth.provider.value,
                    "provider_id": oauth.provider_id,
                    "email": oauth.email,
                    "name": oauth.name,
                    "avatar_url": oauth.avatar_url,
                }
                for oauth in self.oauth_info
            ],
            "role": self.role.value,
            "permissions": self.permissions,
            "status": self.status.value,
            "usage_stats": {
                "model_api_usage": [
                    {
                        "name": usage.name,
                        "tokens_consumed": usage.tokens_consumed,
                        "api_calls_count": usage.api_calls_count,
                        "last_used": (
                            usage.last_used.isoformat() if usage.last_used else None
                        ),
                    }
                    for usage in self.usage_stats.model_api_usage
                ],
                "last_activity": (
                    self.usage_stats.last_activity.isoformat()
                    if self.usage_stats.last_activity
                    else None
                ),
                "total_sessions": self.usage_stats.total_sessions,
                "created_prompts": self.usage_stats.created_prompts,
                "uploaded_files": self.usage_stats.uploaded_files,
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "quota_limits": self.quota_limits,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create user from dictionary."""
        profile_data = data.get("profile", {})
        profile = UserProfile(
            display_name=profile_data.get("display_name"),
            avatar_url=profile_data.get("avatar_url"),
            bio=profile_data.get("bio"),
            timezone=profile_data.get("timezone"),
            language=profile_data.get("language", "en"),
            preferences=profile_data.get("preferences", {}),
        )

        oauth_info = []
        for oauth_data in data.get("oauth_info", []):
            oauth_info.append(
                OAuthInfo(
                    provider=OAuthProvider(oauth_data["provider"]),
                    provider_id=oauth_data["provider_id"],
                    email=oauth_data["email"],
                    name=oauth_data.get("name"),
                    avatar_url=oauth_data.get("avatar_url"),
                )
            )

        usage_stats_data = data.get("usage_stats", {})
        usage_stats = UsageStats(
            model_api_usage=[
                ModelAPIUsage(
                    name=usage.get("name", ""),
                    tokens_consumed=usage.get("tokens_consumed", 0),
                    api_calls_count=usage.get("api_calls_count", 0),
                    last_used=(
                        datetime.fromisoformat(usage["last_used"])
                        if usage.get("last_used")
                        else None
                    ),
                )
                for usage in usage_stats_data.get("model_api_usage", [])
            ],
            last_activity=(
                datetime.fromisoformat(usage_stats_data["last_activity"])
                if usage_stats_data.get("last_activity")
                else None
            ),
            total_sessions=usage_stats_data.get("total_sessions", 0),
            created_prompts=usage_stats_data.get("created_prompts", 0),
            uploaded_files=usage_stats_data.get("uploaded_files", 0),
        )

        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            password_hash=data.get("password_hash"),
            profile=profile,
            oauth_info=oauth_info,
            role=UserRole(data.get("role", "user")),
            permissions=data.get("permissions", []),
            status=UserStatus(data.get("status", "active")),
            usage_stats=usage_stats,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            last_login=(
                datetime.fromisoformat(data["last_login"])
                if data.get("last_login")
                else None
            ),
            quota_limits=data.get("quota_limits", {}),
        )


@dataclass
class UserCreateRequest:
    """User creation request."""

    username: str
    email: str
    password: Optional[str] = None
    display_name: Optional[str] = None
    role: UserRole = UserRole.USER
    is_oauth: bool = False  # Flag for OAuth users


@dataclass
class UserUpdateRequest:
    """User update request - basic profile information only."""

    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


@dataclass
class EmailChangeRequest:
    """Email change request - requires verification."""

    new_email: str
    password: str  # Current password for verification


@dataclass
class RoleChangeRequest:
    """Role change request - admin only operation."""

    user_id: str
    new_role: UserRole
    reason: Optional[str] = None  # Reason for role change


@dataclass
class LoginRequest:
    """Login request."""

    username: str
    password: str


@dataclass
class UserResponse:
    """User response (without sensitive data)."""

    id: str
    username: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    status: str
    created_at: str
    last_login: Optional[str]

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        """Create user response from user model."""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.profile.display_name,
            avatar_url=user.profile.avatar_url,
            role=user.role.value,
            status=user.status.value,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None,
        )
