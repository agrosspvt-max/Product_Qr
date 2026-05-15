"""Application configuration loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings driven by environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/product_qr"

    # JWT
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 720

    # Short link
    SHORT_DOMAIN: str = "https://qr.company.com"

    # Excel
    EXCEL_EXPORT_DIR: str = "./exports"

    # CORS — comma-separated origin list
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Logging
    LOG_LEVEL: str = "INFO"

    @field_validator("SHORT_DOMAIN")
    @classmethod
    def _strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/") if v else v

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
