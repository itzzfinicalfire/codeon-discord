"""Bootstrap script to run the Discord bot with automatic dependency install."""
from __future__ import annotations

import asyncio
import importlib.util
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
REQUIREMENTS_PATH = PROJECT_ROOT / "requirements.txt"
SRC_PATH = PROJECT_ROOT / "src"


def ensure_dependencies() -> None:
    """Install dependencies from requirements.txt if discord is missing.

    Uses importlib to avoid try/except around imports while still detecting
    whether the package is available in the current environment.
    """

    if importlib.util.find_spec("discord") is not None:
        return

    if not REQUIREMENTS_PATH.exists():
        raise RuntimeError("requirements.txt is missing; cannot install dependencies.")

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(REQUIREMENTS_PATH)]
    )


def add_src_to_path() -> None:
    if SRC_PATH.exists():
        sys.path.insert(0, str(SRC_PATH))


async def run_bot() -> None:
    from src.bot import main as bot_main

    await bot_main()


if __name__ == "__main__":
    ensure_dependencies()
    add_src_to_path()
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass
