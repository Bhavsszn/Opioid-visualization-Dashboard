import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"


def run(cmd: list[str], cwd: Path) -> None:
    print(f"\n>> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(cwd), check=True)


def ensure_frontend_deps() -> None:
    node_modules = FRONTEND / "node_modules"
    if not node_modules.exists():
        run(["npm", "install"], FRONTEND)


def start_backend() -> subprocess.Popen:
    print("\n>> Starting backend on http://127.0.0.1:8000")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api:app", "--reload", "--port", "8000"],
        cwd=str(BACKEND),
    )


def start_frontend() -> subprocess.Popen:
    env = os.environ.copy()
    env.setdefault("VITE_USE_STATIC", "false")
    env.setdefault("VITE_API_BASE", "http://127.0.0.1:8000")
    print("\n>> Starting frontend on http://127.0.0.1:5173")
    return subprocess.Popen(["npm", "run", "dev"], cwd=str(FRONTEND), env=env)


def main() -> None:
    run([sys.executable, "export_static.py"], BACKEND)
    ensure_frontend_deps()

    backend_proc = start_backend()
    time.sleep(1.0)
    frontend_proc = start_frontend()

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
