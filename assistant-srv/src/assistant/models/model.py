"""
Model entity definition for LLM model management.
"""

from typing import Any, Dict, List, Optional, TypedDict, Union


# Model related types
class ModelDefaultParams(TypedDict, total=False):
    """Model default parameters with specific types."""

    temperature: float
    max_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    stop: Union[str, List[str]]


class ModelExtraData(TypedDict, total=False):
    """Model extra data with specific fields."""

    provider: str
    version: str
    capabilities: List[str]
    pricing: Dict[str, float]
    context_length: int


class Model:
    """
    Model entity for LLM management. Does not contain sensitive key info.
    """

    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        description: str,
        default_params: ModelDefaultParams,
        owner: str = "system",
        api_key: Optional[str] = None,
        extra: Optional[ModelExtraData] = None,
    ):
        self.id = id or ""
        self.name = name or ""
        self.type = type or ""
        self.description = description or ""
        self.default_params = default_params or {}
        self.owner = owner or "system"
        self.api_key = api_key
        self.extra = extra or {}

    # Static variable for system owner
    SYSTEM_OWNER = "system"

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "default_params": self.default_params,
            "owner": self.owner,
            "api_key": self.api_key,
            **(self.extra or {}),
        }
        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Model":
        # Extract known fields and create extra data from remaining fields
        known_fields = {"id", "name", "type", "description", "default_params", "owner", "api_key"}

        extra_data: ModelExtraData = {}
        for k, v in data.items():
            if k not in known_fields:
                extra_data[k] = v  # type: ignore

        return Model(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            type=str(data.get("type", "")),
            description=str(data.get("description", "")),
            default_params=data.get("default_params", {}),
            owner=str(data.get("owner", "system")),
            api_key=data.get("api_key"),
            extra=extra_data if extra_data else None,
        )

    def is_system_model(self) -> bool:
        """Return if it's a system model."""
        return self.owner == self.SYSTEM_OWNER
