"""Watch a .env file for changes and auto-reload the active pinned profile."""

import time
import os
from pathlib import Path
from typing import Callable, Optional


class WatchError(Exception):
    pass


def get_mtime(path: Path) -> Optional[float]:
    """Return the modification time of a file, or None if it doesn't exist."""
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return None


def watch_file(
    path: Path,
    callback: Callable[[Path], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Poll a file for changes and invoke callback when it changes.

    Args:
        path: Path to the file to watch.
        callback: Called with the path when a change is detected.
        interval: Polling interval in seconds.
        max_iterations: Stop after this many iterations (useful for testing).
    """
    if not path.exists():
        raise WatchError(f"File not found: {path}")

    last_mtime = get_mtime(path)
    iterations = 0

    while True:
        time.sleep(interval)
        current_mtime = get_mtime(path)

        if current_mtime is None:
            raise WatchError(f"File disappeared during watch: {path}")

        if current_mtime != last_mtime:
            last_mtime = current_mtime
            callback(path)

        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break


def make_reload_callback(
    profile_name: str,
    apply_fn: Callable[[str, Path], None],
    target: Path,
) -> Callable[[Path], None]:
    """Create a callback that applies a profile to a target .env file on change."""
    def _callback(changed_path: Path) -> None:
        apply_fn(profile_name, target)

    return _callback
