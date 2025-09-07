"""
ChatAgent: 用于响应 API 客户端对话请求的智能体类。
- 构造函数通过模型工厂创建 model 对象，并基于 model 创建 langgraph agent。
- 提供 chat 方法，接收用户消息并返回回复。
"""

from typing import Annotated, Any, Dict, List, Optional, Sequence, Type, TypeVar, Union

from langchain_core.messages import AnyMessage, BaseMessage, HumanMessage, RemoveMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.base import Runnable
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState, AgentStatePydantic
from langgraph.types import Checkpointer
from langmem.short_term.summarization import (
    SummarizationNode,
)
from pydantic import BaseModel

from ..models.model import ModelCapabilities, ModelParams, ProviderInfo
from .chat_model_factory import get_chat_model
from .tools.builtin import get_tools_by_names


class ChatAgentState(AgentState):
    """The state of the agent."""

    summarized_messages: Annotated[Sequence[BaseMessage], add_messages]
    context: Annotated[Dict[str, Any], {}]


class ChatAgentStatePydantic(AgentStatePydantic):
    """The state of the agent."""

    summarized_messages: Annotated[Sequence[BaseMessage], add_messages]
    context: Annotated[Dict[str, Any], {}]


ChatStateSchema = TypeVar("ChatStateSchema", bound=Union[ChatAgentState, ChatAgentStatePydantic])
ChatStateSchemaType = Type[ChatStateSchema]


DEFAULT_INITIAL_SUMMARY_PROMPT_SHORT_VER = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a context manager AI, maintaining a "Key Information Log" for the further conversation.

Execute the task defined in the `<TASK>` tag from the last user message,
create the log with the rest of the following messages. Make it concise.""",
        ),
        ("placeholder", "{messages}"),
        (
            "human",
            """<TASK>Based on the conversation turns above create the log now.

**Instructions**:

- Extract and merge key information & facts.
- New information overwrites old if there is a conflict.
- **CRITICAL**: Facts are important.

</TASK>""",
        ),
    ]
)


DEFAULT_INITIAL_SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a context manager AI, maintaining a "Key Information Log" for the further conversation.

Execute the task defined in the `<TASK>` tag from the last user message,
create the log with the rest of the following messages. Make it concise.""",
        ),
        ("placeholder", "{messages}"),
        (
            "human",
            """<TASK>Based on the conversation turns above create the log now.

**Instructions**:

- Extract and merge key information into the categories defined in `<OUTPUT_FORMAT>`.
- New information overwrites old if there is a conflict.

</TASK>

<OUTPUT_FORMAT>
Strictly use this Markdown format. For empty categories, write "N/A".

## Key Entities & Facts

*   Named entities (people, projects, identities, etc.) & confirmed facts.

## Goals & Intent

*   User's main goals, active tasks, and key questions.

## Constraints & Preferences

*   Restrictions, requirements, likes, and dislikes.

## Key Insights & Conclusions

*   Important conclusions, solutions, or ideas reached.

## Conversation State

*   A brief summary of the last few messages for context.

</OUTPUT_FORMAT>""",
        ),
    ]
)


DEFAULT_EXISTING_SUMMARY_PROMPT_SHORT_VER = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a context manager AI, maintaining a "Key Information Log" for the further conversation.

Execute the task defined in the `<TASK>` tag from the last user message,
update the log with the rest of the following messages. Make it concise.""",
        ),
        (
            "human",
            """<EXISTING_LOG>
{existing_summary}
</EXISTING_LOG>""",
        ),
        ("placeholder", "{messages}"),
        (
            "human",
            """<TASK>
Based on the provided log in the '<EXISTING_LOG>' and the new conversation turns above (after the `<EXISTING_LOG>`),
update the log now.

**Instructions**:

- Extract and merge key information & facts.
- New information overwrites old if there is a conflict.
- **CRITICAL**: Facts are important.

