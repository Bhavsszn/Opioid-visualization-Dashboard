"""Database access helpers for sqlite-backed analytics data."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from typing import Any

from settings import settings


def _to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


@contextmanager
def get_connection(db_path: str | None = None):
    """Yield a sqlite connection configured to return dictionary-like rows."""
    conn = sqlite3.connect(db_path or str(settings.db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def fetch_all(sql: str, params: Iterable[Any] = (), db_path: str | None = None) -> list[dict[str, Any]]:
    """Execute a read query and return all rows as dictionaries."""
    with get_connection(db_path=db_path) as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()
    return [_to_dict(row) for row in rows]


def fetch_one(sql: str, params: Iterable[Any] = (), db_path: str | None = None) -> dict[str, Any] | None:
    """Execute a read query and return one row as a dictionary."""
    with get_connection(db_path=db_path) as conn:
        row = conn.execute(sql, tuple(params)).fetchone()
    return _to_dict(row) if row else None
