from typing import Any, Dict, List, Optional, Set

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI as ChatGoogleGenAI
from langchain_ollama import ChatOllama
from langchain_openai.chat_models import ChatOpenAI
from pydantic import SecretStr

from ..models.model import Model_API_Type, ModelCapabilities, ModelParams, ProviderInfo


def _adapt_params_for_openai(params: Dict[str, Any]) -> Dict[str, Any]:
    out = params.copy()
    return out


def _adapt_params_for_openai_compatible(params: Dict[str, Any]) -> Dict[str, Any]:
    out = params.copy()
    return out


def _adapt_params_for_anthropic(params: Dict[str, Any]) -> Dict[str, Any]:
    # stop → stop_sequences
    out = params.copy()
    if "stop" in out:
        out["stop_sequences"] = out.pop("stop")
    return out


def _adapt_params_for_google_genai(params: Dict[str, Any]) -> Dict[str, Any]:
    # max_tokens → max_output_tokens，stop → stop_sequences
    out = params.copy()
    if "max_tokens" in out:
        out["max_output_tokens"] = out.pop("max_tokens")
    if "stop" in out:
        out["stop_sequences"] = out.pop("stop")
    return out


def _adapt_params_for_ollama(params: Dict[str, Any]) -> Dict[str, Any]:
    # Ollama 直接透传
    return params.copy()


def adapt_params_for_provider(model_params: Optional[ModelParams], model_api_type: Model_API_Type) -> Dict[str, Any]:

    params = model_params.to_dict() if model_params else {}

    if model_api_type == "openai":
        return _adapt_params_for_openai(params)
    elif model_api_type == "anthropic":
        return _adapt_params_for_anthropic(params)
    elif model_api_type == "google_genai":
        return _adapt_params_for_google_genai(params)
    elif model_api_type == "ollama":
        return _adapt_params_for_ollama(params)
    elif model_api_type == "openai_compatible":
        return _adapt_params_for_openai_compatible(params)
    else:
        raise ValueError(f"Unsupported model_api_type: {model_api_type}")


def get_chat_model(provider_info: ProviderInfo, model_params: Optional[ModelParams] = None) -> BaseChatModel:
    """
    根据模型 provider 和参数，返回对应的 ChatXX 实例。
    支持 OpenAI、Anthropic、Gemini、Ollama。
    """

    model_api_type = provider_info.api_type
    model_name = provider_info.model
    base_url = provider_info.base_url

    sec_api_key = (
        provider_info.api_key
        if isinstance(provider_info.api_key, SecretStr)
        else SecretStr(provider_info.api_key if provider_info.api_key is not None else "")
    )

    chat_params = adapt_params_for_provider(model_params, model_api_type)

    if model_api_type == "anthropic":
        return ChatAnthropic(model_name=model_name, api_key=sec_api_key, base_url=base_url, **chat_params)
    elif model_api_type == "google_genai":
        return ChatGoogleGenAI(model=model_name, api_key=sec_api_key, **chat_params)
    elif model_api_type == "ollama":
        return ChatOllama(model=model_name, **chat_params)
    elif model_api_type == "openai":
        return ChatOpenAI(model=model_name, api_key=sec_api_key, base_url=base_url, **chat_params)
    elif model_api_type == "openai_compatible":
        return ChatOpenAI(model=model_name, api_key=sec_api_key, base_url=base_url, **chat_params)
    else:
        raise ValueError(f"Unsupported api_type: {model_api_type}")


def get_google_gemini_tools() -> Dict[str, Any]:
    from google.ai.generativelanguage_v1beta.types import Tool as GeminiTools

    return {
        "code_execution": GeminiTools.code_execution,
        "google_search": GeminiTools.google_search,
    }


def get_openai_tools() -> Dict[str, Any]:

    return {
        "code_interpreter": {"type": "code_interpreter"},
        "file_search": {"type": "file_search"},
        "dalle": {"type": "dalle"},
    }


def get_model_built_in_tools(
    provider_info: ProviderInfo, model_capabilities: ModelCapabilities, enabled_list: Set[str]
) -> List[Any]:

    tools = {}
    if provider_info.api_type == "google_genai":
        tools = get_google_gemini_tools()
    elif provider_info.api_type == "openai":
        tools = get_openai_tools()

    return [t for n, t in tools.items() if n in enabled_list]
