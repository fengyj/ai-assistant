"""
JSON file-based user repository implementation.
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from ..core import config
from ..core.exceptions import UserNotFoundError, UserAlreadyExistsError
from ..models import User, UserStatus, OAuthProvider
from .user_repository import UserRepository


class JsonUserRepository(UserRepository):
    """JSON file-based user repository."""
    
    def __init__(self, data_dir: str = None):
        """Initialize repository with data directory."""
        self.data_dir = data_dir or config.data_dir
        self.users_file = os.path.join(self.data_dir, config.users_file)
        self._ensure_data_dir()
        self._users_cache: Dict[str, User] = {}
        self._load_users()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists."""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_users(self):
        """Load users from JSON file."""
        if not os.path.exists(self.users_file):
            self._users_cache = {}
            return
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            self._users_cache = {}
            for user_data in users_data:
                user = User.from_dict(user_data)
                self._users_cache[user.id] = user
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If file is corrupted, start fresh
            self._users_cache = {}
            print(f"Warning: Error loading users file {self.users_file}: {e}")
    
    def _save_users(self):
        """Save users to JSON file."""
        users_data = [user.to_dict() for user in self._users_cache.values()]
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
    
    async def create(self, entity: User) -> User:
        """Create a new user."""
        # Check if user already exists
        if entity.id in self._users_cache:
            raise UserAlreadyExistsError(f"User with ID {entity.id} already exists")
        
        # Check username uniqueness
        if await self.get_by_username(entity.username):
            raise UserAlreadyExistsError(f"Username {entity.username} already exists")
        
        # Check email uniqueness
        if await self.get_by_email(entity.email):
            raise UserAlreadyExistsError(f"Email {entity.email} already exists")
        
        # Set timestamps
        entity.created_at = datetime.now(tz=timezone.utc)
        entity.updated_at = datetime.now(tz=timezone.utc)

        # Save to cache and file
        self._users_cache[entity.id] = entity
        self._save_users()
        
        return entity
    
    async def get_by_id(self, entity_id: str) -> Optional[User]:
        """Get user by ID."""
        return self._users_cache.get(entity_id)
    
    async def get_all(self) -> List[User]:
        """Get all users."""
        return list(self._users_cache.values())
    
    async def update(self, entity: User) -> User:
        """Update a user."""
        if entity.id not in self._users_cache:
            raise UserNotFoundError(f"User with ID {entity.id} not found")
        
        # Update timestamp
        entity.updated_at = datetime.now(tz=timezone.utc)
        
        # Save to cache and file
        self._users_cache[entity.id] = entity
        self._save_users()
        
        return entity
    
    async def delete(self, entity_id: str) -> bool:
        """Delete a user."""
        if entity_id not in self._users_cache:
            return False
        
        del self._users_cache[entity_id]
        self._save_users()
        return True
    
    async def exists(self, entity_id: str) -> bool:
        """Check if user exists."""
        return entity_id in self._users_cache
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self._users_cache.values():
            if user.username == username:
                return user
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self._users_cache.values():
            if user.email == email:
                return user
        return None
    
    async def get_by_oauth(self, provider: str, provider_id: str) -> Optional[User]:
        """Get user by OAuth provider and ID."""
        try:
            oauth_provider = OAuthProvider(provider)
        except ValueError:
            return None
        
        for user in self._users_cache.values():
            for oauth_info in user.oauth_info:
                if oauth_info.provider == oauth_provider and oauth_info.provider_id == provider_id:
                    return user
        return None
    
    async def search_users(self, query: str, limit: int = 10) -> List[User]:
        """Search users by query."""
        query_lower = query.lower()
        results = []
        
        for user in self._users_cache.values():
            if (query_lower in user.username.lower() or 
                query_lower in user.email.lower() or
                (user.profile.display_name and query_lower in user.profile.display_name.lower())):
                results.append(user)
                if len(results) >= limit:
                    break
        
        return results
    
    async def get_active_users(self) -> List[User]:
        """Get all active users."""
        return [user for user in self._users_cache.values() if user.status == UserStatus.ACTIVE]
