"""
Repository for model storage and key management.
Handles CRUD for models and keys, using json files.
"""

import json
import os
from threading import Lock
from typing import List, Dict, Optional
from ..models.model import Model

MODELS_FILE = os.path.join(os.path.dirname(__file__), "../../data/models.json")
KEYS_FILE = os.path.join(
    os.path.dirname(__file__), "../../data/model_keys.json"
)
_models_lock = Lock()
_keys_lock = Lock()


class ModelRepository:
    """Repository for model and key data persistence."""
    
    @staticmethod
    def list_models_by_owner(user_id: str) -> List[Model]:
        """List all models available to the user (system + user)."""
        models = ModelRepository.load_models()
        return [m for m in models if m.owner in ("system", user_id)]

    @staticmethod
    def get_model_by_id(model_id: str) -> Optional[Model]:
        """Get a model by id."""
        models = ModelRepository.load_models()
        for m in models:
            if m.id == model_id:
                return m
        return None

    @staticmethod
    def model_name_exists(
        owner: str, name: str, exclude_id: Optional[str] = None
    ) -> bool:
        """Check if a model name exists for an owner."""
        models = ModelRepository.load_models()
        for m in models:
            if m.owner == owner and m.name == name:
                if exclude_id is None or m.id != exclude_id:
                    return True
        return False

    @staticmethod
    def add_model(model: Model) -> None:
        """Add a new model to storage."""
        models = ModelRepository.load_models()
        models.append(model)
        ModelRepository.save_models(models)

    @staticmethod
    def update_model(model_id: str, updates: Dict) -> None:
        """Update a model by id with given fields."""
        models = ModelRepository.load_models()
        for m in models:
            if m.id == model_id:
                for k, v in updates.items():
                    if hasattr(m, k):
                        setattr(m, k, v)
                    else:
                        if hasattr(m, 'extra') and isinstance(m.extra, dict):
                            m.extra[k] = v
                break
        ModelRepository.save_models(models)

    @staticmethod
    def delete_model(model_id: str, owner: str) -> None:
        """Delete a model by id and owner."""
        models = ModelRepository.load_models()
        models = [
            m for m in models
            if not (m.id == model_id and m.owner == owner)
        ]
        ModelRepository.save_models(models)

    @staticmethod
    def load_models() -> List[Model]:
        """Load all models from storage."""
        with _models_lock:
            if not os.path.exists(MODELS_FILE):
                return []
            with open(MODELS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Model.from_dict(m) for m in data]

    @staticmethod
    def save_models(models: List[Model]) -> None:
        """Save models to storage."""
        with _models_lock:
            with open(MODELS_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    [m.to_dict() for m in models],
                    f,
                    ensure_ascii=False,
                    indent=2
                )

    @staticmethod
    def get_user_api_key(user_id: str, model_id: str) -> Optional[str]:
        """Get API key for a specific user and model."""
        keys = ModelRepository._load_api_keys()
        for key_data in keys:
            if (key_data.get("user_id") == user_id and
                    key_data.get("model_id") == model_id):
                return key_data.get("api_key")
        return None

    @staticmethod
    def set_user_api_key(user_id: str, model_id: str, api_key: str) -> None:
        """Set API key for a specific user and model."""
        keys = ModelRepository._load_api_keys()
        found = False
        for key_data in keys:
            if (key_data.get("user_id") == user_id and
                    key_data.get("model_id") == model_id):
                key_data["api_key"] = api_key
                found = True
                break
        if not found:
            keys.append({
                "user_id": user_id,
                "model_id": model_id,
                "api_key": api_key
            })
        ModelRepository._save_api_keys(keys)

    @staticmethod
    def remove_user_api_key(user_id: str, model_id: str) -> None:
        """Remove API key for a specific user and model."""
        keys = ModelRepository._load_api_keys()
        keys = [
            k for k in keys
            if not (k.get("user_id") == user_id and
                    k.get("model_id") == model_id)
        ]
        ModelRepository._save_api_keys(keys)

    @staticmethod
    def _load_api_keys() -> List[Dict]:
        """Load API keys from storage."""
        with _keys_lock:
            if not os.path.exists(KEYS_FILE):
                return []
            with open(KEYS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

    @staticmethod
    def _save_api_keys(keys: List[Dict]) -> None:
        """Save API keys to storage."""
        with _keys_lock:
            with open(KEYS_FILE, "w", encoding="utf-8") as f:
                json.dump(keys, f, ensure_ascii=False, indent=2)
