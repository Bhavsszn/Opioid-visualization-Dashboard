import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import etl  # noqa: E402


class TestTransforms(unittest.TestCase):
    def test_to_num_parses_numeric_strings(self):
        self.assertEqual(etl._to_num("1,234"), 1234.0)
        self.assertAlmostEqual(etl._to_num("12.3 (CI)"), 12.3)
        self.assertTrue(math.isnan(etl._to_num("Suppressed")))

    def test_load_wonder_csv_filters_us_and_cleans_columns(self):
        csv_text = (
            "Year,State,Deaths,Population,Crude Rate,Age-adjusted Rate\n"
            "2021,Kansas,1000,2900,34.5,30.2\n"
            "2021,United States,999,100000,12.0,10.0\n"
            "2022,Kansas,Suppressed,2950,NA,29.1\n"
        )

        with tempfile.TemporaryDirectory(dir=str(BACKEND_DIR / "tests")) as tmpdir:
            csv_path = Path(tmpdir) / "sample.csv"
            csv_path.write_text(csv_text, encoding="utf-8")

            original_data_dir = etl.DATA_DIR
            etl.DATA_DIR = tmpdir
            try:
                df = etl.load_wonder_csv(str(csv_path))
            finally:
                etl.DATA_DIR = original_data_dir

            self.assertEqual(df["state"].nunique(), 1)
            self.assertEqual(df["state"].iloc[0], "Kansas")
            self.assertEqual(int(df["year"].iloc[0]), 2021)
            self.assertEqual(float(df["deaths"].iloc[0]), 1000.0)
            self.assertTrue((Path(tmpdir) / "overdoses_state_year_clean_typed.csv").exists())


if __name__ == "__main__":
    unittest.main()
