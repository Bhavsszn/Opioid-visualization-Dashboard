import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from forecast_eval import evaluate_state, forecast_state  # noqa: E402


class TestForecastEvaluation(unittest.TestCase):
    def test_evaluate_state_returns_metrics(self):
        df = pd.DataFrame(
            {
                "state": ["Kansas"] * 8,
                "year": list(range(2016, 2024)),
                "deaths": [100, 104, 108, 113, 117, 120, 122, 125],
            }
        )
        result = evaluate_state(df)
        self.assertIn(result["selected_model"], ["naive_last", "sarimax"])
        self.assertIsNotNone(result["mae"])
        self.assertIsNotNone(result["mape"])

    def test_forecast_state_shape(self):
        df = pd.DataFrame(
            {
                "state": ["Kansas"] * 8,
                "year": list(range(2016, 2024)),
                "deaths": [100, 101, 99, 102, 104, 107, 110, 112],
            }
        )
        forecast, metadata = forecast_state(df, horizon=3)
        self.assertEqual(len(forecast), 3)
        self.assertIn("forecast_deaths", forecast[0])
        self.assertIn("model_name", metadata)


if __name__ == "__main__":
    unittest.main()
