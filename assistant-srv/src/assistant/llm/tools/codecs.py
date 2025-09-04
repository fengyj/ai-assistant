"""
codecsgraphic operations tools.

Provides hashing, Base64 encoding/decoding, and URL encoding/decoding utilities.
"""

import base64
import hashlib
import urllib.parse
from enum import Enum
from typing import Any, Dict, Literal

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .base import ToolResult

# =============================================================================
# Enums
# =============================================================================


class HashAlgorithm(str, Enum):
    """Supported hash algorithms."""

    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"


# =============================================================================
# Input Parameter Models
# =============================================================================


class HashInput(BaseModel):
    """Hash generation parameters."""

    text: str = Field(description="The text to hash")
    algorithm: HashAlgorithm = Field(default=HashAlgorithm.SHA256, description="Hash algorithm to use")
    encoding: str = Field(default="utf-8", description="Text encoding")
    output_format: Literal["hex", "base64"] = Field(default="hex", description="Output format")


class Base64Input(BaseModel):
    """Base64 conversion parameters."""

    data: str = Field(description="The data to encode/decode")
    direction: Literal["encode", "decode"] = Field(default="encode", description="Operation direction")
    encoding: str = Field(default="utf-8", description="Text encoding")
    url_safe: bool = Field(default=False, description="Use URL-safe base64 encoding")


class UrlInput(BaseModel):
    """URL conversion parameters."""

    text: str = Field(description="The text to encode/decode")
    direction: Literal["encode", "decode"] = Field(default="encode", description="Operation direction")
    safe_chars: str = Field(default="", description="Additional safe characters for encoding")
    encoding: str = Field(default="utf-8", description="Text encoding")


# =============================================================================
# Tool Implementations
# =============================================================================


@tool("local::codecs.generate_hash", args_schema=HashInput)
def generate_hash(
    text: str,
    algorithm: HashAlgorithm = HashAlgorithm.SHA256,
    encoding: str = "utf-8",
    output_format: Literal["hex", "base64"] = "hex",
) -> Dict[str, Any]:
    """
    Generate codecsgraphic hash for given text using various algorithms.

    Returns:
        Dictionary containing hash generation results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'hash_value': (string) The generated hash value in specified format
          - 'algorithm': (string) Hash algorithm used (MD5, SHA1, SHA256, SHA512)
          - 'input_length': (integer) Length of input text in characters
          - 'encoding': (string) Text encoding used for byte conversion
          - 'output_format': (string) Output format used (hex or base64)
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        # Encode text to bytes
        text_bytes = text.encode(encoding)

        # Get hash algorithm
        hash_obj = hashlib.new(algorithm.value)
        hash_obj.update(text_bytes)

        # Generate hash in specified format
        if output_format == "hex":
            hash_value = hash_obj.hexdigest()
        else:  # base64
            hash_value = base64.b64encode(hash_obj.digest()).decode()

        # Return using ToolResult for consistency
        return ToolResult.success(
            {
                "hash_value": hash_value,
                "algorithm": algorithm.value,
                "input_length": len(text),
                "encoding": encoding,
                "output_format": output_format,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Hash generation failed: {str(e)}").model_dump()


@tool("local::codecs.base64_convert", args_schema=Base64Input)
def base64_convert(
    data: str, direction: Literal["encode", "decode"] = "encode", encoding: str = "utf-8", url_safe: bool = False
) -> Dict[str, Any]:
    """
    Encode or decode data using Base64 with support for URL-safe variant.

    Returns:
        Dictionary containing Base64 conversion results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'converted_data': (string) The converted data result
          - 'direction': (string) Conversion direction performed (encode/decode)
          - 'input_length': (integer) Length of input data in characters
          - 'output_length': (integer) Length of output data in characters
          - 'encoding': (string) Text encoding used for string operations
          - 'url_safe': (boolean) Whether URL-safe Base64 variant was used
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        input_length = len(data)

        if direction == "encode":
            # Encode to base64
            data_bytes = data.encode(encoding)
            if url_safe:
                encoded_bytes = base64.urlsafe_b64encode(data_bytes)
            else:
                encoded_bytes = base64.b64encode(data_bytes)
            converted_data = encoded_bytes.decode("ascii")

        elif direction == "decode":
            # Decode from base64
            try:
                if url_safe:
                    decoded_bytes = base64.urlsafe_b64decode(data)
                else:
                    decoded_bytes = base64.b64decode(data)
                converted_data = decoded_bytes.decode(encoding)
            except Exception as decode_error:
                return ToolResult.failure(f"Invalid base64 string: {str(decode_error)}").model_dump()

        else:
            return ToolResult.failure(f"Unsupported direction '{direction}'. Use 'encode' or 'decode'").model_dump()

        # Return using ToolResult for consistency
        return ToolResult.success(
            {
                "converted_data": converted_data,
                "direction": direction,
                "input_length": input_length,
                "output_length": len(converted_data),
                "encoding": encoding,
                "url_safe": url_safe,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Base64 conversion failed: {str(e)}").model_dump()


@tool("local::codecs.url_convert", args_schema=UrlInput)
def url_convert(
    text: str, direction: Literal["encode", "decode"] = "encode", safe_chars: str = "", encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Encode or decode data using URL encoding (percent-encoding) with configurable safe characters.

    Returns:
        Dictionary containing URL conversion results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'converted_text': (string) The converted text result
          - 'direction': (string) Conversion direction performed (encode/decode)
          - 'input_length': (integer) Length of input text in characters
          - 'output_length': (integer) Length of output text in characters
          - 'safe_chars': (string) Additional safe characters used during encoding
          - 'encoding': (string) Text encoding used for URL operations
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        input_length = len(text)

        if direction == "encode":
            # URL encode with custom safe characters
            converted_text = urllib.parse.quote(text, safe=safe_chars, encoding=encoding)

        elif direction == "decode":
            # URL decode
            converted_text = urllib.parse.unquote(text, encoding=encoding)

        else:
            return ToolResult.failure(f"Unsupported direction '{direction}'. Use 'encode' or 'decode'").model_dump()

        # Return using ToolResult for consistency
        return ToolResult.success(
            {
                "converted_text": converted_text,
                "direction": direction,
                "input_length": input_length,
                "output_length": len(converted_text),
                "safe_chars": safe_chars,
                "encoding": encoding,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"URL conversion failed: {str(e)}").model_dump()
