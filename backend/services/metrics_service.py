"""Metric retrieval services (state-year and latest snapshots)."""

import pandas as pd

from db import query


def load_state_year_df() -> pd.DataFrame:
    """Load canonical state-year data from sqlite."""
    rows = query(
        """
        SELECT year, state, deaths, population, crude_rate, age_adjusted_rate
        FROM state_year_overdoses
        ORDER BY year, state
        """
    )
    if not rows:
        return pd.DataFrame(columns=["year", "state", "deaths", "population", "crude_rate", "age_adjusted_rate"])
    return pd.DataFrame(rows)


def get_state_year(state: str | None = None, year: int | None = None) -> dict:
    sql = "SELECT * FROM state_year_overdoses WHERE 1=1"
    params: list = []
    if state:
        sql += " AND state=?"
        params.append(state)
    if year:
        sql += " AND year=?"
        params.append(year)
    sql += " ORDER BY year, state"
    return {"rows": query(sql, tuple(params))}


def get_states_latest(year: int | None = None) -> dict:
    if year is None:
        max_year = query("SELECT MAX(year) AS y FROM state_year_overdoses")
        if not max_year or max_year[0]["y"] is None:
            return {"year": None, "rows": []}
        year = int(max_year[0]["y"])
    rows = query("SELECT * FROM state_year_overdoses WHERE year=? ORDER BY crude_rate DESC", (year,))
    return {"year": year, "rows": rows}
