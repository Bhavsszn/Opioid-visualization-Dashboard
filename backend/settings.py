"""Centralized application settings loaded from environment variables."""

from __future__ import annotations

from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Runtime configuration for the analytics API."""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).with_name(".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = Field(default="dev", validation_alias=AliasChoices("ENVIRONMENT", "APP_ENV"))

    data_dir: Path = Field(default=ROOT_DIR / "data", validation_alias=AliasChoices("DATA_DIR"))
    db_path: Path = Field(default=ROOT_DIR / "data" / "opioid.db", validation_alias=AliasChoices("DB_PATH"))
    static_api_dir: Path = Field(
        default=ROOT_DIR / "frontend" / "public" / "api",
        validation_alias=AliasChoices("STATIC_API_DIR", "STATIC_OUT_DIR"),
    )

    db_backend: str = Field(default="postgres", validation_alias=AliasChoices("DB_BACKEND"))
    postgres_host: str = Field(default="localhost", validation_alias=AliasChoices("POSTGRES_HOST"))
    postgres_port: int = Field(default=5432, validation_alias=AliasChoices("POSTGRES_PORT"))
    postgres_db: str = Field(default="opioid", validation_alias=AliasChoices("POSTGRES_DB"))
    postgres_user: str = Field(default="postgres", validation_alias=AliasChoices("POSTGRES_USER"))
    postgres_password: str = Field(default="postgres", validation_alias=AliasChoices("POSTGRES_PASSWORD"))
    postgres_schema: str = Field(default="analytics", validation_alias=AliasChoices("POSTGRES_SCHEMA"))
    postgres_sslmode: str = Field(default="prefer", validation_alias=AliasChoices("POSTGRES_SSLMODE"))
    database_url: str | None = Field(default=None, validation_alias=AliasChoices("DATABASE_URL"))

    databricks_host: str | None = Field(default=None, validation_alias=AliasChoices("DATABRICKS_HOST"))
    databricks_http_path: str | None = Field(default=None, validation_alias=AliasChoices("DATABRICKS_HTTP_PATH"))
    databricks_token: str | None = Field(default=None, validation_alias=AliasChoices("DATABRICKS_TOKEN"))

    default_forecast_horizon: int = Field(
        default=3, ge=1, le=20, validation_alias=AliasChoices("DEFAULT_FORECAST_HORIZON")
    )
    allowed_cors_origins: list[str] = Field(
        default_factory=lambda: ["http://127.0.0.1:5173", "http://localhost:5173"],
        validation_alias=AliasChoices("ALLOWED_CORS_ORIGINS", "CORS_ORIGINS"),
    )

    enable_static_fallback: bool = Field(default=False, validation_alias=AliasChoices("ENABLE_STATIC_FALLBACK"))
    enable_sqlite_fallback: bool = Field(default=False, validation_alias=AliasChoices("ENABLE_SQLITE_FALLBACK"))
    slow_request_ms: int = Field(default=750, ge=1, validation_alias=AliasChoices("SLOW_REQUEST_MS"))

    @field_validator("allowed_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if value is None:
            return ["http://127.0.0.1:5173", "http://localhost:5173"]
        if isinstance(value, list):
            cleaned = [str(item).strip() for item in value if str(item).strip()]
            return cleaned or ["http://127.0.0.1:5173", "http://localhost:5173"]
        raw = str(value).strip()
        if not raw:
            return ["http://127.0.0.1:5173", "http://localhost:5173"]
        return [part.strip() for part in raw.split(",") if part.strip()]

    @field_validator("db_backend")
    @classmethod
    def validate_backend(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in {"postgres", "sqlite"}:
            raise ValueError("DB_BACKEND must be 'postgres' or 'sqlite'")
        return normalized

    @property
    def postgres_dsn(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}?sslmode={self.postgres_sslmode}"
        )


settings = Settings()
