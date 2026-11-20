from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.client import router as client_router
from app.api.dashboard import router as dashboard_router
from app.api.progress import router as progress_router


router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


router.include_router(auth_router)
router.include_router(client_router)
router.include_router(dashboard_router)
router.include_router(progress_router)