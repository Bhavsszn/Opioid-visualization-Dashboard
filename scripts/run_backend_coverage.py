import subprocess
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if importlib.util.find_spec("coverage") is None:
        print(">> coverage module not installed; running unit tests without coverage gate")
        fallback = [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "backend/tests",
            "-p",
            "test_*.py",
            "-v",
        ]
        print(f">> {' '.join(fallback)}")
        subprocess.run(fallback, cwd=str(ROOT), check=True)
        return

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
