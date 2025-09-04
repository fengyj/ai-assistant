"""
Unit tests for text processing tools module.
"""

from typing import Any, Dict, List
from unittest.mock import patch

from assistant.llm.tools.text import (
    CaseType,
    calculate_basic_stats,
    calculate_chinese_stats,
    calculate_english_stats,
    calculate_latin_stats,
    change_case,
    compare_texts,
    count_language_characters,
    detect_language,
    filter_non_latin_chars,
    get_statistics,
    regex_find_and_replace,
)


class TestDetectLanguage:
    """Test cases for detect_language function."""

    def test_detect_english_text(self) -> None:
        """Test language detection for English text."""
        text: str = "Hello world, this is a test."
        result: List[Dict[str, Any]] = detect_language(text)
        assert isinstance(result, list)
        if result:
            assert "language_code" in result[0]
            assert result[0]["language_code"] == "en"

    def test_detect_chinese_text(self) -> None:
        """Test language detection for Chinese text."""
        text: str = "你好世界，这是一个测试。"
        result: List[Dict[str, Any]] = detect_language(text)
        assert isinstance(result, list)
        if result:
            assert "language_code" in result[0]
            assert result[0]["language_code"] == "zh"

    def test_detect_with_expected_language(self) -> None:
        """Test language detection with expected language hint."""
        text: str = "Bonjour le monde"
        result: List[Dict[str, Any]] = detect_language(text, expected_language="fr")
        assert isinstance(result, list)

    def test_detect_empty_text(self) -> None:
        """Test language detection for empty text."""
        result: List[Dict[str, Any]] = detect_language("")
        assert result == []

    def test_detect_exception_handling(self) -> None:
        """Test exception handling in language detection."""
        with patch("assistant.llm.tools.text.cld2.detect", side_effect=Exception("Test error")):
            result: List[Dict[str, Any]] = detect_language("test")
            assert result == []


class TestCountLanguageCharacters:
    """Test cases for count_language_characters function."""

    def test_count_latin_characters(self) -> None:
        """Test counting Latin characters."""
        text: str = "Hello World"
        result: Dict[str, int] = count_language_characters(text)
        assert "latin" in result
        assert result["latin"] == 11  # H,e,l,l,o, ,W,o,r,l,d

    def test_count_chinese_characters(self) -> None:
        """Test counting Chinese characters."""
        text: str = "你好世界"
        result: Dict[str, int] = count_language_characters(text)
        assert "chinese" in result
        assert result["chinese"] == 4

    def test_count_mixed_characters(self) -> None:
        """Test counting mixed language characters."""
        text: str = "Hello 你好 World 世界"
        result: Dict[str, int] = count_language_characters(text)
        assert "latin" in result
        assert "chinese" in result
        assert result["latin"] > 0
        assert result["chinese"] > 0

    def test_count_empty_text(self) -> None:
        """Test counting characters in empty text."""
        result: Dict[str, int] = count_language_characters("")
        assert result == {}


class TestCalculateBasicStats:
    """Test cases for calculate_basic_stats function."""

    def test_calculate_basic_stats_normal_text(self) -> None:
        """Test basic statistics calculation for normal text."""
        text: str = "Hello\nWorld\nTest"
        result: Dict[str, Any] = calculate_basic_stats(text)
        assert "character_count" in result
        assert "line_count" in result
        assert "language_characters" in result
        assert result["character_count"] == 16  # H,e,l,l,o,\n,W,o,r,l,d,\n,T,e,s,t
        assert result["line_count"] == 3

    def test_calculate_basic_stats_empty_text(self) -> None:
        """Test basic statistics calculation for empty text."""
        result: Dict[str, Any] = calculate_basic_stats("")
        assert result["character_count"] == 0
        assert result["line_count"] == 1  # split by \n gives ['']


class TestCalculateEnglishStats:
    """Test cases for calculate_english_stats function."""

    def test_calculate_english_stats_normal_text(self) -> None:
        """Test English statistics calculation for normal text."""
        text: str = "This is a simple test sentence."
        result: Dict[str, Any] = calculate_english_stats(text)
        assert "word_count" in result
        assert "sentence_count" in result
        assert "syllable_count" in result
        assert result["word_count"] == 6
        assert result["sentence_count"] == 1

    def test_calculate_english_stats_exception_handling(self) -> None:
        """Test exception handling in English statistics calculation."""
        with patch("assistant.llm.tools.text.textstat.syllable_count", side_effect=Exception("Test error")):
            result: Dict[str, Any] = calculate_english_stats("test")
            assert result == {}


