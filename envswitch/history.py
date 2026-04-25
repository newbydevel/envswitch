"""Track which profile was last applied per project directory."""

import json
import os
from pathlib import Path
from typing import Optional

HISTORY_FILE = "history.json"


def get_history_path() -> Path:
    base = Path(os.environ.get("ENVSWITCH_HOME", Path.home() / ".envswitch"))
    base.mkdir(parents=True, exist_ok=True)
    return base / HISTORY_FILE


def load_history(path: Optional[Path] = None) -> dict:
    p = path or get_history_path()
    if not p.exists():
        return {}
    with open(p, "r") as f:
        return json.load(f)


def save_history(history: dict, path: Optional[Path] = None) -> None:
    p = path or get_history_path()
    with open(p, "w") as f:
        json.dump(history, f, indent=2)


def record_apply(profile_name: str, directory: Optional[str] = None, path: Optional[Path] = None) -> None:
    """Record that a profile was applied in a given directory."""
    cwd = directory or os.getcwd()
    history = load_history(path)
    history[cwd] = profile_name
    save_history(history, path)


def get_last_applied(directory: Optional[str] = None, path: Optional[Path] = None) -> Optional[str]:
    """Return the last applied profile name for the given directory."""
    cwd = directory or os.getcwd()
    history = load_history(path)
    return history.get(cwd)


def clear_history(path: Optional[Path] = None) -> None:
    history_path = path or get_history_path()
    if history_path.exists():
        history_path.unlink()
