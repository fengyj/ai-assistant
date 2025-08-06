"""
Model management service for unified model storage and secure key management.
- All models (system/user) stored in models.json, no keys.
- Keys stored in model_keys.json, each record: {user_id, model_id, api_key}
- Service provides CRUD for models and keys, ensures security and separation.
"""

from typing import List, Optional
from ..models.model import Model
from ..repositories.model_repository import ModelRepository


class ModelService:
    """
    Service for managing models and their secure keys.
    """

    def __init__(self, model_repository: ModelRepository):
        """Initialize model service."""
        self.model_repository = model_repository

    async def list_models(self, user_id: str) -> List[Model]:
        """List all models available to the user (system + user)."""
        return await self.model_repository.list_models_by_owner(user_id)

    async def get_model(
        self,
        model_id: str,
        load_api_key: bool = False,
        user_id: Optional[str] = None
    ) -> Optional[Model]:
        """Get a model by id, optionally loading api_key."""
        model = await self.model_repository.get_by_id(model_id)
        if model and load_api_key and user_id:
            model.api_key = await self.model_repository.get_user_api_key(
                user_id, model.id
            )
        elif model:
            model.api_key = None
        return model

    async def add_model(self, model: Model) -> Model:
        """Add a new model, ensuring name uniqueness and handling api_key."""
        if await self.model_repository.model_name_exists(
            model.owner, model.name
        ):
            raise ValueError(
                f"Model name '{model.name}' already exists "
                f"for owner '{model.owner}'"
            )
        
        api_key = model.api_key
        model.api_key = None
        result = await self.model_repository.create(model)
        
        if api_key:
            await self.model_repository.set_user_api_key(
                model.owner, result.id, api_key
            )
        
        return result

    async def update_model(self, model: Model) -> Optional[Model]:
        """Update a model, enforcing owner and name uniqueness."""
        # Check if model exists first
        existing_model = await self.model_repository.get_by_id(model.id)
        if not existing_model:
            return None
        
        # Handle API key separately
        api_key = model.api_key
        model.api_key = None  # Don't store api_key in model data
        
        try:
            # Update the model (this will check name uniqueness)
            updated_model = await self.model_repository.update(model)
            
            # Update API key if provided
            if api_key:
                await self.model_repository.set_user_api_key(
                    model.owner, model.id, api_key
                )
            
            return updated_model
        except ValueError:
            return None

    async def delete_model(self, model_id: str, owner: str) -> bool:
        """Delete a model by id and owner, and remove its api_key."""
        # Check if model exists and belongs to owner
        model = await self.model_repository.get_by_id(model_id)
        if not model or model.owner != owner:
            return False
            
        # Delete the model
        success = await self.model_repository.delete(model_id)
        
        # Remove associated API key
        if success:
            await self.model_repository.remove_user_api_key(owner, model_id)
        
        return success

    # Key management methods
    async def get_key(self, owner: str, model_id: str) -> Optional[str]:
        """Get API key for owner and model."""
        return await self.model_repository.get_user_api_key(owner, model_id)

    async def set_key(self, owner: str, model_id: str, api_key: str) -> None:
        """Set API key for owner and model."""
        await self.model_repository.set_user_api_key(owner, model_id, api_key)

    async def delete_key(self, owner: str, model_id: str) -> None:
        """Delete API key for owner and model."""
        await self.model_repository.remove_user_api_key(owner, model_id)


# TODO: Add unit tests for ModelService
# TODO: Add API endpoints for model and key management
# TODO: Ensure all sensitive key operations are authenticated
# TODO: Document all public methods