class TestCalculateLatinStats:
    """Test cases for calculate_latin_stats function."""

    def test_calculate_latin_stats_normal_text(self) -> None:
        """Test Latin statistics calculation for normal text."""
        text: str = "Ceci est un test simple."
        result: Dict[str, Any] = calculate_latin_stats(text)
        assert "word_count" in result
        assert "sentence_count" in result
        assert result["word_count"] == 5
        assert result["sentence_count"] == 1

    def test_calculate_latin_stats_exception_handling(self) -> None:
        """Test exception handling in Latin statistics calculation."""
        with patch("assistant.llm.tools.text.textstat.lexicon_count", side_effect=Exception("Test error")):
            result: Dict[str, Any] = calculate_latin_stats("test")
            assert result == {}


class TestCalculateChineseStats:
    """Test cases for calculate_chinese_stats function."""

    def test_calculate_chinese_stats_normal_text(self) -> None:
        """Test Chinese statistics calculation for normal text."""
        text: str = "这是一个简单的测试句子。"
        result: Dict[str, Any] = calculate_chinese_stats(text)
        assert "sentence_count" in result
        assert "words_per_sentence" in result
        assert result["sentence_count"] == 1

    def test_calculate_chinese_stats_multiple_sentences(self) -> None:
        """Test Chinese statistics calculation for multiple sentences."""
        text: str = "这是第一句。这是第二句！这是第三句？"
        result: Dict[str, Any] = calculate_chinese_stats(text)
        assert result["sentence_count"] == 3

    def test_calculate_chinese_stats_exception_handling(self) -> None:
        """Test exception handling in Chinese statistics calculation."""
        with patch("assistant.llm.tools.text.re.split", side_effect=Exception("Test error")):
            result: Dict[str, Any] = calculate_chinese_stats("test")
            assert result == {}


class TestFilterNonLatinChars:
    """Test cases for filter_non_latin_chars function."""

    def test_filter_non_latin_chars_mixed_text(self) -> None:
        """Test filtering non-Latin characters from mixed text."""
        text: str = "Hello 世界 World"
        result: str = filter_non_latin_chars(text)
        assert result == "Hello  World"

    def test_filter_non_latin_chars_latin_only(self) -> None:
        """Test filtering when text contains only Latin characters."""
        text: str = "Hello World"
        result: str = filter_non_latin_chars(text)
        assert result == "Hello World"

    def test_filter_non_latin_chars_non_latin_only(self) -> None:
        """Test filtering when text contains only non-Latin characters."""
        text: str = "你好世界"
        result: str = filter_non_latin_chars(text)
        assert result == ""


class TestGetStatistics:
    """Test cases for get_statistics tool."""

    def test_get_statistics_empty_text(self) -> None:
        """Test statistics for empty text."""
        result = get_statistics.invoke({"text": ""})
        assert result["status"] == "success"
        assert result["data"]["character_count"] == 0
        assert result["data"]["line_count"] == 0

    def test_get_statistics_english_text(self) -> None:
        """Test statistics for English text."""
        text: str = "This is a test."
        result = get_statistics.invoke({"text": text})
        assert result["status"] == "success"
        assert "word_count" in result["data"]
        assert "sentence_count" in result["data"]

    def test_get_statistics_chinese_text(self) -> None:
        """Test statistics for Chinese text."""
        text: str = "这是一个测试。"
        result = get_statistics.invoke({"text": text})
        assert result["status"] == "success"
        assert "character_count" in result["data"]

    def test_get_statistics_with_wpm(self) -> None:
        """Test statistics with custom words per minute."""
        text: str = "This is a test with multiple words."
        result = get_statistics.invoke({"text": text, "words_per_minute": 300})
        assert result["status"] == "success"
        assert "reading_time_minutes" in result["data"]

    def test_get_statistics_exception_handling(self) -> None:
        """Test exception handling in get_statistics."""
        with patch("assistant.llm.tools.text.calculate_basic_stats", side_effect=Exception("Test error")):
            result = get_statistics.invoke({"text": "test"})
            assert result["status"] == "error"


