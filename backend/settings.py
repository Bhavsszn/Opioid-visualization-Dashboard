"""Centralized backend settings/configuration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    env_name: str = Field(default="dev")
    data_dir: Path = Field(default=ROOT / "data")
    db_path: Path = Field(default=ROOT / "data" / "opioid.db")
    static_api_dir: Path = Field(default=ROOT / "frontend" / "public" / "api")
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    default_forecast_horizon: int = Field(default=3, ge=1)

    @staticmethod
    def _parse_origins(raw: str, env_name: str) -> list[str]:
        raw = raw.strip()
        if not raw:
            # Preserve current permissive behavior in development.
            if env_name.lower() in {"dev", "development", "local"}:
                return ["*"]
            return []
        if raw == "*":
            return ["*"]
        return [item.strip() for item in raw.split(",") if item.strip()]

    @classmethod
    def from_env(cls) -> "Settings":
        env_name = os.getenv("APP_ENV", "dev")
        data_dir = Path(os.getenv("DATA_DIR", str(ROOT / "data")))
        db_path = Path(os.getenv("DB_PATH", str(data_dir / "opioid.db")))
        static_api_dir = Path(
            os.getenv("STATIC_API_DIR", os.getenv("STATIC_OUT_DIR", str(ROOT / "frontend" / "public" / "api")))
        )
        cors_origins = cls._parse_origins(os.getenv("CORS_ORIGINS", ""), env_name)
        default_horizon = int(os.getenv("DEFAULT_FORECAST_HORIZON", "3"))
        return cls(
            env_name=env_name,
            data_dir=data_dir,
            db_path=db_path,
            static_api_dir=static_api_dir,
            cors_origins=cors_origins,
            default_forecast_horizon=default_horizon,
        )


settings = Settings.from_env()
