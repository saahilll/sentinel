"""
Custom exception hierarchy for consistent error handling.
"""

from fastapi import HTTPException, status


class SentinelException(Exception):
    """Base exception for all Sentinel errors."""

    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(SentinelException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message)


class TokenExpiredError(SentinelException):
    """Raised when a token (access, refresh, magic link) has expired."""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)


class RateLimitError(SentinelException):
    """Raised when a rate limit is exceeded."""

    def __init__(self, message: str = "Too many requests. Please wait."):
        super().__init__(message)


class AuthorizationError(SentinelException):
    """Raised when user lacks permission."""

    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(message)


class NotFoundError(SentinelException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found")


class ConflictError(SentinelException):
    """Raised when a resource already exists."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message)


# HTTP Exception factories for FastAPI
def credentials_exception() -> HTTPException:
    """Standard 401 exception for invalid credentials."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden_exception(detail: str = "Not enough permissions") -> HTTPException:
    """Standard 403 exception for authorization failures."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


def not_found_exception(resource: str = "Resource") -> HTTPException:
    """Standard 404 exception."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found",
    )


def conflict_exception(detail: str = "Resource already exists") -> HTTPException:
    """Standard 409 exception for conflicts."""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail,
    )
