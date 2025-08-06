"""
Model entity definition for LLM model management.
"""

from typing import Dict, Optional


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
        default_params: Dict,
        owner: str = "system",
        api_key: Optional[str] = None,
        extra: Optional[Dict] = None,
    ):
        self.id = id or ""
        self.name = name or ""
        self.type = type or ""
        self.description = description or ""
        self.default_params = default_params or {}
        self.owner = owner or "system"
        self.api_key = api_key
        self.extra = extra or {}

    def to_dict(self) -> Dict:
        d = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "default_params": self.default_params,
            "owner": self.owner,
            "api_key": self.api_key,
            **self.extra,
        }
        return d

    @staticmethod
    def from_dict(data: Dict) -> "Model":
        return Model(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            type=str(data.get("type", "")),
            description=str(data.get("description", "")),
            default_params=data.get("default_params", {}),
            owner=str(data.get("owner", "system")),
            api_key=data.get("api_key"),
            extra={
                k: v
                for k, v in data.items()
                if k
                not in {
                    "id",
                    "name",
                    "type",
                    "description",
                    "default_params",
                    "owner",
                    "api_key",
                }
            },
        )
