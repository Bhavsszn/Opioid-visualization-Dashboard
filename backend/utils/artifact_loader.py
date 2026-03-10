"""Helpers for loading static JSON artifacts when fallback mode is enabled."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from settings import settings


def load_artifact(name: str, base_dir: Path | None = None) -> dict[str, Any] | list[Any] | None:
    """Return parsed JSON artifact if present and static fallback is enabled."""
    if not settings.enable_static_fallback:
        return None

    path = (base_dir or settings.static_api_dir) / name
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
