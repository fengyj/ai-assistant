"""
Base classes and types for tool implementations.

This module provides:
1. ToolResult structure for consistent tool outputs
2. Base types and utilities for tool implementations
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """
    Unified tool result structure.

    Provides consistent return format across all tools.
    """

    status: str = Field(description="Operation status: 'success' or 'error'")
    data: dict[str, Any] = Field(description="Result data as dictionary")
    error: Optional[str] = Field(default=None, description="Error message if status is 'error'")

    @classmethod
    def success(cls, data: dict[str, Any]) -> "ToolResult":
        """Create a successful result."""
        return cls(status="success", data={k: v for k, v in data.items() if v is not None}, error=None)

    @classmethod
    def failure(cls, error_msg: str) -> "ToolResult":
        """Create an error result."""
        return cls(status="error", data={}, error=error_msg)
