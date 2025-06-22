"""Custom exceptions for MyGH."""


class MyGHException(Exception):
    """Base exception for MyGH."""

    pass


class AuthenticationError(MyGHException):
    """Raised when authentication fails."""

    pass


class APIError(MyGHException):
    """Raised when GitHub API returns an error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(APIError):
    """Raised when GitHub API rate limit is exceeded."""

    pass


class ConfigurationError(MyGHException):
    """Raised when configuration is invalid."""

    pass
