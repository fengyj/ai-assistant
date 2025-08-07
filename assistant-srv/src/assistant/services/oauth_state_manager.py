"""
OAuth state management for security and session tracking.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from ..core import config
from ..utils.security import TokenGenerator


@dataclass
class OAuthState:
    """OAuth state information for security."""

    state_token: str
    provider: str
    created_at: datetime
    expires_at: datetime
    redirect_uri: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if state is expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "state_token": self.state_token,
            "provider": self.provider,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "redirect_uri": self.redirect_uri,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OAuthState":
        """Create from dictionary."""
        return cls(
            state_token=data["state_token"],
            provider=data["provider"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            redirect_uri=data["redirect_uri"],
            metadata=data.get("metadata", {}),
        )


class OAuthStateManager:
    """Manages OAuth state tokens for security."""

    def __init__(self, data_dir: Optional[str] = None) -> None:
        """Initialize state manager."""
        self.data_dir = data_dir or config.data_dir
        self.state_file = os.path.join(self.data_dir, "oauth_states.json")
        self._ensure_data_dir()
        self._states_cache: Dict[str, OAuthState] = {}
        self._load_states()

    def _ensure_data_dir(self) -> None:
        """Ensure data directory exists."""
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_states(self) -> None:
        """Load states from JSON file."""
        if not os.path.exists(self.state_file):
            self._states_cache = {}
            return

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                states_data = json.load(f)

            self._states_cache = {}
            for state_data in states_data:
                state = OAuthState.from_dict(state_data)
                # Only load non-expired states
                if not state.is_expired():
                    self._states_cache[state.state_token] = state
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self._states_cache = {}
            print(f"Warning: Error loading OAuth states file: {e}")

    def _save_states(self) -> None:
        """Save states to JSON file."""
        # Filter out expired states before saving
        active_states = [state for state in self._states_cache.values() if not state.is_expired()]

        states_data = [state.to_dict() for state in active_states]

        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(states_data, f, indent=2, ensure_ascii=False)

        # Update cache to only include active states
        self._states_cache = {state.state_token: state for state in active_states}

    def create_state(self, provider: str, redirect_uri: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new OAuth state token."""
        state_token = TokenGenerator.generate_token(32)

        oauth_state = OAuthState(
            state_token=state_token,
            provider=provider,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            redirect_uri=redirect_uri,
            metadata=metadata or {},
        )

        self._states_cache[state_token] = oauth_state
        self._save_states()

        return state_token

    def validate_and_consume_state(self, state_token: str, provider: str) -> Optional[OAuthState]:
        """Validate and consume (remove) a state token."""
        if state_token not in self._states_cache:
            return None

        oauth_state = self._states_cache[state_token]

        # Check if expired
        if oauth_state.is_expired():
            del self._states_cache[state_token]
            self._save_states()
            return None

        # Check if provider matches
        if oauth_state.provider != provider:
            return None

        # Remove state token (consume it)
        del self._states_cache[state_token]
        self._save_states()

        return oauth_state

    def cleanup_expired_states(self) -> int:
        """Clean up expired state tokens."""
        initial_count = len(self._states_cache)

        # Remove expired states
        self._states_cache = {token: state for token, state in self._states_cache.items() if not state.is_expired()}

        self._save_states()

        return initial_count - len(self._states_cache)
