import pytest
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from assistant.core import config
from assistant.llm.chat_agent import ChatAgent
from assistant.models.model import ModelCapabilities, ModelParams, ProviderInfo


@pytest.fixture
def chat_agent() -> ChatAgent:
    provider_info = ProviderInfo(
        model="z-ai/glm-4.5-air:free",
        api_type="openai",
        base_url="https://openrouter.ai/api/v1",
        api_key=config.openrouter_api_key,
    )

    model_params = ModelParams(
        max_tokens=512,
    )

    model_capabilities = ModelCapabilities(
        context_window=1024,
        support_tools=True,
        support_images=False,
        support_structure_output=False,
    )

    return ChatAgent(
        provider_info=provider_info,
        model_params=model_params,
        model_capabilities=model_capabilities,
        user_instructions="Your are a helpful and perspicacious assistant, always happy to answer user's questions.",
    )


def test_chat_agent_initialization(chat_agent: ChatAgent) -> None:
    assert hasattr(chat_agent, "_provider_info")
    assert hasattr(chat_agent, "_model_params")
    assert hasattr(chat_agent, "_model_capabilities")
    assert hasattr(chat_agent, "agent")
    assert chat_agent._model_capabilities.context_window == 1024


def test_summarization(chat_agent: ChatAgent) -> None:

    chat_thread_cfg = RunnableConfig()
    chat_thread_cfg["configurable"] = {"thread_id": "thread-0001", "checkpoint_ns": "demo"}
    response1 = chat_agent.agent.invoke(
        {"messages": [HumanMessage("Hi there! I'm Eric. How's it going?")]}, config=chat_thread_cfg
    )
    response2 = chat_agent.agent.invoke(
        {"messages": [HumanMessage("What can you do for me? What's your strength? Introduce around 150 words.")]},
        config=chat_thread_cfg,
    )
    response3 = chat_agent.agent.invoke(
        {"messages": [HumanMessage("Can you tell me some funny things about cats, and within 150 words?")]},
        config=chat_thread_cfg,
    )
    response4 = chat_agent.agent.invoke(
        {"messages": [HumanMessage("Can you tell me a sad story? At least 6 sentences.")]}, config=chat_thread_cfg
    )
    response5 = chat_agent.agent.invoke(
        {"messages": [HumanMessage("And can you tell me a love story? At least 6 sentences.")]}, config=chat_thread_cfg
    )
    response6 = chat_agent.agent.invoke(
        {"messages": [HumanMessage("Do you know my name? Just reply 'Yes' or 'No', no other characters.")]},
        config=chat_thread_cfg,
    )

    assert (
        response1 is not None
        and response2 is not None
        and response3 is not None
        and response4 is not None
        and response5 is not None
        and response6 is not None
        and response6["messages"][-1].text().strip() == "Yes"
    )
