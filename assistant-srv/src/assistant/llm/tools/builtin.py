"""
内置工具集合，提供便捷函数来获取不同类别的工具
"""

from functools import cache
from typing import Dict, List, Optional

from langchain_core.tools import BaseTool

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
from .random import generate_number, generate_password, generate_uuid
from .text import change_case, compare_texts, get_statistics, regex_find_and_replace
from .validation import lint_markdown, validate_csv, validate_json, validate_xml


@cache
def get_all_builtin_tools() -> Dict[str, BaseTool]:
    """
    获取所有内置工具，返回以工具名称为 key 的字典

    Returns:
        包含所有22个内置工具的字典，key 为工具名称，value 为工具对象
    """
    tools = [
        # Math tools (3)
        math_calc,
        convert_units,
        compare_numbers,
        # Text tools (4)
        get_statistics,
        change_case,
        regex_find_and_replace,
        compare_texts,
        # DateTime tools (5)
        get_date_info,
        add_time_delta,
        get_country_timezones,
        convert_timezone,
        get_holiday_info,
        date_diff,
        # Codecs tools (3)
        generate_hash,
        base64_convert,
        url_convert,
        # Data structure tools (5)
        sort_list,
        validate_json,
        validate_xml,
        lint_markdown,
        validate_csv,
        # Random tools (3)
        generate_number,
        generate_uuid,
        generate_password,
    ]
    return {tool.name: tool for tool in tools}


def get_math_tools() -> List[BaseTool]:
    """获取数学相关工具"""
    return [
        math_calc,
        convert_units,
        compare_numbers,
    ]


def get_text_tools() -> List[BaseTool]:
    """获取文本处理工具"""
    return [
        get_statistics,
        change_case,
        regex_find_and_replace,
        compare_texts,
    ]


def get_datetime_tools() -> List[BaseTool]:
    """获取日期时间工具"""
    return [
        get_country_timezones,
        add_time_delta,
        get_date_info,
        convert_timezone,
        get_holiday_info,
    ]


def get_codecs_tools() -> List[BaseTool]:
    """获取加密工具"""
    return [
        generate_hash,
        base64_convert,
        url_convert,
    ]


def get_data_structure_tools() -> List[BaseTool]:
    """获取数据结构工具"""
    return [
        sort_list,
        validate_json,
        validate_xml,
        lint_markdown,
        validate_csv,
    ]


def get_random_tools() -> List[BaseTool]:
    """获取随机生成工具"""
    return [
        generate_number,
        generate_uuid,
        generate_password,
    ]


def get_tools_by_categories(categories: Optional[List[str]] = None) -> List[BaseTool]:
    """
    根据类别获取工具

    Args:
        categories: 工具类别列表，可选值：
            - 'math': 数学工具
            - 'text': 文本工具
            - 'datetime': 日期时间工具
            - 'codecs': 编解码工具
            - 'data_struct': 数据结构工具
            - 'random': 随机生成工具
            如果为 None，返回所有工具

    Returns:
        指定类别的工具列表
    """
    if categories is None:
        return list(get_all_builtin_tools().values())

    tools = []
    category_mapping = {
        "math": get_math_tools,
        "text": get_text_tools,
        "datetime": get_datetime_tools,
        "codecs": get_codecs_tools,
        "data_struct": get_data_structure_tools,
        "random": get_random_tools,
    }

    for category in categories:
        if category in category_mapping:
            tools.extend(category_mapping[category]())

    return tools


def get_tool_names() -> List[str]:
    """
    获取所有工具的名称列表

    Returns:
        所有工具名称的列表
    """
    return list(get_all_builtin_tools().keys())


def get_tool_descriptions() -> Dict[str, str]:
    """
    获取所有工具的描述信息

    Returns:
        工具名称到描述的映射字典
    """
    return {name: tool.description for name, tool in get_all_builtin_tools().items()}


# 新增：根据工具名称列表筛选工具
def get_tools_by_names(names: Optional[List[str]] = None) -> List[BaseTool]:
    """
    根据工具名称列表筛选工具

    Args:
        names: 工具名称列表。如果为 None 或空，返回所有工具

    Returns:
        工具对象列表
    """
    all_tools = get_all_builtin_tools()
    if not names:
        return list(all_tools.values())
    return [all_tools[name] for name in names if name in all_tools]


# 导出主要函数
__all__ = [
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
