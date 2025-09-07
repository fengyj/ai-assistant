"""
Unit tests for builtin tools module.

This module contains tests for:
- get_all_builtin_tools function
"""

from assistant.llm.tools.builtin import get_all_builtin_tools


class TestBuiltinTools:
    """Test cases for builtin tools."""

    def test_get_all_builtin_tools(self) -> None:
        """Test that get_all_builtin_tools returns the correct number of tools."""
        tools = get_all_builtin_tools()
        # According to the docstring, there should be 24 tools
        assert len(tools) == 24
        # Ensure all are BaseTool instances
        from langchain_core.tools import BaseTool

        for tool in tools:
            assert isinstance(tools.get(tool, None), BaseTool)

    def test_get_all_builtin_tools_unique_names(self) -> None:
        """Test that all tools have unique names."""
        tools = get_all_builtin_tools()
        names = [tool for tool in tools]
        assert len(names) == len(set(names)), "Tool names are not unique"
