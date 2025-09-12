"""
Unit tests for tool_retriever module.

This module contains tests for:
- get_tools_retriver function
- retrieve_tools tool functionality
- Error handling and edge cases
"""

from typing import List

import pytest
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from assistant.core import config
from assistant.llm.chat_model_factory import get_chat_model
from assistant.llm.tools import get_tool_names
from assistant.llm.tools.tool_retriever import get_tools_retriver
from assistant.models.model import ModelParams, ProviderInfo


class TestRetrieveToolsFunction:
    """Test cases for the retrieve_tools function returned by get_tools_retriver."""

    @pytest.mark.asyncio
    async def test_retrieve_tools(self) -> None:

        thread_config = RunnableConfig()
        thread_config["configurable"] = {"thread_id": "thread-0002", "checkpoint_ns": "demo"}

        provider_info = ProviderInfo(
            model="moonshotai/kimi-k2:free",
            api_type="openai_compatible",
            base_url="https://openrouter.ai/api/v1",
            api_key=config.openrouter_api_key,
        )

        retrieve_tool = get_tools_retriver(
            provider_info, ModelParams(max_tokens=1024 * 16), set(get_tool_names()), thread_config
        )

        model = get_chat_model(
            provider_info=provider_info,
            model_params=ModelParams(max_tokens=1024 * 16),
        ).bind_tools([retrieve_tool])

        input_messages: List[BaseMessage] = [HumanMessage("What time is it now in New York?")]

        response = model.invoke(input_messages, config=thread_config)

        assert isinstance(response, AIMessage)

        # 演示如何执行 retrieve_tools 工具调用
        if response.tool_calls:
            tool_call = response.tool_calls[0]
            print(f"Tool call: {tool_call['name']}")
            print(f"Args: {tool_call['args']}")

            # 执行工具调用
            tool_result = await retrieve_tool.ainvoke(tool_call["args"], config=thread_config)
            print(f"Tool result: {tool_result}")

            # 创建 ToolMessage 来传递结果
            tool_message = ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])

            # 将工具结果添加到对话历史中
            input_messages.extend([response, tool_message])

            # 继续对话，让模型处理工具结果
            final_response = model.invoke(input_messages, config=thread_config)
            print(f"Final response: {final_response.content}")
