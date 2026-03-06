import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"


def run(cmd: list[str], cwd: Path) -> None:
    print(f"\n>> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> None:
    # Export static files first
    run([sys.executable, "export_static.py"], BACKEND)

    # Ensure frontend dependencies exist
    node_modules = FRONTEND / "node_modules"
    if not node_modules.exists():
        run(["npm", "install"], FRONTEND)

    # Start the frontend app
    run(["npm", "run", "dev"], FRONTEND)


if __name__ == "__main__":
    main()
