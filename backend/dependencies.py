"""FastAPI dependency providers."""

from __future__ import annotations

from fastapi import Request


def get_request_id(request: Request) -> str:
    """Return per-request ID populated by middleware."""
    return getattr(request.state, "request_id", "unknown")
