"""
Custom exceptions for the assistant server.
"""


class AssistantError(Exception):
    """Base exception for assistant server errors."""

    pass


class UserError(AssistantError):
    """User-related errors."""

    pass


class UserNotFoundError(UserError):
    """User not found error."""

    pass


class UserAlreadyExistsError(UserError):
    """User already exists error."""

    pass


class InvalidCredentialsError(UserError):
    """Invalid credentials error."""

    pass


class AuthenticationError(AssistantError):
    """Authentication-related errors."""

    pass


class AuthorizationError(AssistantError):
    """Authorization-related errors."""

    pass


class ValidationError(AssistantError):
    """Data validation errors."""

    pass
