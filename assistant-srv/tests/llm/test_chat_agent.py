import pytest
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from assistant.core import config
from assistant.llm.chat_agent import ChatAgent
from assistant.llm.chat_model_factory import get_chat_model
from assistant.llm.tools import get_date_info, get_holiday_info, get_tool_names
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
        user_instructions="You are a helpful and perspicacious assistant, always happy to answer user's questions.",
    )


@pytest.fixture
def chat_agent_with_tool() -> ChatAgent:
    provider_info = ProviderInfo(
        model="moonshotai/kimi-k2:free",
        api_type="openai_compatible",
        base_url="https://openrouter.ai/api/v1",
        api_key=config.openrouter_api_key,
    )

    model_params = ModelParams(
        max_tokens=1024 * 16,
    )

    model_capabilities = ModelCapabilities(
        context_window=1024 * 32,
        support_tools=True,
        support_images=False,
        support_structure_output=False,
    )

    return ChatAgent(
        provider_info=provider_info,
        model_params=model_params,
        model_capabilities=model_capabilities,
        tools=get_tool_names(),
        user_instructions="You are a helpful assistant, and able to use tools smartly. "
        "If necessary, you can use the provided tools to assist in answering questions.",
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


def test_chat_agent_with_tool(chat_agent_with_tool: ChatAgent) -> None:
    chat_thread_cfg = RunnableConfig()
    chat_thread_cfg["configurable"] = {"thread_id": "thread-0002", "checkpoint_ns": "demo"}
    response1 = chat_agent_with_tool.agent.invoke(
        {"messages": [HumanMessage("What date is today? And what is the Chinese lunar date today?")]},
        config=chat_thread_cfg,
    )
    response2 = chat_agent_with_tool.agent.invoke(
        {
            "messages": [
                HumanMessage("如果今天是2025年9月1日，距离中秋节还有几天？仅回复数字，比如还有2天，那就回复'2'。")
            ]
        },
        config=chat_thread_cfg,
    )
    response3 = chat_agent_with_tool.agent.invoke(
        {
            "messages": [
                HumanMessage(
                    "Replace the 'a' to 'A' in the sentence below, and add '_' to each word at the beginning. "
                    "Hello world! Hello ai! Hello Gemini!"
                )
            ]
        },
        config=chat_thread_cfg,
    )
    response4 = chat_agent_with_tool.agent.invoke(
        {"messages": [HumanMessage("2000的平方，加上16900的平方根，和4000120比，谁大？仅回复数字，比如12345。")]},
        config=chat_thread_cfg,
    )

    assert response1 is not None and response2 is not None and response3 is not None and response4 is not None
    assert 35 == int(response2["messages"][-1].text().strip())
    assert "_Hello _world! _Hello _Ai! _Hello _Gemini!" in response3["messages"][-1].text()


def test_agent_tool() -> None:

    @tool
    def get_now() -> str:
        """Get the current date and time in ISO format."""
        from datetime import datetime

        return datetime.now().isoformat()

    provider_info = ProviderInfo(
        model="moonshotai/kimi-k2:free",
        api_type="openai_compatible",
        base_url="https://openrouter.ai/api/v1",
        api_key=config.openrouter_api_key,
    )
    # provider_info = ProviderInfo(
    #     model="models/gemini-2.5-flash",
    #     api_type="google_genai",
    #     api_key=config.gemini_api_key,
    # )
    model_params = ModelParams(
        max_tokens=1024 * 16,
    )

    llm = get_chat_model(provider_info=provider_info, model_params=model_params)

    agent = create_react_agent(model=llm, tools=[get_date_info, get_holiday_info])

    chat_thread_cfg = RunnableConfig()
    chat_thread_cfg["configurable"] = {"thread_id": "thread-0003", "checkpoint_ns": "demo"}
    response1 = agent.invoke(
        {"messages": [HumanMessage("What date is today? And what is the Chinese lunar date today?")]},
        config=chat_thread_cfg,
    )
    response2 = agent.invoke(
        {
            "messages": [
                HumanMessage("如果今天是2025年9月1日，距离中秋节还有几天？仅回复数字，比如还有2天，那就回复'2'。")
            ]
        },
        config=chat_thread_cfg,
    )

    assert response1 is not None and response2 is not None
