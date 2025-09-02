"""
Model entity definition for LLM model management.
"""

import uuid
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, SecretStr

Model_API_Type = Literal["openai", "google_genai", "openai_compatible", "ollama", "anthropic"]

SYSTEM_OWNER = "system"


# Model related types
class ModelParams(BaseModel):

    temperature: Optional[float] = Field(
        default=None,
        description="控制随机性/创造性。 值越低（如0.0），输出越确定、越具事实性。值越高（如1.0+），输出越随机、越有创造性。",
    )

    max_tokens: int = Field(
        description="控制最大输出长度。 设置模型在停止前最多能生成多少Token。这是控制成本和防止输出过长的最重要参数。"
    )
    """
    For google_gemini, it will be converted to max_output_tokens by adapt_params_for_provider
    """

    top_p: Optional[float] = Field(
        default=None,
        description=(
            "核心采样 (Nucleus Sampling)。一个0.0到1.0之间的值。模型只从累积概率加起来达到top_p的最小词汇集中进行抽样。"
            "是temperature的另一种替代方案，通常不与temperature同时修改。"
        ),
    )

    stop: Optional[List[str]] = Field(
        default=None,
        description="定义停止序列。当模型生成了列表中的任何一个字符串时，它会立即停止。对于控制开源模型的输出格式至关重要。",
    )
    """
    For google_gemini and anthropic, it will be converted to stop_sequences by adapt_params_for_provider
    """

    provider_special_parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Parameters only work in a particular provider"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert ModelParams to dict, flattening provider_special_parameters."""
        data = self.model_dump(exclude={"provider_special_parameters"}, exclude_none=True)
        data.update(self.provider_special_parameters)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelParams":
        """Create ModelParams from dict, extracting provider_special_parameters."""
        # Identify fields belonging to ModelParams except provider_special_parameters
        param_fields = set(cls.model_fields.keys()) - {"provider_special_parameters"}
        base_params = {k: v for k, v in data.items() if k in param_fields}
        special_params = {k: v for k, v in data.items() if k not in param_fields}
        base_params["provider_special_parameters"] = special_params
        return cls(**base_params)


class ModelCapabilities(BaseModel):
    """Model capabilities."""

    context_window: int = Field(description="模型支持的最大上下文长度（单位：tokens）。")
    support_tools: bool = Field(default=True, description="是否支持工具调用。")
    support_images: bool = Field(default=False, description="是否支持图片输入。")
    support_structure_output: bool = Field(default=False, description="是否支持结构化输出。")
    built_in_tools: Dict[str, str] = Field(
        default_factory=dict, description="模型内置的工具列表, key 为工具名称，value 为工具描述。"
    )


class ProviderInfo(BaseModel):
    """Provider information."""

    model: str = Field(description="模型名称或标识符。")
    api_type: Model_API_Type = Field(description="API 类型。")
    base_url: Optional[str] = Field(default=None, description="API 基础 URL。")
    api_key: Optional[str | SecretStr] = Field(default=None, description="API 密钥。")


class Model(BaseModel):

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="模型唯一标识符。")
    name: str = Field(description="模型名称。")
    description: Optional[str] = Field(default=None, description="模型描述。")
    owner: str = Field(default=SYSTEM_OWNER, description="模型所有者。")
    provider: ProviderInfo = Field(description="模型提供商信息。")
    default_params: ModelParams = Field(description="模型默认参数。")
    capabilities: ModelCapabilities = Field(description="模型能力。")

    def is_system_model(self) -> bool:
        """Return if it's a system model."""
        return self.owner == SYSTEM_OWNER
