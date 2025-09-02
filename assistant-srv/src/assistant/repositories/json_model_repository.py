"""
JSON file-based model repository implementation.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, List, Optional

from ..models.model import Model
from .model_repository import ModelRepository


class JsonModelRepository(ModelRepository):
    """JSON file-based model repository."""

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize repository with data directory."""
        self.data_dir = data_dir or "data"
        self.models_file = os.path.join(self.data_dir, "models.json")
        self.keys_file = os.path.join(self.data_dir, "model_keys.json")
        self._models_lock = Lock()
        self._keys_lock = Lock()
        self._ensure_data_dir()
        self._models_cache: Dict[str, Model] = {}
        self._keys_cache: List[Dict[str, Any]] = []
        self._load_models()
        self._load_keys()

    def _ensure_data_dir(self) -> None:
        """Ensure data directory exists."""
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_models(self) -> None:
        """Load models from JSON file."""
        if not os.path.exists(self.models_file):
            self._models_cache = {}
            return

        try:
            with open(self.models_file, "r", encoding="utf-8") as f:
                models_data = json.load(f)

            self._models_cache = {}
            for model_data in models_data:
                model = Model.model_validate(model_data)
                self._models_cache[model.id] = model
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If file is corrupted, start fresh
            self._models_cache = {}
            print(f"Warning: Error loading models file {self.models_file}: {e}")

    def _save_models(self) -> None:
        """Save models to JSON file."""
        models_data = [model.model_dump() for model in self._models_cache.values()]

        with open(self.models_file, "w", encoding="utf-8") as f:
            json.dump(models_data, f, indent=2, ensure_ascii=False)

    def _load_keys(self) -> None:
        """Load API keys from JSON file."""
        if not os.path.exists(self.keys_file):
            self._keys_cache = []
            return

        try:
            with open(self.keys_file, "r", encoding="utf-8") as f:
                self._keys_cache = json.load(f)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If file is corrupted, start fresh
            self._keys_cache = []
            print(f"Warning: Error loading keys file {self.keys_file}: {e}")

    def _save_keys(self) -> None:
        """Save API keys to JSON file."""
        with open(self.keys_file, "w", encoding="utf-8") as f:
            json.dump(self._keys_cache, f, indent=2, ensure_ascii=False)

    async def create(self, entity: Model) -> Model:
        """Create a new model."""
        # Generate a unique ID if not provided or empty
        if not entity.id:
            entity.id = str(uuid.uuid4())

        # Check if model already exists
        if entity.id in self._models_cache:
            raise ValueError(f"Model with ID {entity.id} already exists")

        # Check name uniqueness
        if await self.model_name_exists(entity.owner, entity.name):
            raise ValueError(f"Model name '{entity.name}' already exists " f"for owner '{entity.owner}'")

        # Save to cache and file
        with self._models_lock:
            self._models_cache[entity.id] = entity
            self._save_models()

        return entity

    async def get_by_id(self, entity_id: str) -> Optional[Model]:
        """Get model by ID."""
        return self._models_cache.get(entity_id)

    async def get_all(self) -> List[Model]:
        """Get all models."""
        return list(self._models_cache.values())

    async def update(self, entity: Model) -> Model:
        """Update a model."""
        if entity.id not in self._models_cache:
            raise ValueError(f"Model with ID {entity.id} not found")

        # Check if current model exists and owner matches
        existing_model = self._models_cache[entity.id]
        if existing_model.owner != entity.owner:
            raise ValueError("Owner mismatch - cannot update model")

        # Check name uniqueness if name is being changed
        if entity.name != existing_model.name and await self.model_name_exists(
            entity.owner, entity.name, exclude_id=entity.id
        ):
            raise ValueError(f"Model name '{entity.name}' already exists " f"for owner '{entity.owner}'")

        # Save to cache and file
        with self._models_lock:
            self._models_cache[entity.id] = entity
            self._save_models()

        return entity

    async def delete(self, entity_id: str) -> bool:
        """Delete a model."""
        if entity_id not in self._models_cache:
            return False

        with self._models_lock:
            del self._models_cache[entity_id]
            self._save_models()

        # Also remove any associated API keys
        with self._keys_lock:
            self._keys_cache = [k for k in self._keys_cache if k.get("model_id") != entity_id]
            self._save_keys()

        return True

    async def exists(self, entity_id: str) -> bool:
        """Check if model exists."""
        return entity_id in self._models_cache

    async def list_models_by_owner(self, user_id: str) -> List[Model]:
        """List all models available to the user."""
        return [model for model in self._models_cache.values() if model.owner == user_id]

    async def model_name_exists(self, owner: str, name: str, exclude_id: Optional[str] = None) -> bool:
        """Check if a model name exists for an owner."""
        for model in self._models_cache.values():
            if model.owner == owner and model.name == name and (exclude_id is None or model.id != exclude_id):
                return True
        return False

    async def get_api_key(self, user_id: str, model_id: str) -> Optional[str]:
        """Get API key for a specific user and model."""
        for key_data in self._keys_cache:
            if key_data.get("user_id") == user_id and key_data.get("model_id") == model_id:
                return key_data.get("api_key")
        return None

    async def set_api_key(self, user_id: str, model_id: str, api_key: str) -> None:
        """Set API key for a specific user and model."""
        found = False
        for key_data in self._keys_cache:
            if key_data.get("user_id") == user_id and key_data.get("model_id") == model_id:
                key_data["api_key"] = api_key
                key_data["last_used"] = None  # Will be updated when used
                found = True
                break

        if not found:
            self._keys_cache.append(
                {
                    "user_id": user_id,
                    "model_id": model_id,
                    "api_key": api_key,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_used": None,
                }
            )

        with self._keys_lock:
            self._save_keys()

    async def remove_api_key(self, user_id: str, model_id: str) -> None:
        """Remove API key for a specific user and model."""
        with self._keys_lock:
            self._keys_cache = [
                k for k in self._keys_cache if not (k.get("user_id") == user_id and k.get("model_id") == model_id)
            ]
            self._save_keys()
