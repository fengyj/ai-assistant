"""
Text processing tools for statistics, case conversion, regex operations, and text comparison.
"""

import difflib
import re
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import pycld2 as cld2
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from textstat import textstat

from .base import ToolResult

# =============================================================================
# Enums
# =============================================================================


class CaseType(str, Enum):
    """Text case conversion types."""

    UPPER = "upper"
    LOWER = "lower"
    TITLE = "title"
    CAPITALIZE = "capitalize"
    SNAKE_CASE = "snake_case"
    CAMEL_CASE = "camelCase"
    PASCAL_CASE = "PascalCase"


# =============================================================================
# Input Schemas
# =============================================================================


class TextStatsInput(BaseModel):
    """Input schema for text statistics analysis tool."""

    text: str = Field(..., description="The text to analyze for statistics and language detection")
    words_per_minute: Optional[int] = Field(
        None, description="Words per minute for reading time estimation (200-300 typical). If None, defaults to 200"
    )
    expected_language: Optional[str] = Field(
        None, description="Expected language codes (e.g., 'en', 'zh', 'ja,fr'). ISO 639-1 codes, comma-separated"
    )


class CaseConversionInput(BaseModel):
    """Input schema for case conversion."""

    text: str = Field(..., description="The text to convert")
    case_type: CaseType = Field(..., description="The case conversion type")
    separator: Optional[str] = Field(None, description="Separator for snake_case (default '_')")


class RegexFindReplaceInput(BaseModel):
    """Input schema for regex find and replace operations."""

    text: str = Field(..., description="The text to search")
    pattern: str = Field(..., description="The regex pattern to search for")
    flags: Optional[str] = Field(None, description="Regex flags (e.g., 'i' for case-insensitive)")
    replacement: Optional[str] = Field(None, description="Replacement string for replace operation")


class TextComparisonInput(BaseModel):
    """Input schema for text comparison."""

    text1: str = Field(..., description="First text to compare")
    text2: str = Field(..., description="Second text to compare")
    context_lines: Optional[int] = Field(None, description="Context lines for diff (default all if None)")


# =============================================================================
# Helper Functions
# =============================================================================


def detect_language(
    text: str, expected_language: Optional[str] = None, is_plain_text: bool = False
) -> List[Dict[str, Any]]:
    """Detect language using pycld2 with optional hint and plain text flag.

    Args:
        text: The text to detect language for
        expected_language: Expected language code(s) as hint (e.g., 'en', 'zh', 'en,jp').
                          Use ISO 639-1 two-letter codes. Multiple codes separated by comma.
        is_plain_text: Whether the text is plain text (skip HTML/XML tag removal for better performance)

    Returns:
        List of detected languages with their details, sorted by confidence score.
        Each item contains: language_code, language_name, percent, score
    """

    try:
        # 准备cld2.detect的参数
        detect_kwargs: Dict[str, Any] = {"isPlainText": is_plain_text}

        if expected_language:
            # 处理多个语言代码（用逗号分隔）
            hint_codes = [code.strip().lower()[:2] for code in expected_language.split(",") if code.strip()]
            if hint_codes:
                detect_kwargs["hintLanguage"] = ",".join(hint_codes)

        is_reliable, _, details = cld2.detect(text, **detect_kwargs)

        # 只返回可靠的结果
        if not is_reliable:
            return []

        result_filter: Callable[[str, float], bool] = (
            lambda lang_code, percent: lang_code is not None and lang_code != "un" and percent > 0
        )
        results = [
            {"language_code": lang_code, "language_name": lang_name, "percent": percent, "score": score}
            for lang_name, lang_code, percent, score in details
            if result_filter(lang_code, percent)
        ]

        return results

    except Exception:
        return []


