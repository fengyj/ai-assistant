"""
Model management service for unified model storage and secure key management.
- All models (system/user) stored in models.json, no keys.
- Keys stored in model_keys.json, each record: {user_id, model_id, api_key}
- Service provides CRUD for models and keys, ensures security and separation.
"""

from typing import List, Dict, Optional
from ..models.model import Model
from ..repositories.model_repository import ModelRepository


class ModelService:
    """
    Service for managing models and their secure keys.
    """

    @staticmethod
    def list_models(user_id: str) -> List[Model]:
        """List all models available to the user (system + user)."""
        return ModelRepository.list_models_by_owner(user_id)

    @staticmethod
    def get_model(model_id: str, load_api_key: bool = False) -> Optional[Model]:
        """Get a model by id, optionally loading api_key."""
        model = ModelRepository.get_model_by_id(model_id)
        if model and load_api_key:
            model.api_key = ModelService.get_key(model.owner, model.id)
        elif model:
            model.api_key = None
        return model

    @staticmethod
    def add_model(model: Model) -> Model:
        """Add a new model, ensuring name uniqueness and handling api_key."""
        if ModelRepository.model_name_exists(model.owner, model.name):
            raise ValueError(f"Model name '{model.name}' already exists for owner '{model.owner}'")
        api_key = model.api_key
        model.api_key = None
        ModelRepository.add_model(model)
        if api_key:
            ModelService.set_key(model.owner, model.id, api_key)
        result = ModelRepository.get_model_by_id(model.id)
        if result is None:
            raise RuntimeError("Failed to add model: model not found after save.")
        return result

    @staticmethod
    def update_model(
        model_id: str, updates: Dict, owner: str
    ) -> Optional[Model]:
        """Update a model, enforcing owner and name uniqueness."""
        model = ModelRepository.get_model_by_id(model_id)
        if not model:
            return None
        if model.owner != owner:
            raise PermissionError()
        new_name = updates.get("name")
        if new_name and ModelRepository.model_name_exists(
            owner, new_name, exclude_id=model_id
        ):
            raise ValueError(
                f"Model name '{new_name}' already exists for owner '{owner}'"
            )
        api_key = updates.get("api_key")
        ModelRepository.update_model(model_id, updates)
        if api_key:
            ModelService.set_key(owner, model_id, api_key)
        return ModelRepository.get_model_by_id(model_id)

    @staticmethod
    def delete_model(model_id: str, owner: str) -> bool:
        """Delete a model by id and owner, and remove its api_key."""
        ModelRepository.delete_model(model_id, owner)
        ModelService.delete_key(owner, model_id)
        return True

    # Key management
    @staticmethod
    def get_key(owner: str, model_id: str) -> Optional[str]:
        keys = ModelRepository.load_keys()
        for k in keys:
            if k.get("user_id") == owner and k.get("model_id") == model_id:
                return k.get("api_key")
        return None

    @staticmethod
    def set_key(owner: str, model_id: str, api_key: str) -> None:
        keys = ModelRepository.load_keys()
        found = False
        for k in keys:
            if k.get("user_id") == owner and k.get("model_id") == model_id:
                k["api_key"] = api_key
                found = True
        if not found:
            keys.append({
                "user_id": owner,
                "model_id": model_id,
                "api_key": api_key
            })
        ModelRepository.save_keys(keys)

    @staticmethod
    def delete_key(owner: str, model_id: str) -> None:
        keys = ModelRepository.load_keys()
        keys = [
            k for k in keys
            if not (
                k.get("user_id") == owner and k.get("model_id") == model_id
            )
        ]
        ModelRepository.save_keys(keys)


# TODO: Add unit tests for ModelService
# TODO: Add API endpoints for model and key management
# TODO: Ensure all sensitive key operations are authenticated
# TODO: Document all public methods
