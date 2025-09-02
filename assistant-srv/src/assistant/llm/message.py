import json
from typing import Any, Dict, Optional, Type, TypeVar, Union

from langchain_core.messages import AIMessage as LangchainAIMessage
from langchain_core.messages import BaseMessage as LangchainBaseMessage
from langchain_core.messages import HumanMessage as LangchainHumanMessage
from langchain_core.messages import SystemMessage as LangchainSystemMessage

T = TypeVar("T", bound="Message")


class Message:
    """
    通用消息类，支持user、llm、tool calling等类型，封装langchain的message对象，支持json序列化。
    """

    def __init__(
        self,
        content: Union[str, list[Union[str, Dict[str, Any]]]],
        role: str,
        type_: str = "user",
        tool_call: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
    ):
        self.content = content
        self.role = role  # user/assistant/tool/system
        self.type_ = type_  # user/llm/tool/system
        self.tool_call = tool_call
        self.meta = meta or {}

    def to_langchain_message(self) -> LangchainBaseMessage:
        if self.type_ == "user":
            return LangchainHumanMessage(content=self.content, additional_kwargs=self.meta)
        elif self.type_ == "llm":
            return LangchainAIMessage(content=self.content, additional_kwargs=self.meta)
        elif self.type_ == "tool":
            # 工具调用消息转为AIMessage，function_call信息放入additional_kwargs
            meta = dict(self.meta)
            if self.tool_call:
                meta["function_call"] = self.tool_call
            return LangchainAIMessage(content=self.content, additional_kwargs=meta)
        elif self.type_ == "system":
            return LangchainSystemMessage(content=self.content, additional_kwargs=self.meta)
        else:
            raise ValueError(f"Unknown message type: {self.type_}")

    @classmethod
    def from_langchain_message(cls: Type[T], msg: LangchainBaseMessage) -> T:
        # content 可能为str或list
        content = getattr(msg, "content", "")
        meta = getattr(msg, "additional_kwargs", {})
        if isinstance(msg, LangchainHumanMessage):
            return cls(content=content, role="user", type_="user", meta=meta)
        elif isinstance(msg, LangchainAIMessage):
            # 判断是否为工具调用回复
            tool_call = meta.get("function_call")
            if tool_call:
                return cls(content=content, role="tool", type_="tool", tool_call=tool_call, meta=meta)
            return cls(content=content, role="assistant", type_="llm", meta=meta)
        elif isinstance(msg, LangchainSystemMessage):
            return cls(content=content, role="system", type_="system", meta=meta)
        else:
            raise ValueError(f"Unsupported langchain message type: {type(msg)}")

    def to_json(self) -> str:
        return json.dumps(
            {
                "content": self.content,
                "role": self.role,
                "type_": self.type_,
                "tool_call": self.tool_call,
                "meta": self.meta,
            }
        )

    @classmethod
    def from_json(cls: Type[T], data: Union[str, Dict[str, Any]]) -> T:
        if isinstance(data, str):
            data = json.loads(data)
        if not isinstance(data, dict):
            raise ValueError("data must be dict or JSON str")
        return cls(
            content=data.get("content", ""),
            role=data.get("role", "user"),
            type_=data.get("type_", "user"),
            tool_call=data.get("tool_call"),
            meta=data.get("meta", {}),
        )

    def __repr__(self) -> str:
        return f"<Message role={self.role} type={self.type_} " f"content={str(self.content)[:30]!r}...>"
