"""Cross-platform development commands; run with the project virtual environment."""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def godot() -> str:
    executable = os.environ.get("GODOT_BIN") or shutil.which("godot") or shutil.which("godot4")
    if not executable:
        raise SystemExit("Set GODOT_BIN to the Godot 4.7.2 executable or add godot to PATH.")
    version = subprocess.check_output([executable, "--version"], text=True).strip()
    expected = (ROOT / ".godot-version").read_text().strip()
    if not version.startswith(expected + ".stable."):
        raise SystemExit(f"Expected Godot {expected} stable, got {version}")
    return executable


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["test", "check", "format", "validate", "api", "game", "godot-test"]
    )
    args = parser.parse_args()
    if args.command == "format":
        run(sys.executable, "-m", "ruff", "check", "--fix", ".")
        run(sys.executable, "-m", "ruff", "format", ".")
    elif args.command == "test":
        run(sys.executable, "-m", "pytest", "-q")
    elif args.command == "check":
        run(sys.executable, "-m", "ruff", "check", ".")
        run(sys.executable, "-m", "ruff", "format", "--check", ".")
        run(sys.executable, "-m", "mypy")
        run(sys.executable, "-m", "pytest", "-q")
        run(sys.executable, "tools/validate_world.py", "examples/blackwater_harbor.json")
        run(sys.executable, "tools/scan_secrets.py")
    elif args.command == "validate":
        run(sys.executable, "tools/validate_world.py", "examples/blackwater_harbor.json")
    elif args.command == "api":
        run(
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        )
    elif args.command == "game":
        run(godot(), "--path", "game")
    else:
        executable = godot()
        run(executable, "--headless", "--path", "game", "--editor", "--import", "--quit")
        run(executable, "--headless", "--path", "game", "--script", "res://tests/menu_smoke.gd")


if __name__ == "__main__":
    main()
