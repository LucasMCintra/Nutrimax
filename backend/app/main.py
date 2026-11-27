from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API do sistema Nutrimax.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.api_v1_prefix)
