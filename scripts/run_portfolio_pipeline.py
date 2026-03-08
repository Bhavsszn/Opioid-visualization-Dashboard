import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    where = cwd or ROOT
    print(f">> {' '.join(cmd)} (cwd={where})")
    subprocess.run(cmd, cwd=str(where), check=True)


def main() -> None:
    run([sys.executable, "etl.py"], cwd=BACKEND)
    run([sys.executable, "export_static.py"], cwd=BACKEND)
    run([sys.executable, "scripts/run_transform_tests.py"])
    run([sys.executable, "scripts/validate_quality_report.py"])
    run(["cmd", "/c", "npm ci"], cwd=FRONTEND)
    run(["cmd", "/c", "npm run build"], cwd=FRONTEND)


if __name__ == "__main__":
    main()
