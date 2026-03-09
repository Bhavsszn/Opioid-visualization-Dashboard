import os
import sqlite3
import subprocess
import sys
import time
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"


def run(cmd: list[str], cwd: Path) -> None:
    print(f"\n>> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(cwd), check=True)


def npm_executable() -> str:
    # On Windows, npm is typically exposed as npm.cmd rather than npm.
    candidates = ["npm.cmd", "npm"]
    for name in candidates:
        path = shutil.which(name)
        if path:
            return path
    raise FileNotFoundError(
        "Could not find npm executable. Ensure Node.js is installed and npm is on PATH."
    )


def ensure_frontend_deps() -> None:
    node_modules = FRONTEND / "node_modules"
    if not node_modules.exists():
        run([npm_executable(), "install"], FRONTEND)

def db_ready() -> bool:
    db_path = ROOT / "data" / "opioid.db"
    if not db_path.exists():
        return False
    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='state_year_overdoses'"
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def start_backend() -> subprocess.Popen:
    print("\n>> Starting backend on http://127.0.0.1:8000")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api:app", "--reload", "--port", "8000"],
        cwd=str(BACKEND),
    )


def start_frontend(use_static: bool) -> subprocess.Popen:
    env = os.environ.copy()
    env.setdefault("VITE_USE_STATIC", "true" if use_static else "false")
    env.setdefault("VITE_API_BASE", "http://127.0.0.1:8000")
    mode = "static" if use_static else "live API"
    print("\n>> Starting frontend on http://127.0.0.1:5173")
    print(f">> Frontend mode: {mode}")
    return subprocess.Popen([npm_executable(), "run", "dev"], cwd=str(FRONTEND), env=env)


def main() -> None:
    # Build/refresh database so live API mode has data for charts.
    try:
        run([sys.executable, "etl.py"], BACKEND)
    except subprocess.CalledProcessError:
        print("\n>> ETL failed. Falling back to static frontend mode.")

    run([sys.executable, "export_static.py"], BACKEND)
    ensure_frontend_deps()

    backend_proc = start_backend()
    time.sleep(1.0)
    try:
        frontend_proc = start_frontend(use_static=not db_ready())
    except Exception:
        if backend_proc.poll() is None:
            backend_proc.terminate()
            try:
                backend_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_proc.kill()
        raise

    try:
        while True:
            if backend_proc.poll() is not None:
                raise RuntimeError("Backend process exited unexpectedly")
            if frontend_proc.poll() is not None:
                raise RuntimeError("Frontend process exited unexpectedly")
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        for proc in (frontend_proc, backend_proc):
            if proc.poll() is None:
                proc.terminate()
        for proc in (frontend_proc, backend_proc):
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    main()
