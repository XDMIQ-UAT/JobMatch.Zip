from fastapi import APIRouter

from .assess import router as assess_router
from .matches import router as matches_router
from .profile import router as profile_router

router = APIRouter()

router.include_router(assess_router, prefix="/assess", tags=["assess"])
router.include_router(matches_router, prefix="/matches", tags=["matches"])
router.include_router(profile_router, prefix="/profile", tags=["profile"])