</TASK>""",
        ),
    ]
)


DEFAULT_EXISTING_SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a context manager AI, maintaining a "Key Information Log" for the further conversation.

Execute the task defined in the `<TASK>` tag from the last user message,
update the log with the rest of the following messages. Make it concise.""",
        ),
        (
            "human",
            """<EXISTING_LOG>
{existing_summary}
</EXISTING_LOG>""",
        ),
        ("placeholder", "{messages}"),
        (
            "human",
            """<TASK>
Based on the provided log in the '<EXISTING_LOG>' and the new conversation turns above (after the `<EXISTING_LOG>`),
update the log now.

**Instructions**:

- Extract and merge key information into the categories defined in `<OUTPUT_FORMAT>`.
- New information overwrites old if there is a conflict.
- **CRITICAL**: Never delete existing log entries unless explicitly instructed by the user.

</TASK>

<OUTPUT_FORMAT>
Strictly use this Markdown format. For empty categories, write "N/A".

## Key Entities & Facts

*   Named entities (people, projects, identities, etc.) & confirmed facts.

## Goals & Intent

*   User's main goals, active tasks, and key questions.

## Constraints & Preferences

*   Restrictions, requirements, likes, and dislikes.

## Key Insights & Conclusions

*   Important conclusions, solutions, or ideas reached.

## Conversation State

*   A brief summary of the last few messages for context.

</OUTPUT_FORMAT>""",
        ),
    ]
)


DEFAULT_FINAL_SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        # if exists
        ("placeholder", "{system_message}"),
        (
            "system",
            """Your are a helpful and perspicacious assistant.
Use the information in `<CONVERSACTION_SUMMARY>` as the background to assist the user.

<CONVERSACTION_SUMMARY>
{summary}
</CONVERSACTION_SUMMARY>""",
        ),
        ("placeholder", "{messages}"),
    ]
)


DEFAULT_FINAL_SUMMARY_PROMPT_WITH_USER_INSTRUCTIONS = ChatPromptTemplate.from_messages(
    [
        # if exists
        ("placeholder", "{system_message}"),
        (
            "system",
            """Use the information in `<CONVERSACTION_SUMMARY>` as the background,
and follow the user's instructions in `<USER_INSTRUCTIONS>` to assist the user.

<USER_INSTRUCTIONS>
{user_instructions}
</USER_INSTRUCTIONS>

<CONVERSACTION_SUMMARY>
{summary}
</CONVERSACTION_SUMMARY>""",
        ),
        ("placeholder", "{messages}"),
    ]
)


