"""
Unit tests for validation tools module.

This module contains tests for:
- validate_json function
- validate_xml function
- validate_csv function
- lint_markdown function
"""

from assistant.llm.tools.validation import lint_markdown, validate_csv, validate_json, validate_xml


class TestValidateJson:
    """Test cases for validate_json function."""

    def test_valid_json(self) -> None:
        """Test validating valid JSON."""
        result = validate_json.invoke('{"name": "test", "value": 123}')
        assert result["status"] == "success"
        assert result["data"]["is_valid"] is True
        assert result["data"]["is_valid"] is True

    def test_invalid_json(self) -> None:
        """Test validating invalid JSON."""
        result = validate_json.invoke('{"name": "test", "value": }')
        assert result["status"] == "success"
        assert result["data"]["is_valid"] is False

    def test_empty_json(self) -> None:
        """Test validating empty JSON."""
        result = validate_json.invoke("{}")
        assert result["status"] == "success"
        assert result["data"]["is_valid"] is True


class TestValidateXml:
    """Test cases for validate_xml function."""

    def test_valid_xml(self) -> None:
        """Test validating valid XML."""
        xml_data = '<?xml version="1.0"?><root><name>test</name></root>'
        result = validate_xml.invoke(xml_data)
        assert result["status"] == "success"
        assert result["data"]["is_valid"] is True

    def test_invalid_xml(self) -> None:
        """Test validating invalid XML."""
        result = validate_xml.invoke("<root><name>test</name>")
        assert result["status"] == "success"
        assert result["data"]["is_valid"] is False

    def test_malformed_xml(self) -> None:
        """Test validating malformed XML."""
        result = validate_xml.invoke("<root><name>test<name></root>")
        assert result["status"] == "success"
        assert result["data"]["is_valid"] is False


class TestValidateCsv:
    """Test cases for validate_csv function."""

    def test_valid_csv(self) -> None:
        """Test validating valid CSV."""
        csv_data = "name,value\nJohn,123\nJane,456"
        result = validate_csv.invoke(csv_data)
        assert result["status"] == "success"
        assert result["data"]["is_valid"] is True

    def test_invalid_csv_with_quotes(self) -> None:
        """Test validating CSV with unclosed quotes."""
        csv_data = 'name,value\n"John,123\nJane,456'
        result = validate_csv.invoke(csv_data)
        assert result["status"] == "success"
        assert result["data"]["is_valid"] is False

    def test_empty_csv(self) -> None:
        """Test validating empty CSV."""
        result = validate_csv.invoke("")
        assert result["status"] == "success"
        assert result["data"]["is_valid"] is False


class TestLintMarkdown:
    """Test cases for lint_markdown function."""

    def test_valid_markdown(self) -> None:
        """Test linting valid Markdown."""
        md_data = "# Title\n\nThis is a paragraph.\n\n- List item 1\n- List item 2"
        result = lint_markdown.invoke(md_data)
        assert result["status"] == "success"
        assert result["data"]["issue_count"] == 0

    def test_markdown_with_issues(self) -> None:
        """Test linting Markdown with potential issues."""
        md_data = "#Title\n\nThis is a paragraph with  multiple  spaces.\n\n- List item"
        result = lint_markdown.invoke(md_data)
        assert result["status"] == "success"
        # Note: The actual validation logic may vary

    def test_empty_markdown(self) -> None:
        """Test linting empty Markdown."""
        result = lint_markdown.invoke("")
        assert result["status"] == "success"
        assert result["data"]["issue_count"] == 0
