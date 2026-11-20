from fastapi import APIRouter

from app.api.client import router as client_router


router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


router.include_router(client_router)