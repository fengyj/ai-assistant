"""
API request and response models for model management.
"""
from typing import Optional
from pydantic import BaseModel


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
    def from_model(cls, model: object) -> "ModelResponseData":
        return cls(
            id=model.id,
            name=model.name,
            description=getattr(model, 'description', None),
            provider=model.provider,
            model_type=model.model_type,
            owner=model.owner,
            created_at=getattr(model, 'created_at', None),
            updated_at=getattr(model, 'updated_at', None),
        )
