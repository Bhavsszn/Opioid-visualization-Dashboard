import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    cmd = [
        sys.executable,
        "-m",
        "coverage",
        "run",
        "-m",
        "unittest",
        "discover",
        "-s",
        "backend/tests",
        "-p",
        "test_*.py",
        "-v",
    ]
    print(f">> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(ROOT), check=True)

    report = [sys.executable, "-m", "coverage", "report", "--fail-under=70"]
    print(f">> {' '.join(report)}")
    subprocess.run(report, cwd=str(ROOT), check=True)


if __name__ == "__main__":
    main()
