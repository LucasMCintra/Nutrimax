from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.client import router as client_router
from app.api.dashboard import router as dashboard_router
from app.api.progress import router as progress_router
from app.db import SessionLocal
from app.core.config import settings


router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", tags=["Health"])
def readiness_check() -> dict[str, str]:
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database is not ready") from error
    return {"status": "ready", "environment": settings.environment}


router.include_router(auth_router)
router.include_router(client_router)
router.include_router(dashboard_router)
router.include_router(progress_router)