class SummarizationNodeWrapper(Runnable[Any, Any]):

    def __init__(
        self,
        summarization_node: SummarizationNode,
        user_instructions: Optional[str] = None,
        max_summarization_times: Optional[int] = None,
        keep_last_messages_at_least: Optional[int] = None,
    ) -> None:

        self._summarization_node = summarization_node
        self._summarization_node.func = self._func
        self._summarization_node.afunc = self._afunc
        self._max_summarization_times = max_summarization_times
        self._keep_last_messages_at_least = keep_last_messages_at_least
        self._user_instructions = user_instructions.strip() if user_instructions else None

        self._summarization_node.initial_summary_prompt = DEFAULT_INITIAL_SUMMARY_PROMPT
        self._summarization_node.existing_summary_prompt = DEFAULT_EXISTING_SUMMARY_PROMPT
        self._summarization_node.final_prompt = (
            DEFAULT_FINAL_SUMMARY_PROMPT_WITH_USER_INSTRUCTIONS.partial(user_instructions=self._user_instructions)
            if self._user_instructions
            else DEFAULT_FINAL_SUMMARY_PROMPT
        )

    def invoke(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Any:

        return self._summarization_node.invoke(input, config=config, **kwargs)

    async def ainvoke(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Any:

        return await self._summarization_node.ainvoke(input, config=config, **kwargs)

    def _update_state_with_summarized_messages(
        self, state_update: dict[str, Any], messages: List[AnyMessage], last_user_messages: List[AnyMessage]
    ) -> dict[str, Any]:

        if "context" in state_update and "running_summary" in state_update["context"]:

            summarized_message_ids = state_update["context"]["running_summary"].summarized_message_ids
            summarized_messages = [msg for msg in messages if msg.id in summarized_message_ids]
            state_update["summarized_messages"] = summarized_messages

        if len(last_user_messages) > 0:
            output_messages = state_update[self._summarization_node.output_messages_key]
            state_update[self._summarization_node.output_messages_key] = output_messages + last_user_messages

        return state_update

    def _remove_last_messages(self, messages: List[AnyMessage]) -> List[AnyMessage]:
        """
        Excludes the last human messages from the list. The summarization could be affected by these messages,
        or the information in those messages could be lost in the summary.
        """
        last_messages: List[AnyMessage] = []
        count_to_keep_at_least = self._keep_last_messages_at_least or 0
        for i in reversed(range(len(messages))):
            if isinstance(messages[i], HumanMessage) or len(last_messages) < count_to_keep_at_least:
                last_messages.append(messages[i])
                del messages[i]
            else:
                break
        last_messages.reverse()
        return last_messages

    def _remove_system_message(self, messages: List[AnyMessage], context: Dict[str, Any]) -> Optional[SystemMessage]:
        """
        Excludes the system message from the list. The summarization could be affected by these messages.
        """
        if len(messages) > 0 and isinstance(messages[0], SystemMessage):
            system_message = messages[0]
            messages.pop(0)
            return system_message
        return None

    def _is_over_summarization_limit_times(self, context: Dict[str, Any]) -> bool:

        if self._max_summarization_times is None:
            return False
        elif self._max_summarization_times > 0:
            return "summarized_times" in context and context["summarized_times"] >= self._max_summarization_times
        else:
            return True

    def _add_user_instructions_if_needed(
        self, state: dict[str, Any], original_messages: List[AnyMessage], system_message: Optional[SystemMessage]
    ) -> dict[str, Any]:

        if self._user_instructions:
            user_instructions = self._user_instructions
            messages = state[self._summarization_node.output_messages_key]
            if len(user_instructions) > 0 and len(messages) > 0:
                if not isinstance(messages[0], SystemMessage) and not isinstance(messages[0], RemoveMessage):
                    messages.insert(
                        0, (system_message if system_message is not None else SystemMessage(content=user_instructions))
                    )

            # add the system message back to the original messages,
            # only when there is no new system message created.
            # if don't add it back, the system message added to the state, and will be treated as a new message.
            if system_message is not None and (len(messages) == 0 or system_message.id != messages[0].id):
                original_messages.insert(0, system_message)

        return state

    def _func(self, input: dict[str, Any] | BaseModel) -> dict[str, Any]:

        original_messages, context = self._summarization_node._parse_input(input)
        system_message: Optional[SystemMessage] = None
        if self._is_over_summarization_limit_times(context):  # in case losing too many details in the summarization
            state = {self._summarization_node.output_messages_key: original_messages}
        else:
            last_messages = self._remove_last_messages(original_messages)
            system_message = self._remove_system_message(original_messages, context)
            if len(original_messages) > 1:
                # if only one message in the list, it could be a SystemMessage,
                # so only consider the case that is more than one messages
                state = self._summarization_node._func(input)
                state = self._update_state_with_summarized_messages(state, original_messages, last_messages)
            else:
                # If there are no messages left, or just a SystemMessage, skip the summarization
                state = {self._summarization_node.output_messages_key: original_messages + last_messages}

        return self._add_user_instructions_if_needed(state, original_messages, system_message)

    async def _afunc(self, input: dict[str, Any] | BaseModel) -> dict[str, Any]:

        original_messages, context = self._summarization_node._parse_input(input)
        system_message: Optional[SystemMessage] = None
        if self._is_over_summarization_limit_times(context):  # in case losing too many details in the summarization
            state = {self._summarization_node.output_messages_key: original_messages}
        else:
            last_messages = self._remove_last_messages(original_messages)
            system_message = self._remove_system_message(original_messages, context)
            if len(original_messages) > 1:
                # if only one message in the list, it could be a SystemMessage,
                # so only consider the case that is more than one messages
                state = await self._summarization_node._afunc(input)
                state = self._update_state_with_summarized_messages(state, original_messages, last_messages)
            else:
                # If there are no messages left, or just a SystemMessage, skip the summarization
                state = {self._summarization_node.output_messages_key: original_messages + last_messages}

        return self._add_user_instructions_if_needed(state, original_messages, system_message)

    @staticmethod
    def create(
        model_provider_for_summarization: ProviderInfo,
        model_params_for_summarization: ModelParams,
        model_capabilities_for_summarization: ModelCapabilities,
        model_context_window_to_summarize: int,
        max_summarization_times: Optional[int] = None,
        keep_last_messages_at_least: Optional[int] = None,
        user_instructions: Optional[str] = None,
    ) -> "SummarizationNodeWrapper":

        max_tokens = int(
            min(model_context_window_to_summarize, model_capabilities_for_summarization.context_window) * 0.8
        )
        # max_tokens_before_summary must be less than max_tokens to avoid any messages won't be summarized
        max_tokens_before_summary = int(max_tokens * 0.8)
        max_summary_tokens = int(min(max_tokens_before_summary / 3, model_params_for_summarization.max_tokens / 2))

        summarization_node_model_params = model_params_for_summarization.model_copy(update={"temperature": 0.0})

        model = get_chat_model(
            provider_info=model_provider_for_summarization, model_params=summarization_node_model_params
        )

        summarization_node = SummarizationNode(
            model=model,
            max_tokens=max_tokens,
            max_tokens_before_summary=max_tokens_before_summary,
            max_summary_tokens=max_summary_tokens,
            output_messages_key="messages",
        )

        return SummarizationNodeWrapper(
            summarization_node,
            max_summarization_times=max_summarization_times,
            keep_last_messages_at_least=keep_last_messages_at_least,
            user_instructions=user_instructions,
        )


class ChatAgent:

    def __init__(
        self,
        provider_info: ProviderInfo,
        model_params: ModelParams,
        model_capabilities: ModelCapabilities,
        tools: Optional[List[str]] = None,
        checkpointer: Optional[Checkpointer] = None,
        max_summarization_times: Optional[int] = None,
        model_info_for_summarization: Optional[tuple[ProviderInfo, ModelParams, ModelCapabilities]] = None,
        user_instructions: Optional[str] = None,
    ):

        self._provider_info = provider_info
        self._model_params = model_params
        self._model_capabilities = model_capabilities
        self._tools = get_tools_by_names(tools) if tools else []
        self._checkpointer = checkpointer or InMemorySaver()

        def retrieve_model(state: ChatAgentState, context: Any) -> Any:
            return get_chat_model(provider_info=provider_info, model_params=model_params)

        model_provider_for_summarization = (
            model_info_for_summarization[0] if model_info_for_summarization else provider_info
        )
        model_params_for_summarization = (
            model_info_for_summarization[1] if model_info_for_summarization else model_params
        )
        model_capabilities_for_summarization = (
            model_info_for_summarization[2] if model_info_for_summarization else model_capabilities
        )
        self.agent = create_react_agent(
            model=retrieve_model,
            tools=self._tools,
            pre_model_hook=SummarizationNodeWrapper.create(
                model_provider_for_summarization=model_provider_for_summarization,
                model_params_for_summarization=model_params_for_summarization,
                model_capabilities_for_summarization=model_capabilities_for_summarization,
                model_context_window_to_summarize=model_capabilities.context_window,
                max_summarization_times=max_summarization_times,
                user_instructions=user_instructions,
            ),
            checkpointer=self._checkpointer,
            state_schema=ChatAgentState,
        )