def count_language_characters(text: str) -> Dict[str, int]:
    """Count characters by language/script using Unicode ranges."""
    counts = {
        "latin": 0,  # 英文、基本拉丁字母 (U+0000-U+00FF)
        "latin_extended": 0,  # 扩展拉丁字母 (U+0100-U+024F)
        "cyrillic": 0,  # 西里尔字母 (U+0400-U+04FF)
        "arabic": 0,  # 阿拉伯文 (U+0600-U+06FF)
        "hebrew": 0,  # 希伯来文 (U+0590-U+05FF)
        "devanagari": 0,  # 天城文 (U+0900-U+097F)
        "chinese": 0,  # 中文 (U+4E00-U+9FFF)
        "japanese_hiragana": 0,  # 日文平假名 (U+3040-U+309F)
        "japanese_katakana": 0,  # 日文片假名 (U+30A0-U+30FF)
        "korean": 0,  # 韩文 (U+AC00-U+D7AF)
        "thai": 0,  # 泰文 (U+0E00-U+0E7F)
        "greek": 0,  # 希腊文 (U+0370-U+03FF)
        "other": 0,  # 其他字符
    }

    for char in text:
        code = ord(char)
        if 0x0000 <= code <= 0x00FF:
            counts["latin"] += 1
        elif 0x0100 <= code <= 0x024F:
            counts["latin_extended"] += 1
        elif 0x0400 <= code <= 0x04FF:
            counts["cyrillic"] += 1
        elif 0x0600 <= code <= 0x06FF:
            counts["arabic"] += 1
        elif 0x0590 <= code <= 0x05FF:
            counts["hebrew"] += 1
        elif 0x0900 <= code <= 0x097F:
            counts["devanagari"] += 1
        elif 0x4E00 <= code <= 0x9FFF:
            counts["chinese"] += 1
        elif 0x3040 <= code <= 0x309F:
            counts["japanese_hiragana"] += 1
        elif 0x30A0 <= code <= 0x30FF:
            counts["japanese_katakana"] += 1
        elif 0xAC00 <= code <= 0xD7AF:
            counts["korean"] += 1
        elif 0x0E00 <= code <= 0x0E7F:
            counts["thai"] += 1
        elif 0x0370 <= code <= 0x03FF:
            counts["greek"] += 1
        else:
            counts["other"] += 1

    # 只返回有内容的语言统计
    return {lang: count for lang, count in counts.items() if count > 0}


def calculate_basic_stats(text: str) -> Dict[str, Any]:
    """Calculate basic text statistics with language character counts.

    This method provides the most reliable statistics when language detection
    is uncertain or unavailable. It focuses on character counts and line counts
    which are universally applicable, and includes language-specific character
    counts based on Unicode ranges for major world languages.
    """
    # 基本确定的统计
    character_count = len(text)

    lines = text.split("\n")
    line_count = len(lines)

    # 语言字符统计 - 根据Unicode编码范围识别主流语言
    language_chars = count_language_characters(text)

    return {
        "character_count": character_count,
        "line_count": line_count,
        "language_characters": language_chars,
    }


def calculate_english_stats(text: str) -> Dict[str, Any]:
    """Calculate English text statistics using textstat."""

    try:
        # Basic Counts
        syllable_count = textstat.syllable_count(text)
        lexicon_count = textstat.lexicon_count(text)
        sentence_count = textstat.sentence_count(text)
        letter_count = textstat.letter_count(text)
        words_per_sentence = textstat.words_per_sentence(text)
        avg_syllables_per_word = textstat.avg_syllables_per_word(text)
        difficult_words = textstat.difficult_words(text)

        # Readability Indices
        flesch_reading_ease = textstat.flesch_reading_ease(text)
        dale_chall_readability_score = textstat.dale_chall_readability_score(text)
        text_standard = textstat.text_standard(text)

        return {
            "syllable_count": syllable_count,
            "word_count": lexicon_count,
            "sentence_count": sentence_count,
            "letter_count": letter_count,
            "words_per_sentence": words_per_sentence,
            "avg_syllables_per_word": avg_syllables_per_word,
            "difficult_words": difficult_words,
            "flesch_reading_ease": flesch_reading_ease,
            "dale_chall_readability_score": dale_chall_readability_score,
            "text_standard": text_standard,
        }
    except Exception:
        return {}


def calculate_latin_stats(text: str) -> Dict[str, Any]:
    """Calculate basic statistics for Latin-script languages (non-English) using textstat."""

    try:
        lexicon_count = textstat.lexicon_count(text)
        sentence_count = textstat.sentence_count(text)
        letter_count = textstat.letter_count(text)
        words_per_sentence = textstat.words_per_sentence(text)

        return {
            "word_count": lexicon_count,
            "sentence_count": sentence_count,
            "letter_count": letter_count,
            "words_per_sentence": words_per_sentence,
        }
    except Exception:
        return {}


def calculate_chinese_stats(text: str) -> Dict[str, Any]:

    try:

        sentence_delimiters = r"[。！？.!?]"
        sentences = re.split(sentence_delimiters, text)
        sentences_filtered = [s for s in sentences if s.strip()]
        sentence_count = len(sentences_filtered)
        words_per_sentence = sum(len(s) for s in sentences_filtered) / sentence_count if sentence_count > 0 else 0

        return {"sentence_count": sentence_count, "words_per_sentence": words_per_sentence}
    except Exception:
        return {}


