from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from .model import ModelParams


class Artifact:
    def __init__(self, artifact_id: str, content: str, artifact_type: str, language: Optional[str] = None):
        self.artifact_id = artifact_id
        self.content = content
        self.artifact_type = artifact_type
        self.language = language
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at


class ModelUsageMetadata:

    def __init__(
        self,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        model_id: Optional[str] = None,
        model_name: Optional[str] = None,
        model_owner: Optional[str] = None,
    ) -> None:

        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = total_tokens
        self.model_id = model_id
        self.model_name = model_name
        self.model_owner = model_owner


class ModelToolCall(TypedDict):
    """Represents a request to call a tool."""

    call_id: str
    """An identifier associated with the tool call.

    An identifier is needed to associate a tool call request with a tool
    call result in events when multiple concurrent tool calls are made.
    """
    name: str
    """The name of the tool to be called."""
    args: dict[str, Any]
    """The arguments to the tool call."""
    result: Any
    """The result of the tool call, which can be any type."""
    executed_at: Optional[str]
    """The time at which the tool call was executed."""
    duration_ms: Optional[int]
    """The duration of the tool call in milliseconds."""
    status: Optional[Literal["pending", "running", "completed", "failed"]]
    """The status of the tool call."""
    error: Optional[str]
    """An error message associated with the tool call."""


class ModelConfig:
    """
    Configuration for the model used for responding to the user message.
    """

    def __init__(self, model_id: str, model_name: str, model_owner: str, params: Optional[ModelParams]) -> None:
        self.model_id = model_id
        self.model_name = model_name
        self.model_owner = model_owner
        self.params = params


class ChatMessageBlock:

    def __init__(
        self,
        message_block_id: str,
        content: Union[str, list[Union[str, Dict[str, Any]]]],
        tool_calls: Optional[list[ModelToolCall]] = None,
        thinking: Optional[str] = None,
        usage_metadata: Optional[ModelUsageMetadata] = None,
    ) -> None:
        self.message_block_id = message_block_id
        self.content = content
        self.tool_calls = tool_calls
        self.thinking = thinking
        self.usage_metadata = usage_metadata


class ChatMessageMetadata:

    def __init__(self, model_config: Optional[ModelConfig]) -> None:
        self.model_config = model_config
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at


class ChatMessage:

    def __init__(
        self,
        type: Literal["user", "assistant", "system"],
        message_blocks: List[ChatMessageBlock],
        metadata: Optional[ChatMessageMetadata] = None,
    ) -> None:
        self.type = type
        self.message_blocks = message_blocks
        self.metadata = metadata


class ChatThreadMetadata:

    def __init__(
        self,
        user_id: str,
        subject: str = "",
        system_instruction: Optional[str] = None,
    ) -> None:
        self.user_id = user_id
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
        self.subject = subject
        self.system_instruction = system_instruction


class ChatThread:

    def __init__(
        self,
        chat_thread_id: str,
        session_metadata: ChatThreadMetadata,
        messages: list[ChatMessage],
    ) -> None:
        self.chat_thread_id = chat_thread_id
        self.session_metadata = session_metadata
        self.messages = messages
