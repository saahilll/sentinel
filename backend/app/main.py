"""
Sentinel Core - AI-Native ITSM Platform Backend
Entry point for the FastAPI application.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.auth.router import router as auth_router
from app.core.database import init_db
from app.core.middleware import SecurityHeadersMiddleware

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    await init_db()
    print("✅ Database initialized")
    yield
    print("👋 Shutting down Sentinel Core")


app = FastAPI(
    title="Sentinel Core",
    description="AI-Native ITSM Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# Attach rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount feature routers
app.include_router(auth_router, prefix="/api")


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint."""
    return {"message": "Welcome to Sentinel Core", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "operational"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)