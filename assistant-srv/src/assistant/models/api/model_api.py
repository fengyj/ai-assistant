"""
API request and response models for model management.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ..model import Model, Model_API_Type, ModelCapabilities, ModelParams, ProviderInfo


class ProviderInfoData(BaseModel):
    """Provider info data."""

    model: str = Field(description="Model name, e.g., 'gpt-4', 'gpt-3.5-turbo', etc.")
    api_type: Model_API_Type = Field(
        description="API type, supports openai, google_genai, openai_compatible, ollama, anthropic"
    )
    base_url: Optional[str] = Field(default=None, description="Base URL for API endpoint customization")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")


class ModelParamsData(BaseModel):
    """Model parameters data."""

    temperature: Optional[float] = Field(
        default=None,
        description=(
            "Controls randomness/creativity. Lower values (e.g., 0.0) make output more deterministic "
            "and factual. Higher values (e.g., 1.0+) make output more random and creative"
        ),
        ge=0.0,
        le=2.0,
    )
    max_tokens: int = Field(
        description=(
            "Controls maximum output length. Sets the maximum number of tokens the model can generate "
            "before stopping. This is the most important parameter for controlling cost and preventing "
            "overly long outputs"
        ),
        gt=0,
    )
    top_p: Optional[float] = Field(
        default=None,
        description=(
            "Nucleus sampling. A value between 0.0 and 1.0. The model samples only from the smallest "
            "set of words whose cumulative probability adds up to top_p"
        ),
        ge=0.0,
        le=1.0,
    )
    stop: Optional[list[str]] = Field(
        default=None,
        description=(
            "Defines stop sequences. The model will immediately stop when it generates any string from "
            "this list. Critical for controlling output format of open-source models"
        ),
    )

    class Config:
        extra = "allow"

    def extra_fields(self) -> Dict[str, Any]:
        """Return all extra (user-provided) fields as a dict."""
        return {k: v for k, v in self.__dict__.items() if k not in {"temperature", "max_tokens", "top_p", "stop"}}


class ModelCapabilitiesData(BaseModel):
    """Model capabilities request data."""

    context_window: int = Field(
        description=(
            "The context window size of the model, i.e., the maximum number of tokens " "the model can process"
        ),
        gt=0,
    )
    support_tools: bool = Field(default=True, description="Whether the model supports tool calling (Function Calling)")
    support_images: bool = Field(default=False, description="Whether the model supports image input and processing")
    support_structure_output: bool = Field(
        default=False, description="Whether the model supports structured output (JSON Schema)"
    )
    built_in_tools: Dict[str, str] = Field(
        default_factory=dict, description="Built-in tools list, where key is tool name and value is tool description"
    )


class ModelRequestData(BaseModel):
    """Model creation/update request API model."""

    name: str = Field(description="Model display name for UI presentation")
    description: Optional[str] = Field(default=None, description="Model description information")
    provider: ProviderInfoData = Field(description="Model provider information")
    default_params: ModelParamsData = Field(description="Model default parameter configuration")
    capabilities: ModelCapabilitiesData = Field(description="Model capability configuration")

    def to_model(self) -> Model:
        """Convert request data to Model instance."""
        return Model(
            name=self.name,
            description=self.description,
            owner="",
            provider=ProviderInfo(
                model=self.provider.model,
                api_type=self.provider.api_type,
                base_url=self.provider.base_url,
                api_key=self.provider.api_key,
            ),
            default_params=ModelParams(
                temperature=self.default_params.temperature,
                max_tokens=self.default_params.max_tokens,
                top_p=self.default_params.top_p,
                stop=self.default_params.stop,
                provider_special_parameters=self.default_params.extra_fields(),
            ),
            capabilities=ModelCapabilities(
                context_window=self.capabilities.context_window,
                support_tools=self.capabilities.support_tools,
                support_images=self.capabilities.support_images,
                support_structure_output=self.capabilities.support_structure_output,
                built_in_tools=self.capabilities.built_in_tools,
            ),
        )


class ModelResponseData(BaseModel):
    """Model API response data."""

    id: str = Field(description="Unique model identifier")
    name: str = Field(description="Model display name")
    description: Optional[str] = Field(default=None, description="Model description information")
    owner: str = Field(description="Model owner")
    provider: ProviderInfoData = Field(description="Model provider information (API key excluded)")
    default_params: ModelParamsData = Field(description="Model default parameter configuration")
    capabilities: ModelCapabilitiesData = Field(description="Model capability configuration")
    # 不包含api_key

    @classmethod
    def from_model(cls, model: Model) -> "ModelResponseData":
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            owner=model.owner,
            provider=ProviderInfoData(
                model=model.provider.model, api_type=model.provider.api_type, base_url=model.provider.base_url
            ),
            default_params=ModelParamsData(
                temperature=model.default_params.temperature,
                max_tokens=model.default_params.max_tokens,
                top_p=model.default_params.top_p,
                stop=model.default_params.stop,
                **model.default_params.provider_special_parameters,
            ),
            capabilities=ModelCapabilitiesData(
                context_window=model.capabilities.context_window,
                support_tools=model.capabilities.support_tools,
                support_images=model.capabilities.support_images,
                support_structure_output=model.capabilities.support_structure_output,
                built_in_tools=model.capabilities.built_in_tools,
            ),
        )


class ModelDeleteResponseData(BaseModel):
    """Model delete response API model."""

    success: bool = Field(default=True, description="Whether the delete operation was successful")
    message: str = Field(default="Model deleted successfully", description="Result message of the delete operation")