class TestChangeCase:
    """Test cases for change_case tool."""

    def test_change_case_upper(self) -> None:
        """Test converting text to uppercase."""
        result = change_case.invoke({"text": "hello world", "case_type": CaseType.UPPER})
        assert result["status"] == "success"
        assert result["data"]["converted_text"] == "HELLO WORLD"
        assert result["data"]["case_type"] == "upper"

    def test_change_case_lower(self) -> None:
        """Test converting text to lowercase."""
        result = change_case.invoke({"text": "HELLO WORLD", "case_type": CaseType.LOWER})
        assert result["status"] == "success"
        assert result["data"]["converted_text"] == "hello world"

    def test_change_case_title(self) -> None:
        """Test converting text to title case."""
        result = change_case.invoke({"text": "hello world", "case_type": CaseType.TITLE})
        assert result["status"] == "success"
        assert result["data"]["converted_text"] == "Hello World"

    def test_change_case_capitalize(self) -> None:
        """Test capitalizing text."""
        result = change_case.invoke({"text": "hello world", "case_type": CaseType.CAPITALIZE})
        assert result["status"] == "success"
        assert result["data"]["converted_text"] == "Hello world"

    def test_change_case_snake_case(self) -> None:
        """Test converting text to snake_case."""
        result = change_case.invoke({"text": "HelloWorld", "case_type": CaseType.SNAKE_CASE})
        assert result["status"] == "success"
        assert result["data"]["converted_text"] == "hello_world"

    def test_change_case_camel_case(self) -> None:
        """Test converting text to camelCase."""
        result = change_case.invoke({"text": "hello_world", "case_type": CaseType.CAMEL_CASE})
        assert result["status"] == "success"
        assert result["data"]["converted_text"] == "helloWorld"

    def test_change_case_pascal_case(self) -> None:
        """Test converting text to PascalCase."""
        result = change_case.invoke({"text": "hello_world", "case_type": CaseType.PASCAL_CASE})
        assert result["status"] == "success"
        assert result["data"]["converted_text"] == "HelloWorld"

    def test_change_case_with_separator(self) -> None:
        """Test snake_case conversion with custom separator."""
        result = change_case.invoke({"text": "HelloWorld", "case_type": CaseType.SNAKE_CASE, "separator": "-"})
        assert result["status"] == "success"
        # Note: separator is used for non-alphanumeric chars, not underscores
        assert result["data"]["converted_text"] == "hello_world"

    def test_change_case_exception_handling(self) -> None:
        """Test exception handling in change_case."""
        with patch("assistant.llm.tools.text.re.sub", side_effect=Exception("Test error")):
            result = change_case.invoke({"text": "test", "case_type": CaseType.SNAKE_CASE})
            assert result["status"] == "error"


class TestRegexFindAndReplace:
    """Test cases for regex_find_and_replace tool."""

    def test_regex_find_only(self) -> None:
        """Test regex find without replacement."""
        result = regex_find_and_replace.invoke({"text": "hello world hello", "pattern": r"hello"})
        assert result["status"] == "success"
        assert result["data"]["matches"] == ["hello", "hello"]
        assert result["data"]["match_count"] == 2

    def test_regex_find_and_replace(self) -> None:
        """Test regex find and replace."""
        result = regex_find_and_replace.invoke({"text": "hello world", "pattern": r"world", "replacement": "universe"})
        assert result["status"] == "success"
        assert result["data"]["replaced_text"] == "hello universe"
        assert result["data"]["replacement_count"] == 1

    def test_regex_with_flags(self) -> None:
        """Test regex with case-insensitive flag."""
        result = regex_find_and_replace.invoke({"text": "Hello World", "pattern": r"hello", "flags": "i"})
        assert result["status"] == "success"
        assert result["data"]["matches"] == ["Hello"]

    def test_regex_invalid_pattern(self) -> None:
        """Test regex with invalid pattern."""
        result = regex_find_and_replace.invoke({"text": "test", "pattern": r"[invalid"})
        assert result["status"] == "error"

    def test_regex_exception_handling(self) -> None:
        """Test exception handling in regex operations."""
        # Test with invalid regex pattern instead of mocking
        result = regex_find_and_replace.invoke({"text": "test", "pattern": r"[invalid"})
        assert result["status"] == "error"


class TestCompareTexts:
    """Test cases for compare_texts tool."""

    def test_compare_identical_texts(self) -> None:
        """Test comparing identical texts."""
        text: str = "hello world"
        result = compare_texts.invoke({"text1": text, "text2": text})
        assert result["status"] == "success"
        assert result["data"]["similarity_ratio"] == 1.0
        assert result["data"]["changes_count"] == 0

    def test_compare_different_texts(self) -> None:
        """Test comparing different texts."""
        text1: str = "hello world"
        text2: str = "hello universe"
        result = compare_texts.invoke({"text1": text1, "text2": text2})
        assert result["status"] == "success"
        assert result["data"]["similarity_ratio"] < 1.0
        assert result["data"]["changes_count"] > 0

    def test_compare_with_context_lines(self) -> None:
        """Test comparing texts with custom context lines."""
        text1: str = "line1\nline2\nline3"
        text2: str = "line1\nline2\nline4"
        result = compare_texts.invoke({"text1": text1, "text2": text2, "context_lines": 2})
        assert result["status"] == "success"
        assert isinstance(result["data"]["diff"], list)

    def test_compare_empty_texts(self) -> None:
        """Test comparing empty texts."""
        result = compare_texts.invoke({"text1": "", "text2": ""})
        assert result["status"] == "success"
        assert result["data"]["similarity_ratio"] == 1.0

    def test_compare_exception_handling(self) -> None:
        """Test exception handling in text comparison."""
        with patch("assistant.llm.tools.text.difflib.SequenceMatcher", side_effect=Exception("Test error")):
            result = compare_texts.invoke({"text1": "test1", "text2": "test2"})
            assert result["status"] == "error"
