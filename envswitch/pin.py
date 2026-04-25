"""Pin a profile to a specific project directory."""

import json
from pathlib import Path

PIN_FILENAME = ".envswitch-pin"


class PinError(Exception):
    pass


def get_pin_file(directory: str | None = None) -> Path:
    base = Path(directory) if directory else Path.cwd()
    return base / PIN_FILENAME


def pin_profile(profile_name: str, directory: str | None = None) -> Path:
    """Write a pin file associating a profile with a directory."""
    pin_file = get_pin_file(directory)
    data = {"profile": profile_name}
    pin_file.write_text(json.dumps(data) + "\n")
    return pin_file


def unpin_profile(directory: str | None = None) -> Path:
    """Remove the pin file from a directory."""
    pin_file = get_pin_file(directory)
    if not pin_file.exists():
        raise PinError(f"No pin file found in {pin_file.parent}")
    pin_file.unlink()
    return pin_file


def read_pin(directory: str | None = None) -> str | None:
    """Return the pinned profile name for a directory, or None if not pinned."""
    pin_file = get_pin_file(directory)
    if not pin_file.exists():
        return None
    try:
        data = json.loads(pin_file.read_text())
        return data.get("profile")
    except (json.JSONDecodeError, KeyError):
        raise PinError(f"Malformed pin file at {pin_file}")


def resolve_pin(directory: str | None = None) -> str | None:
    """Walk up the directory tree looking for a pin file."""
    start = Path(directory) if directory else Path.cwd()
    current = start.resolve()
    while True:
        candidate = current / PIN_FILENAME
        if candidate.exists():
            try:
                data = json.loads(candidate.read_text())
                return data.get("profile")
            except (json.JSONDecodeError, KeyError):
                return None
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None
