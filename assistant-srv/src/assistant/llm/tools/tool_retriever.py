"""
Tool retriever - A tool proxy agent for intelligent tool selection and parameter generation.

This module solves the token consumption problem caused by having too many tools in model requests
by implementing a tool proxy that dynamically selects and prepares the appropriate tools based on user needs.
"""

from typing import Any, Dict, Optional, Set

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, tool

from ...models.model import ModelParams, ProviderInfo
from ..chat_model_factory import get_chat_model
from .base import ToolResult
from .builtin import get_tools_by_names


def get_tools_retriver(
    provider_info: ProviderInfo,
    model_params: ModelParams,
    enabled_tools: Set[str],
    config: Optional[RunnableConfig] = None,
) -> BaseTool:

    tools_enabled = get_tools_by_names(enabled_tools)

    max_tokens = max(model_params.max_tokens, 4 * 1024)  # in case the max_tokens is too small
    params = ModelParams(temperature=0.0, max_tokens=max_tokens)
    model = get_chat_model(provider_info=provider_info, model_params=params).bind_tools(tools_enabled)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
             You are an expert tool-selection engine.
             Your purpose is to analyze the user's query and the available tools,
             and then create a plan by selecting the appropriate tool(s) to call.

             **Your Decision Process:**

             1. **Analyze the query and tools.** Can you confidently generate one or more tool calls
                with all necessary parameters filled from the provided query?
                - **If YES:** Generate the tool calls. Your own response `content` should be a brief,
                  user-facing confirmation message like "Okay, I will start by..." or can be empty.

             2. **If you CANNOT generate tool calls**, determine the reason:
                - **Reason A: Not enough information.** The user's query requires a tool,
                  but is missing critical information (e.g., "send an email" but no recipient).
                - **Action:** DO NOT generate tool calls. Instead, your response `content` MUST be a single,
                  polite question to the user, asking for the specific missing information.
                - **Reason B: No tools are needed.** The user's query is a simple greeting, a thank you,
                  or a question that can be answered without any tools.
                  - **Action:** DO NOT generate tool calls. Instead, your response `content` MUST be a direct,
                    conversational answer to the user.

             **Output Format:** Your final output will be an AIMessage.
             Populate the `tool_calls` and `content` fields according to your decision.
             """,
            ),
            ("human", "{query}"),
        ]
    )
    retrieval_chain = prompt | model

    @tool("retrieve_tools")
    async def retrieve_tools(query: str) -> Dict[str, Any]:
        """
        A tool proxy agent that intelligently selects and prepares appropriate tools for user requests.

        **PURPOSE:**
        This tool acts as a proxy to solve the token consumption problem in AI model requests. Instead of
        loading all available tools (which consumes excessive tokens), this agent analyzes user needs and
        dynamically selects only the relevant tools, generates the required parameters, and returns
        ready-to-execute function calls.

        **WHEN TO USE:**
        - When the user's request requires external tools or actions that cannot be fulfilled through conversation alone
        - When you need to find the right tool(s) from a large collection without consuming excessive tokens
        - When the user's request involves: data retrieval, file operations, API calls, computations, etc.

        **DO NOT USE FOR:**
        - Simple greetings, thanks, or casual conversation
        - Questions that can be answered directly without external tools
        - Meta-questions about the assistant itself

        **QUERY PARAMETER GUIDELINES:**
        The 'query' parameter is CRITICAL for success. It must be comprehensive and well-structured:

        Structure your query as:
        ```
        User Request: [Exact user request]
        Context: [Relevant conversation history and data]
        Additional Info: [Any other relevant details]
        ```

        Essential context to include:
        - Summary of recent conversation turns
        - Results from previous tool calls (file content, search results, etc.)
        - User preferences, settings, or constraints mentioned
        - Key entities, facts, or data points from the conversation
        - Any relevant file paths, URLs, or identifiers

        **EXAMPLE QUERIES:**
        Good query:
        ```
        User Request: Create a summary of the sales data
        Context: User uploaded a CSV file 'sales_2024.csv' containing monthly sales figures.
        Previous conversation showed they want quarterly breakdowns with trend analysis.
        File location: /documents/sales_2024.csv
        ```

        Poor query:
        ```
        Create a summary
        ```

        Args:
            query (str): A comprehensive description containing both the user's specific request
                        and all relevant contextual information from the conversation.

        Returns:
            Dictionary containing tools retrieved results:
            - 'status': (string) Operation status ('success' or 'error')
            - 'data': (dict) Result data containing:
              - 'id': (string) The unique ID of the response message
              - 'response_metadata': (dict) Metadata about the response from the model
              - 'usage_metadata': (dict) Metadata about token usage for this response
              - 'content': (str or list of str) A natural language message for the user, explaining the plan.
              - 'tool_calls': (list of dicts) function calls. **If it's NOT EMPTY**, the plan is ready.
                              The main agent's job is to execute these calls.
                              The 'content' field can be shown to the user as a status update.
                              **If it's EMPTY**, the plan is NOT ready.
                              The 'content' field now contains a direct message for the user (
                              either a clarifying question or a final answer).
                              The main agent's job is to immediately deliver this 'content' to the user.
            - 'error': (string, optional) Error message if fail to retrieve tools
        """

        try:

            response_message = await retrieval_chain.ainvoke({"query": query}, config=config)
            if isinstance(response_message, AIMessage):
                tool_calls_data = [
                    {"name": tc["name"], "args": tc["args"], "id": tc.get("id")} for tc in response_message.tool_calls
                ]
                return ToolResult.success(
                    {
                        "id": response_message.id,
                        "content": response_message.content,
                        "tool_calls": tool_calls_data,
                        "response_metadata": response_message.response_metadata,
                        "usage_metadata": response_message.usage_metadata,
                    }
                ).model_dump()
            else:
                return ToolResult.failure(
                    f"Returned unexpected message. The message is {response_message.text()}"
                ).model_dump()
        except Exception as e:
            return ToolResult.failure(f"Failed to retrieve tool calls. Internal error: {str(e)}").model_dump()

    return retrieve_tools
