"""Database access helpers for PostgreSQL analytics serving."""

from __future__ import annotations

from collections.abc import Iterable
from contextlib import contextmanager
from typing import Any

from settings import settings

try:
    import psycopg
    from psycopg.rows import dict_row
except Exception:  # pragma: no cover - optional local dependency
    psycopg = None
    dict_row = None


def _translate_sql(sql: str) -> str:
    """Translate sqlite-style placeholders to psycopg placeholders."""
    return sql.replace("?", "%s")


@contextmanager
def get_connection(db_path: str | None = None):
    """Yield configured PostgreSQL connection."""
    if psycopg is None:
        raise RuntimeError("psycopg is required for Postgres backend")
    conn = psycopg.connect(settings.postgres_dsn, row_factory=dict_row, autocommit=False)
    try:
        yield conn
    finally:
        conn.close()


def fetch_all(sql: str, params: Iterable[Any] = (), db_path: str | None = None) -> list[dict[str, Any]]:
    """Execute read query and return rows as dictionaries."""
    query = _translate_sql(sql)
    with get_connection(db_path=db_path) as conn:
        cur = conn.execute(query, tuple(params))
        rows = cur.fetchall()
    return [dict(row) for row in rows]


def fetch_one(sql: str, params: Iterable[Any] = (), db_path: str | None = None) -> dict[str, Any] | None:
    """Execute read query and return first row as dictionary."""
    query = _translate_sql(sql)
    with get_connection(db_path=db_path) as conn:
        row = conn.execute(query, tuple(params)).fetchone()
    if not row:
        return None
    return dict(row)


def ping() -> bool:
    """Check whether database can be reached."""
    try:
        with get_connection() as conn:
            conn.execute(_translate_sql("SELECT 1"))
        return True
    except Exception:
        return False
