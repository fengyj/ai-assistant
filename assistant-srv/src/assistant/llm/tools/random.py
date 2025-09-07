"""
Random number generation and selection tools.
"""

import random
import string
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .base import ToolResult

# =============================================================================
# Enums
# =============================================================================


class CharacterSet(str, Enum):
    """Character sets for random string generation."""

    LETTERS = "letters"
    DIGITS = "digits"
    LETTERS_DIGITS = "letters_digits"
    LOWERCASE = "lowercase"
    UPPERCASE = "uppercase"
    PUNCTUATION = "punctuation"
    ALPHANUMERIC = "alphanumeric"
    ALL_PRINTABLE = "all_printable"
    CUSTOM = "custom"


# =============================================================================
# Input Parameter Models
# =============================================================================


class RandomNumberInput(BaseModel):
    """Random number generation parameters."""

    min_value: Union[int, float] = Field(default=0, description="Minimum value (inclusive)")
    max_value: Union[int, float] = Field(default=100, description="Maximum value (inclusive)")
    number_type: str = Field(default="integer", description="Type of number: 'integer' or 'float'")
    count: int = Field(default=1, description="Number of random numbers to generate")


class RandomStringInput(BaseModel):
    """Random string generation parameters."""

    length: int = Field(default=10, description="Length of string to generate")
    character_set: CharacterSet = Field(default=CharacterSet.LETTERS_DIGITS, description="Character set to use")
    custom_characters: Optional[str] = Field(default=None, description="Custom characters when using CUSTOM set")
    count: int = Field(default=1, description="Number of random strings to generate")


class RandomChoiceInput(BaseModel):
    """Random choice from list parameters."""

    choices: List[str] = Field(description="List of options to choose from")
    count: int = Field(default=1, description="Number of items to select")
    replace: bool = Field(default=True, description="Whether to allow repeated selections")


class RandomBooleanInput(BaseModel):
    """Random boolean generation parameters."""

    probability: float = Field(default=0.5, description="Probability of True (0.0 to 1.0)")
    count: int = Field(default=1, description="Number of random booleans to generate")


class GeneratePasswordInput(BaseModel):
    """Password generation parameters."""

    length: int = Field(default=12, description="Length of password")
    include_uppercase: bool = Field(default=True, description="Include uppercase letters")
    include_lowercase: bool = Field(default=True, description="Include lowercase letters")
    include_digits: bool = Field(default=True, description="Include digits")
    include_symbols: bool = Field(default=True, description="Include symbols")
    exclude_ambiguous: bool = Field(default=False, description="Exclude ambiguous characters (0, O, l, I)")
    count: int = Field(default=1, description="Number of passwords to generate")


# =============================================================================
# Utility Functions
# =============================================================================


def get_character_set(character_set: CharacterSet, custom_characters: Optional[str] = None) -> str:
    """Get the actual character string for a given character set."""
    if character_set == CharacterSet.LETTERS:
        return string.ascii_letters
    elif character_set == CharacterSet.DIGITS:
        return string.digits
    elif character_set == CharacterSet.LETTERS_DIGITS:
        return string.ascii_letters + string.digits
    elif character_set == CharacterSet.LOWERCASE:
        return string.ascii_lowercase
    elif character_set == CharacterSet.UPPERCASE:
        return string.ascii_uppercase
    elif character_set == CharacterSet.PUNCTUATION:
        return string.punctuation
    elif character_set == CharacterSet.ALPHANUMERIC:
        return string.ascii_letters + string.digits
    elif character_set == CharacterSet.ALL_PRINTABLE:
        return string.printable.replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "")
    elif character_set == CharacterSet.CUSTOM:
        return custom_characters or string.ascii_letters + string.digits
    else:
        return string.ascii_letters + string.digits


# =============================================================================
# Tool Implementations
# =============================================================================


