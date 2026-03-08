from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = ["state", "year", "deaths", "crude_rate", "population"]
MIN_NONNULL_RATE = {
    "state": 1.0,
    "year": 1.0,
    "deaths": 0.98,
    "crude_rate": 0.90,
    "population": 0.98,
}
MIN_LATEST_YEAR_COVERAGE = 0.95


def _check(name: str, passed: bool, value: Any, threshold: Any, detail: str) -> dict[str, Any]:
    return {
        "name": name,
        "status": "pass" if passed else "fail",
        "value": value,
        "threshold": threshold,
        "detail": detail,
    }


def build_quality_report(df: pd.DataFrame) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    checks.append(
        _check(
            "required_columns_present",
            len(missing_cols) == 0,
            {"missing": missing_cols},
            {"required": REQUIRED_COLUMNS},
            "Core schema columns must be present.",
        )
    )

    row_count = int(len(df))
    checks.append(
        _check(
            "row_count_positive",
            row_count > 0,
            row_count,
            "> 0",
            "Dataset must contain at least one row.",
        )
    )

    if row_count > 0:
        for col, min_rate in MIN_NONNULL_RATE.items():
            if col not in df.columns:
                continue
            rate = float(df[col].notna().mean())
            checks.append(
                _check(
                    f"nonnull_rate_{col}",
                    rate >= min_rate,
                    round(rate, 4),
                    min_rate,
                    f"Non-null coverage for {col}.",
                )
            )

    if all(c in df.columns for c in ["state", "year"]):
        dupes = int(df.duplicated(subset=["state", "year"]).sum())
        checks.append(
            _check(
                "state_year_unique",
                dupes == 0,
                dupes,
                0,
                "(state, year) should be unique.",
            )
        )

    if all(c in df.columns for c in ["state", "year"]):
        latest_year = int(pd.to_numeric(df["year"], errors="coerce").dropna().max())
        total_states = int(df["state"].nunique())
        latest_states = int(df[df["year"] == latest_year]["state"].nunique())
        coverage = float(latest_states / total_states) if total_states else 0.0
        checks.append(
            _check(
                "latest_year_coverage",
                coverage >= MIN_LATEST_YEAR_COVERAGE,
                round(coverage, 4),
                MIN_LATEST_YEAR_COVERAGE,
                "Share of states represented in latest year.",
            )
        )
    else:
        latest_year = None

    pass_count = sum(1 for c in checks if c["status"] == "pass")
    fail_count = sum(1 for c in checks if c["status"] == "fail")
    total = len(checks)
    pass_rate = float(pass_count / total) if total else 0.0

    return {
        "status": "pass" if fail_count == 0 else "fail",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "summary": {
            "rows": row_count,
            "columns": sorted(df.columns.tolist()),
            "latest_year": latest_year,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": round(pass_rate, 4),
        },
    }
