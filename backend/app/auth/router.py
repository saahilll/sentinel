"""
Auth module router.
Aggregates all auth-related routes.
"""

from fastapi import APIRouter

from app.auth.routes.auth import router as auth_router
from app.auth.routes.invites import router as invites_router

# Main auth module router
router = APIRouter()

# Include sub-routers
router.include_router(auth_router)  # /auth/*
router.include_router(invites_router)  # /{tenant}/invites/*
