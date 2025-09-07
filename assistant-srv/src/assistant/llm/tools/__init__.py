"""
Built-in tools for the assistant.
"""

from .builtin import (
    get_all_builtin_tools,
    get_codecs_tools,
    get_data_structure_tools,
    get_datetime_tools,
    get_math_tools,
    get_random_tools,
    get_text_tools,
    get_tool_descriptions,
    get_tool_names,
    get_tools_by_categories,
    get_tools_by_names,
)
from .codecs import base64_convert, generate_hash, url_convert
from .data_struct import sort_list
from .datetime import (
    add_time_delta,
    convert_timezone,
    date_diff,
    get_country_timezones,
    get_date_info,
    get_holiday_info,
)
from .math import compare_numbers, convert_units, math_calc
from .random import generate_number, generate_password, generate_string, generate_uuid
from .text import change_case, compare_texts, get_statistics, regex_find_and_replace
from .validation import lint_markdown, validate_csv, validate_json, validate_xml

__all__ = [
    # math tools
    "math_calc",
    "convert_units",
    "compare_numbers",
    # text tools
    "get_statistics",
    "change_case",
    "regex_find_and_replace",
    "compare_texts",
    # datetime tools
    "get_date_info",
    "get_country_timezones",
    "convert_timezone",
    "add_time_delta",
    "get_holiday_info",
    "date_diff",
    # codecs tools
    "generate_hash",
    "base64_convert",
    "url_convert",
    # data structure tools
    "sort_list",
    # validation tools
    "validate_json",
    "validate_xml",
    "lint_markdown",
    "validate_csv",
    # random tools
    "generate_number",
    "generate_uuid",
    "generate_password",
    "generate_string",
    # builtin tool collections
    "get_all_builtin_tools",
    "get_math_tools",
    "get_text_tools",
    "get_datetime_tools",
    "get_codecs_tools",
    "get_data_structure_tools",
    "get_random_tools",
    "get_tools_by_categories",
    "get_tool_names",
    "get_tool_descriptions",
    "get_tools_by_names",
]
