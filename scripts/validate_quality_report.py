import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUALITY_PATH = ROOT / "frontend" / "public" / "api" / "quality_report.json"


def main() -> None:
    if not QUALITY_PATH.exists():
        raise SystemExit(f"Missing quality report: {QUALITY_PATH}")

    report = json.loads(QUALITY_PATH.read_text(encoding="utf-8"))
    status = report.get("status")
    fail_count = report.get("summary", {}).get("fail_count", 0)
    print(f"Quality status: {status}; failed checks: {fail_count}")
    if status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
