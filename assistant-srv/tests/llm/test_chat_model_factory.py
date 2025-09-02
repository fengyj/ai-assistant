from assistant.llm.chat_model_factory import get_chat_model
from assistant.models.model import ModelParams, ProviderInfo


def test_get_chat_model_openai() -> None:
    provider_info = ProviderInfo(
        model="gpt-3.5-turbo",
        api_type="openai",
        api_key="fake-openai-key",
    )
    model_params = ModelParams(temperature=0.1, max_tokens=128)

    model = get_chat_model(provider_info=provider_info, model_params=model_params)
    assert model is not None
    assert getattr(model, "model", getattr(model, "model_name", None)) == "gpt-3.5-turbo"


def test_get_chat_model_anthropic() -> None:
    provider_info = ProviderInfo(
        model="claude-3-opus-20240229",
        api_type="anthropic",
        api_key="fake-anthropic-key",
    )
    model_params = ModelParams(temperature=0.1, max_tokens=128, stop=["\n"])

    model = get_chat_model(provider_info=provider_info, model_params=model_params)
    assert model is not None
    assert getattr(model, "model_name", getattr(model, "model", None)) == "claude-3-opus-20240229"


def test_get_chat_model_gemini() -> None:
    provider_info = ProviderInfo(
        model="models/gemini-pro",
        api_type="google_genai",
        api_key="fake-gemini-key",
    )
    model_params = ModelParams(temperature=0.1, max_tokens=128, stop=["\n"])

    model = get_chat_model(provider_info=provider_info, model_params=model_params)
    assert model is not None
    assert getattr(model, "model", getattr(model, "model_name", None)) == "models/gemini-pro"


def test_get_chat_model_ollama() -> None:
    provider_info = ProviderInfo(
        model="llama2",
        api_type="ollama",
    )
    model_params = ModelParams(temperature=0.1, max_tokens=128)

    model = get_chat_model(provider_info=provider_info, model_params=model_params)
    assert model is not None
    assert getattr(model, "model", getattr(model, "model_name", None)) == "llama2"


def test_get_chat_model_openrouter() -> None:
    from assistant.core import config

    provider_info = ProviderInfo(
        model="deepseek/deepseek-chat-v3-0324:free",
        api_type="openai",
        base_url="https://openrouter.ai/api/v1",
        api_key=config.openrouter_api_key,
    )
    model_params = ModelParams(temperature=0.1, max_tokens=128, stop=["\n"])

    model = get_chat_model(provider_info=provider_info, model_params=model_params)
    assert model is not None
    assert getattr(model, "model", getattr(model, "model_name", None)) == "deepseek/deepseek-chat-v3-0324:free"
