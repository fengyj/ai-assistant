"""
Unit tests for data_struct tools module.

This module contains tests for:
- sort_list function
"""

from assistant.llm.tools.data_struct import sort_list


class TestSortList:
    """Test cases for sort_list function."""

    def test_sort_ascending_numbers(self) -> None:
        """Test sorting numbers in ascending order."""
        result = sort_list.invoke({"items": [3, 1, 4, 1, 5]})
        assert result["status"] == "success"
        assert result["data"]["sorted_items"] == [1, 1, 3, 4, 5]
        assert result["data"]["order"] == "asc"

    def test_sort_descending_strings(self) -> None:
        """Test sorting strings in descending order."""
        result = sort_list.invoke({"items": ["banana", "apple", "cherry"], "order": "desc"})
        assert result["status"] == "success"
        assert result["data"]["sorted_items"] == ["cherry", "banana", "apple"]
        assert result["data"]["order"] == "desc"

    def test_sort_case_insensitive(self) -> None:
        """Test case-insensitive sorting."""
        result = sort_list.invoke({"items": ["Banana", "apple", "Cherry"], "case_sensitive": False})
        assert result["status"] == "success"
        assert result["data"]["sorted_items"] == ["apple", "Banana", "Cherry"]

    def test_sort_with_duplicates_removal(self) -> None:
        """Test sorting with duplicate removal."""
        result = sort_list.invoke({"items": [3, 1, 4, 1, 5], "remove_duplicates": True})
        assert result["status"] == "success"
        assert result["data"]["sorted_items"] == [1, 3, 4, 5]
        assert result["data"]["sorted_count"] == 4

    def test_sort_empty_list(self) -> None:
        """Test sorting an empty list."""
        result = sort_list.invoke({"items": []})
        assert result["status"] == "success"
        assert result["data"]["sorted_items"] == []
        assert result["data"]["original_count"] == 0

    def test_sort_natural_order(self) -> None:
        """Test natural sorting for strings with numbers."""
        result = sort_list.invoke({"items": ["item10", "item2", "item1"], "natural_sort": True})
        assert result["status"] == "success"
        assert result["data"]["sorted_items"] == ["item1", "item2", "item10"]
