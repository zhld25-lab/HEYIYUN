from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # General
    APP_NAME_CN: str = "中国电力工程企业项目经营管理平台"
    APP_NAME_EN: str = "Power Engineering ERP & Project Management Platform"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "change-me-in-production-please-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Database — individual fields (local / Docker)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "power_engineering_erp"
    POSTGRES_USER: str = "erp_user"
    POSTGRES_PASSWORD: str = "erp_password"

    # Railway injects a single DATABASE_URL; takes priority when set
    DATABASE_URL: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # CORS — allow all origins by default so Railway frontend/Streamlit Cloud can connect
    BACKEND_CORS_ORIGINS: str = "*"

    @property
    def database_url(self) -> str:
        # Railway provides postgresql://... — convert to psycopg2 scheme
        raw = self.DATABASE_URL or os.environ.get("DATABASE_URL", "")
        if raw:
            return raw.replace("postgresql://", "postgresql+psycopg2://", 1) \
                      .replace("postgres://", "postgresql+psycopg2://", 1)
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def cors_origins(self) -> list[str]:
        if self.BACKEND_CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