@tool("generate_random_number", args_schema=RandomNumberInput)
def generate_number(
    min_value: Union[int, float] = 0, max_value: Union[int, float] = 100, number_type: str = "integer", count: int = 1
) -> Dict[str, Any]:
    """
    Use it to generate one or more random numbers within specified range.

    Returns:
        Dictionary containing random number generation results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'value': (int/float or list) The generated random number(s) - single value if count=1, list if count>1
          - 'range_min': (int/float) Minimum value in range
          - 'range_max': (int/float) Maximum value in range
          - 'number_type': (string) Type of number generated (integer/float)
          - 'count': (integer) Number of values generated
        - 'error': (string, optional) Error message if generation failed
    """
    try:
        if min_value > max_value:
            return ToolResult.failure("Minimum value cannot be greater than maximum value").model_dump()

        if count <= 0:
            return ToolResult.failure("Count must be greater than 0").model_dump()

        values: List[int | float] = []
        if number_type.lower() == "integer":
            values = [random.randint(int(min_value), int(max_value)) for _ in range(count)]
            result_type = "integer"
        elif number_type.lower() == "float":
            values = [random.uniform(float(min_value), float(max_value)) for _ in range(count)]
            result_type = "float"
        else:
            return ToolResult.failure(f"Invalid number type: {number_type}. Use 'integer' or 'float'").model_dump()

        # Return single value if count=1, otherwise return list
        result_value = values[0] if count == 1 else values

        return ToolResult.success(
            {
                "value": result_value,
                "range_min": min_value,
                "range_max": max_value,
                "number_type": result_type,
                "count": count,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error generating random number: {str(e)}").model_dump()


@tool("generate_random_string", args_schema=RandomStringInput)
def generate_string(
    length: int = 10,
    character_set: CharacterSet = CharacterSet.LETTERS_DIGITS,
    custom_characters: Optional[str] = None,
    count: int = 1,
) -> Dict[str, Any]:
    """
    Use it to generate one or more random strings with specified length and character set.

    Returns:
        Dictionary containing random string generation results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'value': (string or list) The generated random string(s) - single string if count=1, list if count>1
          - 'length': (integer) Length of each generated string
          - 'character_set': (string) Character set used
          - 'available_characters': (string) Characters available for selection
          - 'entropy_bits': (float) Approximate entropy in bits per string
          - 'count': (integer) Number of strings generated
        - 'error': (string, optional) Error message if generation failed
    """
    try:
        if length <= 0:
            return ToolResult.failure("Length must be greater than 0").model_dump()

        if count <= 0:
            return ToolResult.failure("Count must be greater than 0").model_dump()

        available_chars = get_character_set(character_set, custom_characters)

        if not available_chars:
            return ToolResult.failure("No characters available for string generation").model_dump()

        # Generate random strings
        values = ["".join(random.choice(available_chars) for _ in range(length)) for _ in range(count)]

        # Calculate approximate entropy
        import math

        entropy_bits = length * math.log2(len(available_chars)) if len(available_chars) > 1 else 0

        # Return single string if count=1, otherwise return list
        result_value = values[0] if count == 1 else values

        return ToolResult.success(
            {
                "value": result_value,
                "length": length,
                "character_set": character_set.value,
                "available_characters": available_chars,
                "entropy_bits": round(entropy_bits, 2),
                "count": count,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error generating random string: {str(e)}").model_dump()


@tool("choose_from_list_randomly", args_schema=RandomChoiceInput)
def choose_from_list(choices: List[str], count: int = 1, replace: bool = True) -> Dict[str, Any]:
    """
    Use it to randomly select items from a list of choices.

    Returns:
        Dictionary containing random choice results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'selected': (list) List of selected items
          - 'original_choices': (list) Original list of choices
          - 'count_requested': (integer) Number of items requested
          - 'count_selected': (integer) Number of items actually selected
          - 'with_replacement': (boolean) Whether replacement was allowed
        - 'error': (string, optional) Error message if selection failed
    """
    try:
        if not choices:
            return ToolResult.failure("Choices list cannot be empty").model_dump()

        if count <= 0:
            return ToolResult.failure("Count must be greater than 0").model_dump()

        if not replace and count > len(choices):
            return ToolResult.failure("Count cannot exceed number of choices when replacement is disabled").model_dump()

        if replace:
            selected = [random.choice(choices) for _ in range(count)]
        else:
            selected = random.sample(choices, count)

        return ToolResult.success(
            {
                "selected": selected,
                "original_choices": choices,
                "count_requested": count,
                "count_selected": len(selected),
                "with_replacement": replace,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error selecting from choices: {str(e)}").model_dump()


@tool("generate_random_boolean", args_schema=RandomBooleanInput)
def generate_boolean(probability: float = 0.5, count: int = 1) -> Dict[str, Any]:
    """
    Use it to generate one or more random boolean values with specified probability.

    Returns:
        Dictionary containing random boolean generation results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'value': (boolean or list) The generated boolean value(s) - single boolean if count=1, list if count>1
          - 'probability': (float) Probability of True used
          - 'random_values': (float or list) The random value(s) that determined result(s)
          - 'count': (integer) Number of booleans generated
        - 'error': (string, optional) Error message if generation failed
    """
    try:
        if not 0.0 <= probability <= 1.0:
            return ToolResult.failure("Probability must be between 0.0 and 1.0").model_dump()

        if count <= 0:
            return ToolResult.failure("Count must be greater than 0").model_dump()

        random_values = [random.random() for _ in range(count)]
        values = [rv < probability for rv in random_values]

        # Return single value if count=1, otherwise return list
        result_value = values[0] if count == 1 else values
        result_random_values = round(random_values[0], 6) if count == 1 else [round(rv, 6) for rv in random_values]

        return ToolResult.success(
            {
                "value": result_value,
                "probability": probability,
                "random_values": result_random_values,
                "count": count,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error generating random boolean: {str(e)}").model_dump()


@tool("generate_uuid")
def generate_uuid() -> Dict[str, Any]:
    """
    Use it to generate a random UUID (Universally Unique Identifier).

    Returns:
        Dictionary containing UUID generation results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'uuid': (string) The generated UUID string
          - 'version': (integer) UUID version (4 for random)
          - 'format': (string) UUID format description
          - 'hex': (string) UUID as hex string without dashes
        - 'error': (string, optional) Error message if generation failed
    """
    try:
        generated_uuid = uuid.uuid4()

        return ToolResult.success(
            {
                "uuid": str(generated_uuid),
                "version": 4,
                "format": "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx",
                "hex": generated_uuid.hex,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error generating UUID: {str(e)}").model_dump()


@tool("generate_password", args_schema=GeneratePasswordInput)
def generate_password(
    length: int = 12,
    include_uppercase: bool = True,
    include_lowercase: bool = True,
    include_digits: bool = True,
    include_symbols: bool = True,
    exclude_ambiguous: bool = False,
    count: int = 1,
) -> Dict[str, Any]:
    """
    Use it to generate one or more random passwords with specified criteria.

    Returns:
        Dictionary containing password generation results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'password': (string or list) The generated password(s) - single password if count=1, list if count>1
          - 'length': (integer) Password length
          - 'character_sets_used': (list) List of character sets included
          - 'strength_estimate': (string) Rough strength estimate
          - 'entropy_bits': (float) Approximate entropy in bits
          - 'count': (integer) Number of passwords generated
        - 'error': (string, optional) Error message if generation failed
    """
    try:
        if length <= 0:
            return ToolResult.failure("Password length must be greater than 0").model_dump()

        if count <= 0:
            return ToolResult.failure("Count must be greater than 0").model_dump()

        # Build character set
        characters = ""
        character_sets_used = []

        if include_lowercase:
            chars = string.ascii_lowercase
            if exclude_ambiguous:
                chars = chars.replace("l", "").replace("o", "")
            characters += chars
            character_sets_used.append("lowercase")

        if include_uppercase:
            chars = string.ascii_uppercase
            if exclude_ambiguous:
                chars = chars.replace("I", "").replace("O", "")
            characters += chars
            character_sets_used.append("uppercase")

        if include_digits:
            chars = string.digits
            if exclude_ambiguous:
                chars = chars.replace("0", "").replace("1", "")
            characters += chars
            character_sets_used.append("digits")

        if include_symbols:
            chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            characters += chars
            character_sets_used.append("symbols")

        if not characters:
            return ToolResult.failure("At least one character set must be enabled").model_dump()

        # Generate passwords
        passwords = ["".join(random.choice(characters) for _ in range(length)) for _ in range(count)]

        # Calculate entropy
        import math

        entropy_bits = length * math.log2(len(characters)) if len(characters) > 1 else 0

        # Rough strength estimate
        if entropy_bits < 30:
            strength = "weak"
        elif entropy_bits < 50:
            strength = "moderate"
        elif entropy_bits < 70:
            strength = "strong"
        else:
            strength = "very strong"

        # Return single password if count=1, otherwise return list
        result_password = passwords[0] if count == 1 else passwords

        return ToolResult.success(
            {
                "password": result_password,
                "length": length,
                "character_sets_used": character_sets_used,
                "strength_estimate": strength,
                "entropy_bits": round(entropy_bits, 2),
                "count": count,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error generating password: {str(e)}").model_dump()
