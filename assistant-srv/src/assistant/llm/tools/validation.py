"""
Data format validation tools for JSON, XML, CSV, and Markdown.
"""

import csv
import io
import json
import re
from enum import Enum
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool
from lxml import etree
from pydantic import BaseModel, Field

from .base import ToolResult

# =============================================================================
# Enums
# =============================================================================


class ValidationLevel(str, Enum):
    """Validation strictness levels."""

    STRICT = "strict"
    RELAXED = "relaxed"
    BASIC = "basic"


# =============================================================================
# Input Parameter Models
# =============================================================================


class JsonValidationInput(BaseModel):
    """JSON validation parameters."""

    data: str = Field(description="JSON string to validate")
    strict: bool = Field(default=True, description="Use strict validation")


class XmlValidationInput(BaseModel):
    """XML validation parameters."""

    data: str = Field(description="XML string to validate")
    schema_url: Optional[str] = Field(default=None, description="URL to XSD schema for validation")


class CsvValidationInput(BaseModel):
    """CSV validation parameters."""

    data: str = Field(description="CSV string to validate")
    delimiter: str = Field(default=",", description="CSV delimiter character")
    has_header: bool = Field(default=True, description="Whether CSV has header row")
    expected_columns: Optional[int] = Field(default=None, description="Expected number of columns")


class MarkdownLintInput(BaseModel):
    """Markdown linting parameters."""

    data: str = Field(description="Markdown content to lint")
    check_links: bool = Field(default=False, description="Check for broken links")


# =============================================================================
# Utility Functions
# =============================================================================


def analyze_json_structure(data: Any) -> Dict[str, Any]:
    """Analyze the structure of parsed JSON data."""
    if isinstance(data, dict):
        return {
            "type": "object",
            "keys": list(data.keys()),
            "key_count": len(data),
            "nested_levels": max([analyze_json_structure(v)["nested_levels"] for v in data.values()], default=0) + 1,
        }
    elif isinstance(data, list):
        return {
            "type": "array",
            "length": len(data),
            "item_types": list(set(type(item).__name__ for item in data)),
            "nested_levels": max([analyze_json_structure(item)["nested_levels"] for item in data], default=0) + 1,
        }
    else:
        return {"type": type(data).__name__, "nested_levels": 0}


def validate_markdown_links(text: str) -> List[Dict[str, Any]]:
    """Check for potential issues with markdown links."""
    issues = []

    # Find all markdown links
    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    links = re.findall(link_pattern, text)

    for link_text, url in links:
        if not url.strip():
            issues.append({"type": "empty_url", "message": f"Empty URL in link '{link_text}'", "link_text": link_text})
        elif url.startswith("http") and " " in url:
            issues.append(
                {"type": "space_in_url", "message": f"Space found in URL: {url}", "link_text": link_text, "url": url}
            )

    return issues


def lint_markdown_structure(text: str) -> List[Dict[str, Any]]:
    """Check markdown structure for common issues."""
    issues = []
    lines = text.split("\n")

    # Check for heading hierarchy
    heading_levels = []
    for i, line in enumerate(lines, 1):
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            heading_levels.append((i, level))

            # Check for heading level skipping
            if heading_levels and len(heading_levels) > 1:
                prev_level = heading_levels[-2][1]
                if level > prev_level + 1:
                    issues.append(
                        {
                            "type": "heading_skip",
                            "line": i,
                            "message": f"Heading level jumps from {prev_level} to {level}",
                            "content": line.strip(),
                        }
                    )

    # Check for empty headers
    for i, line in enumerate(lines, 1):
        if re.match(r"^#+\s*$", line):
            issues.append(
                {"type": "empty_heading", "line": i, "message": "Empty heading found", "content": line.strip()}
            )

    return issues


# =============================================================================
# Tool Implementations
# =============================================================================