def filter_non_latin_chars(text: str) -> str:
    """Filter out characters outside U+0000-U+00FF range for English text analysis."""
    return "".join(char for char in text if 0x0000 <= ord(char) <= 0x00FF)


# =============================================================================
# Tool Implementations
# =============================================================================


@tool("get_text_statistics", args_schema=TextStatsInput)
def get_statistics(
    text: str,
    words_per_minute: Optional[int] = None,
    expected_language: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Use it to get comprehensive statistics about a text including character count, word count, reading time estimation,
    language detection, and readability analysis for multiple languages.

    Supports English, Chinese, and other Latin-script languages.

    Reading time is automatically calculated if word_count is available, using the provided words_per_minute
    (defaults to 200 if None).

    Returns:
        Dictionary containing text analysis results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'character_count': (integer) Total number of characters in the text
          - 'line_count': (integer) Number of lines in the text
          - 'words_per_sentence': (float, optional) Average sentence length. English/Chinese/Latin-script (>80%)
          - 'avg_syllables_per_word': (float, optional) Average syllables per word. Available only for English (>80%)
          - 'dale_chall_readability_score': (float, optional) Dale-Chall Readability Score. English only (>80%)
          - 'detected_languages': (list) Detected languages (dicts with language_code, language_name, percent, score)
          - 'difficult_words': (integer, optional) Number of difficult words. Available only for English (>80%)
          - 'flesch_reading_ease': (float, optional) Flesch Reading Ease score (0-100). English only (>80%)
          - 'language_characters': (dict) Character counts by language/script (e.g., {'latin': 100, 'chinese': 50})
          - 'letter_count': (integer, optional) Number of letters. Available for English (>80%) or Latin-script (>80%)
          - 'reading_time_minutes': (float) Estimated reading time in minutes (based on word count, 200 wpm default)
          - 'sentence_count': (integer, optional) Number of sentences. Available for English/Chinese/Latin-script (>80%)
          - 'syllable_count': (integer, optional) Total syllables. Available only for English (>80%)
          - 'text_standard': (string, optional) US Grade Level standard. Available only for English (>80%)
          - 'word_count': (integer, optional) Number of words. Available for English (>80%) or Latin-script (>80%)
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        if not text:
            return ToolResult.success(
                {
                    "character_count": 0,
                    "line_count": 0,
                }
            ).model_dump()

        # Step 1: Calculate basic statistics
        basic_stats = calculate_basic_stats(text)

        # Step 2: Detect languages
        detected_languages = detect_language(text, expected_language)

        # Initialize result data with basic stats
        result_data = basic_stats.copy()
        result_data["detected_languages"] = detected_languages

        # Step 3: Determine primary language and its percentage
        if detected_languages:
            primary_lang = detected_languages[0]["language_code"]
            primary_percent = detected_languages[0]["percent"]
        else:
            primary_lang = "unknown"
            primary_percent = 0

        # Step 4: Calculate language-specific statistics based on conditions
        analysis_result = {}

        if primary_lang == "en" and primary_percent > 80:
            # English with high percentage
            if 80 < primary_percent < 98:
                # Filter out non-Latin characters
                filtered_text = filter_non_latin_chars(text)
                analysis_result = calculate_english_stats(filtered_text)
            else:
                analysis_result = calculate_english_stats(text)
        elif primary_lang == "zh" and primary_percent > 80:
            # Chinese with high percentage
            analysis_result = calculate_chinese_stats(text)
        elif primary_lang in ["fr", "de", "es", "it", "pt", "ru"] and primary_percent > 80:
            # Other Latin-script languages with high percentage
            analysis_result = calculate_latin_stats(text)
        # For other cases, only basic stats are used

        # Step 5: Merge analysis results into result_data
        result_data.update(analysis_result)

        # Step 6: Calculate reading time if word_count is available
        reading_time_minutes = 0
        word_count_for_reading = result_data.get("word_count", 0)
        if word_count_for_reading > 0:
            wpm = words_per_minute if words_per_minute is not None else 200
            reading_time_minutes = word_count_for_reading / wpm
        result_data["reading_time_minutes"] = round(reading_time_minutes, 2)

        return ToolResult.success(result_data).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Text statistics analysis failed: {str(e)}").model_dump()


@tool("change_character_case", args_schema=CaseConversionInput)
def change_case(text: str, case_type: CaseType, separator: Optional[str] = None) -> Dict[str, Any]:
    """
    Use it to convert text case according to the specified case type.

    Returns:
        Dictionary containing case conversion results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'original_text': (string) The original input text
          - 'converted_text': (string) The case-converted text
          - 'case_type': (string) The case conversion type applied
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        # Set default values
        if separator is None:
            separator = "_"

        result_text = ""

        if case_type == CaseType.UPPER:
            result_text = text.upper()
        elif case_type == CaseType.LOWER:
            result_text = text.lower()
        elif case_type == CaseType.TITLE:
            result_text = text.title()
        elif case_type == CaseType.CAPITALIZE:
            result_text = text.capitalize()
        elif case_type == CaseType.SNAKE_CASE:
            # Convert to snake_case
            result_text = re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()
            result_text = re.sub(r"[^a-zA-Z0-9_]", separator, result_text)
        elif case_type == CaseType.CAMEL_CASE:
            # Convert to camelCase
            words = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", text)
            if words:
                result_text = words[0].lower() + "".join(word.capitalize() for word in words[1:])
        elif case_type == CaseType.PASCAL_CASE:
            # Convert to PascalCase
            words = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", text)
            result_text = "".join(word.capitalize() for word in words)

        return ToolResult.success(
            {"original_text": text, "converted_text": result_text, "case_type": case_type.value}
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Case conversion failed: {str(e)}").model_dump()


@tool("regex_find_and_replace", args_schema=RegexFindReplaceInput)
def regex_find_and_replace(
    text: str, pattern: str, flags: Optional[str] = None, replacement: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use it to find all matches of a regex pattern in the text, with optional replace functionality.

    The pattern and replacement MUST follow Python's `re` module syntax.

    If replacement is provided, performs find and replace operation.
    Otherwise, only finds and returns matches.

    Returns:
        Dictionary containing regex operation results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'matches': (list) List of matched strings (when replacement is None)
          - 'match_count': (integer) Number of matches found
          - 'pattern': (string) The regex pattern used
          - 'flags': (string) Regex flags used
          - 'replaced_text': (string, optional) The text after replacement (when replacement is provided)
          - 'replacement_count': (integer, optional) Number of replacements made (when replacement is provided)
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        # Compile regex with flags
        regex_flags = 0
        if flags:
            if "i" in flags:
                regex_flags |= re.IGNORECASE
            if "m" in flags:
                regex_flags |= re.MULTILINE
            if "s" in flags:
                regex_flags |= re.DOTALL

        compiled_pattern = re.compile(pattern, regex_flags)

        if replacement is not None:
            # Perform find and replace
            replaced_text, replacement_count = compiled_pattern.subn(replacement, text)
            return ToolResult.success(
                {
                    "match_count": replacement_count,
                    "pattern": pattern,
                    "flags": flags or "",
                    "replaced_text": replaced_text,
                    "replacement_count": replacement_count,
                }
            ).model_dump()
        else:
            # Only find matches
            matches = compiled_pattern.findall(text)
            return ToolResult.success(
                {"matches": matches, "match_count": len(matches), "pattern": pattern, "flags": flags or ""}
            ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Regex operation failed: {str(e)}").model_dump()


@tool("compare_texts", args_schema=TextComparisonInput)
def compare_texts(text1: str, text2: str, context_lines: Optional[int] = None) -> Dict[str, Any]:
    """
    Use it to compare two texts and generate a diff.

    Returns:
        Dictionary containing text comparison results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'similarity_ratio': (float) Similarity ratio between the texts (0-1)
          - 'diff': (list) List of diff lines
          - 'text1_length': (integer) Length of first text
          - 'text2_length': (integer) Length of second text
          - 'changes_count': (integer) Number of changes detected
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        # Set default value for context_lines
        if context_lines is None:
            # Show all lines by setting a large number
            context_lines = 1000

        # Calculate similarity
        similarity_ratio = difflib.SequenceMatcher(None, text1, text2).ratio()

        # Generate unified diff
        diff_lines = list(
            difflib.unified_diff(
                text1.splitlines(keepends=True),
                text2.splitlines(keepends=True),
                fromfile="text1",
                tofile="text2",
                lineterm="",
                n=context_lines,
            )
        )

        # Count changes
        changes_count = len([line for line in diff_lines if line.startswith(("+", "-", "@"))])

        return ToolResult.success(
            {
                "similarity_ratio": round(similarity_ratio, 3),
                "diff": diff_lines,
                "text1_length": len(text1),
                "text2_length": len(text2),
                "changes_count": changes_count,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Text comparison failed: {str(e)}").model_dump()
