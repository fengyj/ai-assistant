"""
Unit tests for codecs tools module.

This module contains tests for:
- generate_hash function
- base64_convert function
- url_convert function
"""

from assistant.llm.tools.codecs import base64_convert, generate_hash, url_convert


class TestGenerateHash:
    """Test cases for generate_hash function."""

    def test_generate_hash_sha256_hex(self) -> None:
        """Test SHA256 hash generation in hex format."""
        result = generate_hash.invoke(
            {"text": "test", "algorithm": "sha256", "encoding": "utf-8", "output_format": "hex"}
        )
        assert result["status"] == "success"
        assert "hash_value" in result["data"]
        assert result["data"]["algorithm"] == "sha256"
        assert result["data"]["output_format"] == "hex"

    def test_generate_hash_md5_base64(self) -> None:
        """Test MD5 hash generation in base64 format."""
        result = generate_hash.invoke(
            {"text": "test", "algorithm": "md5", "encoding": "utf-8", "output_format": "base64"}
        )
        assert result["status"] == "success"
        assert "hash_value" in result["data"]
        assert result["data"]["algorithm"] == "md5"
        assert result["data"]["output_format"] == "base64"

    def test_generate_hash_empty_string(self) -> None:
        """Test hash generation for empty string."""
        result = generate_hash.invoke({"text": ""})
        assert result["status"] == "success"
        assert result["data"]["input_length"] == 0

    def test_generate_hash_invalid_encoding(self) -> None:
        """Test hash generation with invalid encoding."""
        result = generate_hash.invoke({"text": "test", "algorithm": "sha256", "encoding": "invalid-encoding"})
        assert result["status"] == "error"


class TestBase64Convert:
    """Test cases for base64_convert function."""

    def test_base64_encode(self) -> None:
        """Test Base64 encoding."""
        result = base64_convert.invoke({"data": "hello", "direction": "encode"})
        assert result["status"] == "success"
        assert result["data"]["converted_data"] == "aGVsbG8="
        assert result["data"]["direction"] == "encode"

    def test_base64_decode(self) -> None:
        """Test Base64 decoding."""
        result = base64_convert.invoke({"data": "aGVsbG8=", "direction": "decode"})
        assert result["status"] == "success"
        assert result["data"]["converted_data"] == "hello"
        assert result["data"]["direction"] == "decode"

    def test_base64_encode_url_safe(self) -> None:
        """Test URL-safe Base64 encoding."""
        result = base64_convert.invoke({"data": "hello?", "direction": "encode", "url_safe": True})
        assert result["status"] == "success"
        assert result["data"]["url_safe"] is True

    def test_base64_decode_invalid(self) -> None:
        """Test decoding invalid Base64 string."""
        result = base64_convert.invoke({"data": "invalid", "direction": "decode"})
        assert result["status"] == "error"


class TestUrlConvert:
    """Test cases for url_convert function."""

    def test_url_encode(self) -> None:
        """Test URL encoding."""
        result = url_convert.invoke({"text": "hello world", "direction": "encode"})
        assert result["status"] == "success"
        assert result["data"]["converted_text"] == "hello%20world"
        assert result["data"]["direction"] == "encode"

    def test_url_decode(self) -> None:
        """Test URL decoding."""
        result = url_convert.invoke({"text": "hello%20world", "direction": "decode"})
        assert result["status"] == "success"
        assert result["data"]["converted_text"] == "hello world"
        assert result["data"]["direction"] == "decode"

    def test_url_encode_with_safe_chars(self) -> None:
        """Test URL encoding with safe characters."""
        result = url_convert.invoke({"text": "hello@world", "direction": "encode", "safe_chars": "@"})
        assert result["status"] == "success"
        assert "@" in result["data"]["converted_text"]
