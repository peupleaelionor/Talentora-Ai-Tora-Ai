from __future__ import annotations

import logging
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/talentora"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # AWS / S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "talentora-reports"
    AWS_REGION: str = "eu-west-1"

    # App
    ENVIRONMENT: str = "dev"
    LOG_LEVEL: str = "INFO"
    API_VERSION: str = "v1"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # ---------------------------------------------------------------------------
    # Derived / computed helpers
    # ---------------------------------------------------------------------------

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def log_level_int(self) -> int:
        return getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"dev", "staging", "prod"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