@tool("local::validation.validate_json", args_schema=JsonValidationInput)
def validate_json(data: str, strict: bool = True) -> Dict[str, Any]:
    """
    Validate JSON data format and structure.

    Returns:
        Dictionary containing JSON validation results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'is_valid': (boolean) Whether the JSON is valid
          - 'parsed_data': (any) Parsed JSON data if valid
          - 'structure_info': (dict) Information about JSON structure
          - 'error_details': (dict, optional) Error details if invalid
          - 'data_type': (string) Root data type (object/array/primitive)
          - 'validation_level': (string) Validation level used
        - 'error': (string, optional) Error message if validation failed
    """
    try:
        error_details = None
        parsed_data = None
        structure_info = {}

        try:
            # Parse JSON
            parsed_data = json.loads(data)
            is_valid = True

            # Analyze structure
            structure_info = analyze_json_structure(parsed_data)

        except json.JSONDecodeError as e:
            is_valid = False
            error_details = {
                "error_type": "JSONDecodeError",
                "message": str(e),
                "line": getattr(e, "lineno", None),
                "column": getattr(e, "colno", None),
                "position": getattr(e, "pos", None),
            }

        return ToolResult.success(
            {
                "is_valid": is_valid,
                "parsed_data": parsed_data,
                "structure_info": structure_info,
                "error_details": error_details,
                "data_type": structure_info.get("type", "unknown"),
                "validation_level": "strict" if strict else "basic",
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error validating JSON: {str(e)}").model_dump()


@tool("local::validation.validate_xml", args_schema=XmlValidationInput)
def validate_xml(data: str, schema_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate XML data format and optionally against a schema.

    Returns:
        Dictionary containing XML validation results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'is_valid': (boolean) Whether the XML is valid
          - 'is_well_formed': (boolean) Whether XML is well-formed
          - 'schema_valid': (boolean, optional) Whether XML validates against schema
          - 'root_element': (string) Name of root element if valid
          - 'element_count': (integer) Number of elements
          - 'error_details': (list) List of validation errors
        - 'error': (string, optional) Error message if validation failed
    """
    try:
        errors = []
        is_well_formed = False
        is_valid = False
        schema_valid = None
        root_element = None
        element_count = 0

        try:
            # Parse XML to check well-formedness
            root = etree.fromstring(data.encode("utf-8"))
            is_well_formed = True
            is_valid = True
            root_element = root.tag
            elements = root.xpath(".//*")
            element_count = len(elements) + 1 if isinstance(elements, list) else 1  # +1 for root

            # Schema validation if URL provided
            if schema_url:
                try:
                    # Note: In a real implementation, you'd fetch and parse the schema
                    # For now, we'll just indicate that schema validation was requested
                    schema_valid = None  # Would implement actual schema validation
                    errors.append(
                        {"type": "schema_validation", "message": "Schema validation not implemented in this version"}
                    )
                except Exception as schema_error:
                    schema_valid = False
                    errors.append({"type": "schema_error", "message": f"Schema validation error: {str(schema_error)}"})

        except etree.XMLSyntaxError as e:
            is_well_formed = False
            is_valid = False
            errors.append(
                {"type": "XMLSyntaxError", "message": str(e), "line": str(e.lineno or 0), "column": str(e.offset or 0)}
            )

        return ToolResult.success(
            {
                "is_valid": is_valid,
                "is_well_formed": is_well_formed,
                "schema_valid": schema_valid,
                "root_element": root_element,
                "element_count": element_count,
                "error_details": errors,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error validating XML: {str(e)}").model_dump()


@tool("local::validation.validate_csv", args_schema=CsvValidationInput)
def validate_csv(
    data: str, delimiter: str = ",", has_header: bool = True, expected_columns: Optional[int] = None
) -> Dict[str, Any]:
    """
    Validate CSV data format and structure.

    Returns:
        Dictionary containing CSV validation results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'is_valid': (boolean) Whether the CSV is valid
          - 'row_count': (integer) Number of data rows
          - 'column_count': (integer) Number of columns
          - 'headers': (list) Column headers if present
          - 'issues': (list) List of validation issues found
          - 'delimiter_used': (string) Delimiter character used
          - 'consistent_columns': (boolean) Whether all rows have same column count
        - 'error': (string, optional) Error message if validation failed
    """
    try:
        issues: List[Dict[str, Any]] = []
        is_valid = True
        headers = []

        # Parse CSV
        csv_file = io.StringIO(data)
        reader = csv.reader(csv_file, delimiter=delimiter)

        rows = list(reader)

        if not rows:
            return ToolResult.success(
                {
                    "is_valid": False,
                    "row_count": 0,
                    "column_count": 0,
                    "headers": [],
                    "issues": [{"type": "empty_csv", "message": "CSV data is empty"}],
                    "delimiter_used": delimiter,
                    "consistent_columns": True,
                }
            ).model_dump()

        # Extract headers if present
        if has_header and rows:
            headers = rows[0]
            data_rows = rows[1:]
        else:
            data_rows = rows

        row_count = len(data_rows)
        column_count = len(rows[0]) if rows else 0

        # Check column consistency
        column_counts = [len(row) for row in rows]
        consistent_columns = len(set(column_counts)) <= 1

        if not consistent_columns:
            is_valid = False
            issues.append(
                {
                    "type": "inconsistent_columns",
                    "message": "Rows have different numbers of columns",
                    "column_counts": column_counts,
                }
            )

        # Check expected columns
        if expected_columns is not None and column_count != expected_columns:
            is_valid = False
            issues.append(
                {
                    "type": "column_count_mismatch",
                    "message": f"Expected {expected_columns} columns, found {column_count}",
                    "expected": expected_columns,
                    "actual": column_count,
                }
            )

        # Check for empty rows
        for i, row in enumerate(data_rows):
            if not any(cell.strip() for cell in row):
                issues.append(
                    {
                        "type": "empty_row",
                        "message": f"Empty row found at line {i + (2 if has_header else 1)}",
                        "row_index": i,
                    }
                )

        return ToolResult.success(
            {
                "is_valid": is_valid,
                "row_count": row_count,
                "column_count": column_count,
                "headers": headers,
                "issues": issues,
                "delimiter_used": delimiter,
                "consistent_columns": consistent_columns,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error validating CSV: {str(e)}").model_dump()


@tool("local::validation.lint_markdown", args_schema=MarkdownLintInput)
def lint_markdown(data: str, check_links: bool = False) -> Dict[str, Any]:
    """
    Lint Markdown content for common issues and formatting problems.

    Returns:
        Dictionary containing Markdown linting results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'issue_count': (integer) Total number of issues found
          - 'issues': (list) List of linting issues
          - 'structure_issues': (list) Structural problems (heading hierarchy, etc.)
          - 'link_issues': (list) Link-related issues if check_links enabled
          - 'heading_count': (integer) Number of headings
          - 'line_count': (integer) Number of lines
          - 'has_front_matter': (boolean) Whether document has YAML front matter
        - 'error': (string, optional) Error message if linting failed
    """
    try:
        all_issues = []

        # Check document structure
        structure_issues = lint_markdown_structure(data)
        all_issues.extend(structure_issues)

        # Check links if requested
        link_issues = []
        if check_links:
            link_issues = validate_markdown_links(data)
            all_issues.extend(link_issues)

        # Basic statistics
        lines = data.split("\n")
        line_count = len(lines)
        heading_count = len([line for line in lines if line.startswith("#")])

        # Check for YAML front matter
        has_front_matter = data.startswith("---\n") and "\n---\n" in data

        return ToolResult.success(
            {
                "issue_count": len(all_issues),
                "issues": all_issues,
                "structure_issues": structure_issues,
                "link_issues": link_issues,
                "heading_count": heading_count,
                "line_count": line_count,
                "has_front_matter": has_front_matter,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error linting Markdown: {str(e)}").model_dump()
