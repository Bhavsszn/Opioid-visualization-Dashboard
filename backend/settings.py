"""Centralized application settings loaded from environment variables."""

from __future__ import annotations

from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Runtime configuration for the analytics API."""

    model_config = SettingsConfigDict(env_file=str(Path(__file__).with_name(".env")), env_file_encoding="utf-8", extra="ignore")

    environment: str = Field(default="dev", validation_alias=AliasChoices("ENVIRONMENT", "APP_ENV"))
    data_dir: Path = Field(default=ROOT_DIR / "data", validation_alias=AliasChoices("DATA_DIR"))
    db_path: Path = Field(default=ROOT_DIR / "data" / "opioid.db", validation_alias=AliasChoices("DB_PATH"))
    static_api_dir: Path = Field(
        default=ROOT_DIR / "frontend" / "public" / "api",
        validation_alias=AliasChoices("STATIC_API_DIR", "STATIC_OUT_DIR"),
    )
    default_forecast_horizon: int = Field(
        default=3, ge=1, le=20, validation_alias=AliasChoices("DEFAULT_FORECAST_HORIZON")
    )
    allowed_cors_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        validation_alias=AliasChoices("ALLOWED_CORS_ORIGINS", "CORS_ORIGINS"),
    )

    @field_validator("allowed_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if value is None:
            return ["*"]
        if isinstance(value, list):
            cleaned = [str(item).strip() for item in value if str(item).strip()]
            return cleaned or ["*"]
        raw = str(value).strip()
        if not raw:
            return ["*"]
        if raw == "*":
            return ["*"]
        return [part.strip() for part in raw.split(",") if part.strip()]


settings = Settings()
