"""
Global exception handlers for mapping domain exceptions to HTTP responses.
Eliminates try/except boilerplate from route handlers.
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    SentinelException,
    TokenExpiredError,
)


async def authentication_error_handler(
    request: Request, exc: AuthenticationError
) -> JSONResponse:
    """Handle authentication failures → 401."""
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def token_expired_error_handler(
    request: Request, exc: TokenExpiredError
) -> JSONResponse:
    """Handle expired tokens → 401."""
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def authorization_error_handler(
    request: Request, exc: AuthorizationError
) -> JSONResponse:
    """Handle authorization failures → 403."""
    return JSONResponse(
        status_code=403,
        content={"detail": exc.message},
    )


async def not_found_error_handler(
    request: Request, exc: NotFoundError
) -> JSONResponse:
    """Handle resource not found → 404."""
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message},
    )


async def conflict_error_handler(
    request: Request, exc: ConflictError
) -> JSONResponse:
    """Handle resource conflicts → 409."""
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message},
    )


async def rate_limit_error_handler(
    request: Request, exc: RateLimitError
) -> JSONResponse:
    """Handle rate limit exceeded → 429."""
    return JSONResponse(
        status_code=429,
        content={"detail": exc.message},
    )


async def sentinel_error_handler(
    request: Request, exc: SentinelException
) -> JSONResponse:
    """Catch-all for unhandled Sentinel exceptions → 500."""
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred"},
    )


def register_exception_handlers(app) -> None:
    """Register all global exception handlers on the FastAPI app."""
    app.add_exception_handler(AuthenticationError, authentication_error_handler)
    app.add_exception_handler(TokenExpiredError, token_expired_error_handler)
    app.add_exception_handler(AuthorizationError, authorization_error_handler)
    app.add_exception_handler(NotFoundError, not_found_error_handler)
    app.add_exception_handler(ConflictError, conflict_error_handler)
    app.add_exception_handler(RateLimitError, rate_limit_error_handler)
    app.add_exception_handler(SentinelException, sentinel_error_handler)
