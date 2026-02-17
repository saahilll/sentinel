from fastapi import APIRouter

from app.auth.routes.auth import router as auth_router
from app.auth.routes.invites import router as invites_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(invites_router)

__all__ = ["router"]
