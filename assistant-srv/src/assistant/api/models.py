"""
FastAPI endpoints for model management.
- All endpoints require authentication.
- No sensitive key info returned in model APIs.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.api import ModelRequestData, ModelResponseData
from ..services.model_service import ModelService
from ..utils.permissions import require_owner_or_admin
from ..utils.auth import get_current_active_user, CurrentUser
from ..models.model import Model

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/{model_id}", response_model=ModelResponseData)
def get_model(
    model_id: str,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> ModelResponseData:
    """Get model details: user sees own+system, admin sees only system."""
    user_id = current_user.id
    role = current_user.role.value
    model = ModelService.get_model(model_id)
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
def list_models(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> List[ModelResponseData]:
    """List models: user sees own+system, admin sees only system."""
    user_id = current_user.id
    role = current_user.role.value
    if role == "admin":
        models = ModelService.list_models("system")
    else:
        models = ModelService.list_models(user_id)
    return [ModelResponseData.from_model(m) for m in models]


@router.post("/", response_model=ModelResponseData)
def add_model(
    model_data: ModelRequestData,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> ModelResponseData:
    """Add model: admin adds system model, user adds own model."""
    user_id = current_user.id
    role = current_user.role.value
    owner = "system" if role == "admin" else user_id
    try:
        model = ModelService.add_model(
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
    current_user: CurrentUser = Depends(get_current_active_user)
) -> ModelResponseData:
    """Update model: admin can only update system model, user only own."""
    user_id = current_user.id
    role = current_user.role.value
    owner = "system" if role == "admin" else user_id
    try:
        model = ModelService.update_model(
            model_id, updates.dict(exclude_unset=True), owner
        )
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
    current_user: CurrentUser = Depends(get_current_active_user)
) -> dict:
    """Delete model: admin can only delete system model, user only own."""
    user_id = current_user.id
    role = current_user.role.value
    owner = "system" if role == "admin" else user_id
    try:
        success = ModelService.delete_model(model_id, owner)
        if not success:
            raise HTTPException(status_code=404, detail="Model not found")
        return {"success": True}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Forbidden")
