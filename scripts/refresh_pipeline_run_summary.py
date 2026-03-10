"""Refresh analytics.pipeline_run_summary from current local source + quality status."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "populate_postgres_serving_tables.py"),
        "--only",
        "pipeline_run_summary",
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
