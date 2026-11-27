from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Nutrimax API"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/nutrimax"
    api_v1_prefix: str = "/api/v1"
    jwt_secret_key: str = "change-this-secret-in-production"
    access_token_expire_minutes: int = 30
    upload_dir: str = "uploads/meals"
    google_ai_studio_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-3.5-flash"
    gemini_api_url: str = "https://generativelanguage.googleapis.com/v1beta/models"
    gemini_timeout_seconds: float = 60.0
    gemini_max_retries: int = 2
    gemini_retry_backoff_seconds: float = 2.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
