"""
Model management API endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from ..models.model import Model
from ..models.api.model_api import (
    ModelDeleteResponseData, ModelRequestData, ModelResponseData
)
from ..services.model_service import ModelService
from ..repositories.json_model_repository import JsonModelRepository
from ..utils.auth import get_current_active_user, CurrentUser
from ..utils.permissions import require_owner_or_admin


# Dependency injection
def get_model_service() -> ModelService:
    """Get model service instance."""
    model_repository = JsonModelRepository()
    return ModelService(model_repository)


router = APIRouter(prefix="/models", tags=["models"])


@router.get("/{model_id}", response_model=ModelResponseData)
@require_owner_or_admin
async def get_model(
    model_id: str,
    current_user: CurrentUser = Depends(get_current_active_user),
    model_service: ModelService = Depends(get_model_service)
) -> ModelResponseData:
    """Get model details: user sees own+system, admin sees only system."""
    user_id = current_user.id
    role = current_user.role.value
    model = await model_service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    if role == "admin":
        if model.owner != "system":
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        if model.owner not in ("system", user_id):
            raise HTTPException(status_code=403, detail="Forbidden")
    return ModelResponseData.from_model(model)


@router.get("/", response_model=List[ModelResponseData])
@require_owner_or_admin
async def list_models(
    current_user: CurrentUser = Depends(get_current_active_user),
    model_service: ModelService = Depends(get_model_service)
) -> List[ModelResponseData]:
    """List models: user sees own+system, admin sees only system."""
    user_id = current_user.id
    role = current_user.role.value
    if role == "admin":
        models = await model_service.list_models("system")
    else:
        models = await model_service.list_models(user_id)
    return [ModelResponseData.from_model(m) for m in models]


@router.post("/", response_model=ModelResponseData)
@require_owner_or_admin
async def add_model(
    model_data: ModelRequestData,
    current_user: CurrentUser = Depends(get_current_active_user),
    model_service: ModelService = Depends(get_model_service)
) -> ModelResponseData:
    """Add model: admin adds system model, user adds own model."""
    user_id = current_user.id
    role = current_user.role.value
    owner = "system" if role == "admin" else user_id
    try:
        model = await model_service.add_model(
            Model.from_dict({**model_data.dict(), "owner": owner})
        )
        return ModelResponseData.from_model(model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{model_id}", response_model=ModelResponseData)
@require_owner_or_admin
async def update_model(
    model_id: str,
    updates: ModelRequestData,
    current_user: CurrentUser = Depends(get_current_active_user),
    model_service: ModelService = Depends(get_model_service)
) -> ModelResponseData:
    """Update model: admin can only update system model, user only own."""
    user_id = current_user.id
    role = current_user.role.value
    owner = "system" if role == "admin" else user_id
    
    try:
        # Get existing model first
        existing_model = await model_service.get_model(model_id)
        if not existing_model or existing_model.owner != owner:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Apply updates to the existing model
        update_dict = updates.dict(exclude_unset=True)
        
        # Create updated model by copying existing and applying changes
        updated_model = Model(
            id=existing_model.id,
            name=update_dict.get("name", existing_model.name),
            type=update_dict.get("model_type", existing_model.type),
            description=update_dict.get(
                "description", existing_model.description
            ),
            default_params=update_dict.get(
                "default_params", existing_model.default_params
            ),
            owner=existing_model.owner,  # Owner cannot be changed
            api_key=update_dict.get("api_key", existing_model.api_key),
            extra=update_dict.get("extra", existing_model.extra),
        )
        
        model = await model_service.update_model(updated_model)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return ModelResponseData.from_model(model)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Forbidden")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{model_id}")
@require_owner_or_admin
async def delete_model(
    model_id: str,
    current_user: CurrentUser = Depends(get_current_active_user),
    model_service: ModelService = Depends(get_model_service)
) -> ModelDeleteResponseData:
    """Delete model: admin can only delete system model, user only own."""
    user_id = current_user.id
    role = current_user.role.value
    owner = "system" if role == "admin" else user_id
    try:
        success = await model_service.delete_model(model_id, owner)
        if not success:
            raise HTTPException(status_code=404, detail="Model not found")
        return ModelDeleteResponseData()
    except PermissionError:
        raise HTTPException(status_code=403, detail="Forbidden")
