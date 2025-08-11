"""
Custom exceptions for the assistant server.
"""


class AssistantError(Exception):
    """Base exception for assistant server errors."""

    def __init__(self, message: str, detail: str = ""):
        self.message = message
        self.detail = detail
        super().__init__(message)


class UserError(AssistantError):
    """User-related errors."""

    def __init__(self, message: str, detail: str = ""):
        super().__init__(message, detail)
        self.message = message
        self.detail = detail


class UserNotFoundError(UserError):
    """User not found error."""

    def __init__(self, user_id: str):
        super().__init__(f"User with ID {user_id} not found")
        self.user_id = user_id


class UserAlreadyExistsError(UserError):
    """User already exists error."""

    def __init__(self, user_id: str):
        super().__init__(f"User with ID {user_id} already exists")
        self.user_id = user_id


class InvalidCredentialsError(UserError):
    """Invalid credentials error."""

    def __init__(self, message: str = "Invalid credentials provided"):
        super().__init__(message)
        self.message = message


class AuthenticationError(AssistantError):
    """Authentication-related errors."""

    def __init__(self, message: str, detail: str = ""):
        super().__init__(message, detail)
        self.message = message
        self.detail = detail


class AuthorizationError(AssistantError):
    """Authorization-related errors."""

    def __init__(self, message: str, detail: str = ""):
        super().__init__(message, detail)
        self.message = message
        self.detail = detail


class ValidationError(AssistantError):
    """Data validation errors."""

    def __init__(self, message: str, detail: str = ""):
        super().__init__(message, detail)
        self.message = message
        self.detail = detail


class TokenExpiredError(AssistantError):
    """Token expired error."""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)
        self.message = message
