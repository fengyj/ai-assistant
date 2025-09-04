"""
Data structure manipulation tools.

Provides sorting and data manipulation utilities.
"""

import re
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .base import ToolResult

# =============================================================================
# Enums
# =============================================================================


class SortOrder(str, Enum):
    """Sort order options."""

    ASC = "asc"
    DESC = "desc"


# =============================================================================
# Input Parameter Models
# =============================================================================


class SortInput(BaseModel):
    """List sorting parameters."""

    items: List[Union[str, int, float]] = Field(description="List of items to sort")
    order: SortOrder = Field(default=SortOrder.ASC, description="Sort order")
    case_sensitive: bool = Field(default=True, description="Whether to consider case in sorting")
    natural_sort: bool = Field(default=False, description="Use natural sorting for numbers")
    remove_duplicates: bool = Field(default=False, description="Remove duplicate items")


# =============================================================================
# Tool Implementations
# =============================================================================


@tool("local::data.sort_list", args_schema=SortInput)
def sort_list(
    items: List[Union[str, int, float]],
    order: SortOrder = SortOrder.ASC,
    case_sensitive: bool = True,
    natural_sort: bool = False,
    remove_duplicates: bool = False,
) -> Dict[str, Any]:
    """
    Sort a list of items with customizable options.

    Returns:
        Dictionary containing sorting results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'sorted_items': (list) The sorted list of items
          - 'original_count': (integer) Number of items in original list
          - 'sorted_count': (integer) Number of items in sorted list
          - 'order': (string) Sort order applied (asc/desc)
          - 'case_sensitive': (boolean) Whether case sensitivity was used
          - 'natural_sort': (boolean) Whether natural sorting was used
          - 'remove_duplicates': (boolean) Whether duplicates were removed
          - 'changes_made': (boolean) Whether the order was changed
          - 'item_types': (list) Types of items in the list
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        if not items:
            return ToolResult.success(
                {
                    "sorted_items": [],
                    "original_count": 0,
                    "sorted_count": 0,
                    "order": order.value,
                    "case_sensitive": case_sensitive,
                    "natural_sort": natural_sort,
                    "remove_duplicates": remove_duplicates,
                    "changes_made": False,
                    "item_types": [],
                }
            ).model_dump()

        original_count = len(items)
        working_items = items.copy()

        # Get item types for metadata
        item_types = list(set(type(item).__name__ for item in items))

        # Remove duplicates if requested
        if remove_duplicates:
            working_items = list(dict.fromkeys(working_items))  # Preserves order

        # Prepare sort key function
        key_func: Optional[Callable[[Any], Union[int, str, List[Union[int, str]]]]] = None
        if natural_sort:

            def natural_key(text: Any) -> List[Union[int, str]]:
                return [
                    int(s) if s.isdigit() else s.lower() if not case_sensitive else s
                    for s in re.split(r"(\d+)", str(text))
                ]

            key_func = natural_key
        elif not case_sensitive and all(isinstance(item, str) for item in working_items):

            def lowercase_key(x: Any) -> str:
                return str(x).lower()

            key_func = lowercase_key

        # Sort the items
        if key_func is None:
            sorted_items = sorted(working_items, reverse=(order == SortOrder.DESC))
        else:
            sorted_items = sorted(working_items, key=key_func, reverse=(order == SortOrder.DESC))

        # Check if changes were made
        changes_made = sorted_items != items

        return ToolResult.success(
            {
                "sorted_items": sorted_items,
                "original_count": original_count,
                "sorted_count": len(sorted_items),
                "order": order.value,
                "case_sensitive": case_sensitive,
                "natural_sort": natural_sort,
                "remove_duplicates": remove_duplicates,
                "changes_made": changes_made,
                "item_types": sorted(item_types),
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"List sorting failed: {str(e)}").model_dump()
