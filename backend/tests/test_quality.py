import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from quality import build_quality_report  # noqa: E402


class TestQualityContracts(unittest.TestCase):
    def test_quality_report_passes_for_valid_input(self):
        df = pd.DataFrame(
            {
                "state": ["A", "A", "B", "B"],
                "year": [2021, 2022, 2021, 2022],
                "deaths": [10, 12, 20, 22],
                "crude_rate": [1.1, 1.2, 2.1, 2.2],
                "population": [1000, 1005, 1100, 1110],
            }
        )
        report = build_quality_report(df)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["fail_count"], 0)

    def test_quality_report_fails_missing_columns(self):
        df = pd.DataFrame({"state": ["A"], "year": [2022], "deaths": [5]})
        report = build_quality_report(df)
        self.assertEqual(report["status"], "fail")
        failed = [c for c in report["checks"] if c["status"] == "fail"]
        self.assertTrue(any(c["name"] == "required_columns_present" for c in failed))


if __name__ == "__main__":
    unittest.main()
