import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class TestAPIContracts(unittest.TestCase):
    def test_forecast_and_quality_shapes(self):
        with tempfile.TemporaryDirectory(dir=str(BACKEND_DIR / "tests")) as tmpdir:
            db_path = Path(tmpdir) / "opioid.db"
            conn = sqlite3.connect(db_path)
            conn.execute(
                "CREATE TABLE state_year_overdoses (year INTEGER, state TEXT, deaths REAL, population REAL, crude_rate REAL, age_adjusted_rate REAL)"
            )
            rows = [
                (2018, "Kansas", 100.0, 2000.0, 10.0, 9.5),
                (2019, "Kansas", 110.0, 2010.0, 11.0, 10.2),
                (2020, "Kansas", 120.0, 2020.0, 12.0, 11.4),
                (2021, "Kansas", 130.0, 2030.0, 13.0, 12.7),
                (2022, "Kansas", 140.0, 2040.0, 14.0, 13.8),
            ]
            conn.executemany("INSERT INTO state_year_overdoses VALUES (?, ?, ?, ?, ?, ?)", rows)
            conn.commit()
            conn.close()

            import api  # noqa: E402

            old_db = api.DB_PATH
            api.DB_PATH = str(db_path)
            try:
                forecast_json = api.forecast_simple("Kansas", 2)
                for key in ["model_name", "train_start_year", "train_end_year", "mae", "mape", "interval_coverage"]:
                    self.assertIn(key, forecast_json)

                quality_json = api.quality_status()
                self.assertIn("status", quality_json)
                self.assertIn("checked_at", quality_json)
                self.assertIn("checks", quality_json)
                self.assertIn("summary", quality_json)
            finally:
                api.DB_PATH = old_db


if __name__ == "__main__":
    unittest.main()
