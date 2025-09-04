"""
Unit tests for base tools module.

This module contains tests for:
- ToolResult class and its methods
"""

from assistant.llm.tools.base import ToolResult


class TestToolResult:
    """Test cases for ToolResult class."""

    def test_success_creation(self) -> None:
        """Test creating a successful ToolResult."""
        data = {"key": "value"}
        result = ToolResult.success(data)
        assert result.status == "success"
        assert result.data == data
        assert result.error is None

    def test_failure_creation(self) -> None:
        """Test creating a failure ToolResult."""
        error_msg = "An error occurred"
        result = ToolResult.failure(error_msg)
        assert result.status == "error"
        assert result.data == {}
        assert result.error == error_msg

    def test_manual_creation_success(self) -> None:
        """Test manually creating a success result."""
        result = ToolResult(status="success", data={"test": "data"})
        assert result.status == "success"
        assert result.data == {"test": "data"}
        assert result.error is None

    def test_manual_creation_error(self) -> None:
        """Test manually creating an error result."""
        result = ToolResult(status="error", data={}, error="Test error")
        assert result.status == "error"
        assert result.data == {}
        assert result.error == "Test error"
