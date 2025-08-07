"""
API request and response models for model management.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel

from ..model import Model


class ModelCreateRequestData(BaseModel):
    """Model creation request API model."""

    name: str
    description: Optional[str] = None
    provider: str
    model_type: str
    default_params: Dict[str, Any]
    extra: Optional[Dict[str, Any]] = None


class ModelUpdateRequestData(BaseModel):
    """Model update request API model."""

    name: Optional[str] = None
    description: Optional[str] = None
    default_params: Optional[Dict[str, Any]] = None
    extra: Optional[Dict[str, Any]] = None


class ModelRequestData(BaseModel):
    """Model create/update API request data."""

    name: Optional[str] = None
    description: Optional[str] = None
    provider: Optional[str] = None
    model_type: Optional[str] = None
    api_key: Optional[str] = None
    # 其他可选字段按实际模型补充


class ModelResponseData(BaseModel):
    """Model API response data."""

    id: str
    name: str
    description: Optional[str] = None
    provider: str
    model_type: str
    owner: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # 不包含api_key

    @classmethod
    def from_model(cls, model: Model) -> "ModelResponseData":
        extra = model.extra or {}
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            provider=extra.get("provider", ""),
            model_type=model.type,
            owner=model.owner,
            created_at=extra.get("created_at"),
            updated_at=extra.get("updated_at"),
        )


class ModelDeleteResponseData(BaseModel):
    """Model delete response API model."""

    success: bool = True
    message: str = "Model deleted successfully"
