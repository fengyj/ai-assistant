"""
Model management API endpoints.
"""

from typing import List

from fastapi import APIRouter, Depends

# Import centralized dependencies
from ..core.dependencies import get_model_service
from ..models.api.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from ..models.api.model_api import ModelDeleteResponseData, ModelRequestData, ModelResponseData
from ..services.model_service import ModelService
from ..utils.auth import CurrentUser, get_current_user, get_owner_or_admin

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("/user/{user_id}/{model_id}", response_model=ModelResponseData)
async def get_model(
    user_id: str,
    model_id: str,
    current_user: CurrentUser = Depends(get_owner_or_admin),
    model_service: ModelService = Depends(get_model_service),
) -> ModelResponseData:
    """
    Get model details: user sees own+system, admin sees only system.
    Now delegates user_id logic to service layer.
    """
    role = current_user.role
    model = await model_service.get_model(model_id, user_id, role)
    if not model:
        raise NotFoundException(detail="Model not found")
    return ModelResponseData.from_model(model)


@router.get("/user/{user_id}", response_model=List[ModelResponseData])
async def list_models(
    user_id: str,
    current_user: CurrentUser = Depends(get_owner_or_admin),
    model_service: ModelService = Depends(get_model_service),
) -> List[ModelResponseData]:
    """List models: user sees own+system, admin sees only system."""
    role = current_user.role
    models = await model_service.list_models(user_id, role)
    return [ModelResponseData.from_model(m) for m in models]


@router.post("/", response_model=ModelResponseData)
async def add_model(
    model_data: ModelRequestData,
    current_user: CurrentUser = Depends(get_current_user),
    model_service: ModelService = Depends(get_model_service),
) -> ModelResponseData:
    """Add model: admin adds system model, user adds own model."""
    user_id = current_user.id
    role = current_user.role
    try:
        # Convert request data to Model using built-in method
        model = model_data.to_model()
        model = await model_service.add_model(model, user_id, role)
        return ModelResponseData.from_model(model)
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.patch("/user/{user_id}/{model_id}", response_model=ModelResponseData)
async def update_model(
    user_id: str,
    model_id: str,
    updates: ModelRequestData,
    current_user: CurrentUser = Depends(get_owner_or_admin),
    model_service: ModelService = Depends(get_model_service),
) -> ModelResponseData:
    """Update model: admin can only update system model, user only own."""
    role = current_user.role

    try:
        # Get existing model first
        existing_model = await model_service.get_model(model_id, user_id, role)
        if not existing_model:
            raise NotFoundException(detail="Model not found")

        # Use the built-in update method
        updated_model = updates.to_model()
        updated_model.owner = existing_model.owner
        updated_model.id = existing_model.id
        model = await model_service.update_model(updated_model)
        if not model:
            raise NotFoundException(detail="Model not found")
        return ModelResponseData.from_model(model)
    except PermissionError:
        raise ForbiddenException(detail="Forbidden")
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.delete("/user/{user_id}/{model_id}")
async def delete_model(
    user_id: str,
    model_id: str,
    current_user: CurrentUser = Depends(get_owner_or_admin),
    model_service: ModelService = Depends(get_model_service),
) -> ModelDeleteResponseData:
    """Delete model: admin can only delete system model, user only own."""
    role = current_user.role
    try:
        # Get existing model first
        existing_model = await model_service.get_model(model_id, user_id, role)
        if not existing_model:
            raise NotFoundException(detail="Model not found")

        success = await model_service.delete_model(model_id)
        if not success:
            raise NotFoundException(detail="Model not found")
        return ModelDeleteResponseData()
    except PermissionError:
        raise ForbiddenException(detail="Forbidden")
