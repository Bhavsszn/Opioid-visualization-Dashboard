from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from api import app  # noqa: E402
from settings import settings  # noqa: E402


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "opioid_test.db"
    static_dir = tmp_path / "api"
    static_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE state_year_overdoses (
            year INTEGER,
            state TEXT,
            deaths REAL,
            population REAL,
            crude_rate REAL,
            age_adjusted_rate REAL
        )
        """
    )

    rows = [
        (2016, "Kansas", 100, 2900000, 12.1, 11.2),
        (2017, "Kansas", 110, 2910000, 13.2, 12.1),
        (2018, "Kansas", 125, 2920000, 14.7, 13.3),
        (2019, "Kansas", 120, 2930000, 14.1, 13.0),
        (2020, "Kansas", 140, 2940000, 15.8, 14.2),
        (2021, "Kansas", 155, 2950000, 16.9, 15.1),
        (2022, "Kansas", 162, 2960000, 17.5, 15.9),
        (2023, "Kansas", 170, 2970000, 18.3, 16.4),
        (2022, "Texas", 900, 29000000, 12.0, 11.4),
        (2023, "Texas", 940, 29100000, 12.4, 11.8),
    ]
    conn.executemany("INSERT INTO state_year_overdoses VALUES (?, ?, ?, ?, ?, ?)", rows)
    conn.commit()
    conn.close()

    old_db = settings.db_path
    old_static = settings.static_api_dir
    settings.db_path = db_path
    settings.static_api_dir = static_dir

    try:
        yield TestClient(app)
    finally:
        settings.db_path = old_db
        settings.static_api_dir = old_static
