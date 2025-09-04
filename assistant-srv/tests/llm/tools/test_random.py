"""
Unit tests for random generation tools.
"""

from assistant.llm.tools.random import (
    GeneratePasswordInput,
    RandomBooleanInput,
    RandomChoiceInput,
    RandomNumberInput,
    RandomStringInput,
    choose_from_list,
    generate_boolean,
    generate_number,
    generate_password,
    generate_string,
    generate_uuid,
)


class TestRandomTools:
    """Test cases for random generation tools."""

    def test_generate_number_single(self) -> None:
        """Test generating a single random number."""
        tool_input = RandomNumberInput(min_value=1, max_value=10, count=1)
        result = generate_number.invoke(tool_input.model_dump())

        assert result["status"] == "success"
        assert isinstance(result["data"]["value"], (int, float))
        assert 1 <= result["data"]["value"] <= 10
        assert result["data"]["count"] == 1

    def test_generate_number_multiple(self) -> None:
        """Test generating multiple random numbers."""
        tool_input = RandomNumberInput(min_value=1, max_value=10, count=5)
        result = generate_number.invoke(tool_input.model_dump())

        assert result["status"] == "success"
        assert isinstance(result["data"]["value"], list)
        assert len(result["data"]["value"]) == 5
        assert all(1 <= val <= 10 for val in result["data"]["value"])
        assert result["data"]["count"] == 5

    def test_generate_string_single(self) -> None:
        """Test generating a single random string."""
        tool_input = RandomStringInput(length=8, count=1)
        result = generate_string.invoke(tool_input.model_dump())

        assert result["status"] == "success"
        assert isinstance(result["data"]["value"], str)
        assert len(result["data"]["value"]) == 8
        assert result["data"]["count"] == 1

    def test_generate_string_multiple(self) -> None:
        """Test generating multiple random strings."""
        tool_input = RandomStringInput(length=8, count=3)
        result = generate_string.invoke(tool_input.model_dump())

        assert result["status"] == "success"
        assert isinstance(result["data"]["value"], list)
        assert len(result["data"]["value"]) == 3
        assert all(len(s) == 8 for s in result["data"]["value"])
        assert result["data"]["count"] == 3

    def test_generate_boolean_single(self) -> None:
        """Test generating a single random boolean."""
        tool_input = RandomBooleanInput(probability=0.5, count=1)
        result = generate_boolean.invoke(tool_input.model_dump())

        assert result["status"] == "success"
        assert isinstance(result["data"]["value"], bool)
        assert result["data"]["count"] == 1

    def test_generate_boolean_multiple(self) -> None:
        """Test generating multiple random booleans."""
        tool_input = RandomBooleanInput(probability=0.5, count=4)
        result = generate_boolean.invoke(tool_input.model_dump())

        assert result["status"] == "success"
        assert isinstance(result["data"]["value"], list)
        assert len(result["data"]["value"]) == 4
        assert all(isinstance(b, bool) for b in result["data"]["value"])
        assert result["data"]["count"] == 4

    def test_generate_password_single(self) -> None:
        """Test generating a single random password."""
        tool_input = GeneratePasswordInput(length=12, count=1)
        result = generate_password.invoke(tool_input.model_dump())

        assert result["status"] == "success"
        assert isinstance(result["data"]["password"], str)
        assert len(result["data"]["password"]) == 12
        assert result["data"]["count"] == 1

    def test_generate_password_multiple(self) -> None:
        """Test generating multiple random passwords."""
        tool_input = GeneratePasswordInput(length=12, count=2)
        result = generate_password.invoke(tool_input.model_dump())

        assert result["status"] == "success"
        assert isinstance(result["data"]["password"], list)
        assert len(result["data"]["password"]) == 2
        assert all(len(p) == 12 for p in result["data"]["password"])
        assert result["data"]["count"] == 2

    def test_choose_from_list_single(self) -> None:
        """Test selecting a single item from list."""
        choices = ["apple", "banana", "cherry"]
        tool_input = RandomChoiceInput(choices=choices, count=1)
        result = choose_from_list.invoke(tool_input.model_dump())

        assert result["status"] == "success"
        assert isinstance(result["data"]["selected"], list)
        assert len(result["data"]["selected"]) == 1
        assert result["data"]["selected"][0] in choices

    def test_choose_from_list_multiple(self) -> None:
        """Test selecting multiple items from list."""
        choices = ["apple", "banana", "cherry", "date"]
        tool_input = RandomChoiceInput(choices=choices, count=2)
        result = choose_from_list.invoke(tool_input.model_dump())

        assert result["status"] == "success"
        assert isinstance(result["data"]["selected"], list)
        assert len(result["data"]["selected"]) == 2
        assert all(item in choices for item in result["data"]["selected"])

    def test_generate_uuid(self) -> None:
        """Test generating a UUID."""
        result = generate_uuid.invoke({})

        assert result["status"] == "success"
        assert "uuid" in result["data"]
        assert isinstance(result["data"]["uuid"], str)
        assert len(result["data"]["uuid"]) == 36  # UUID format length

    def test_error_handling(self) -> None:
        """Test error handling for invalid inputs."""
        # Test invalid count
        number_input = RandomNumberInput(count=0)
        result = generate_number.invoke(number_input.model_dump())
        assert result["status"] == "error"

        # Test invalid count for string
        string_count_input = RandomStringInput(count=0)
        result = generate_string.invoke(string_count_input.model_dump())
        assert result["status"] == "error"

        # Test invalid count for boolean
        boolean_count_input = RandomBooleanInput(count=0)
        result = generate_boolean.invoke(boolean_count_input.model_dump())
        assert result["status"] == "error"

        # Test invalid count for password
        password_count_input = GeneratePasswordInput(count=0)
        result = generate_password.invoke(password_count_input.model_dump())
        assert result["status"] == "error"

        # Test invalid length for string
        string_length_input = RandomStringInput(length=0)
        result = generate_string.invoke(string_length_input.model_dump())
        assert result["status"] == "error"

        # Test invalid length for password
        password_length_input = GeneratePasswordInput(length=0)
        result = generate_password.invoke(password_length_input.model_dump())
        assert result["status"] == "error"

        # Test empty choices
        choice_input = RandomChoiceInput(choices=[])
        result = choose_from_list.invoke(choice_input.model_dump())
        assert result["status"] == "error"
