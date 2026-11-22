from functools import lru_cache

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
