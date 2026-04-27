"""Profile locking — prevent accidental modification of a profile."""

import json
from pathlib import Path
from envswitch.storage import get_store_path


class LockError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _get_lock_file(store_path: Path | None = None) -> Path:
    base = store_path or get_store_path().parent
    return base / "locks.json"


def _load_locks(lock_file: Path) -> list[str]:
    if not lock_file.exists():
        return []
    with open(lock_file) as f:
        data = json.load(f)
    return data.get("locked", [])


def _save_locks(lock_file: Path, locked: list[str]) -> None:
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_file, "w") as f:
        json.dump({"locked": locked}, f, indent=2)


def lock_profile(name: str, lock_file: Path | None = None) -> None:
    lf = lock_file or _get_lock_file()
    locked = _load_locks(lf)
    if name in locked:
        raise LockError(f"Profile '{name}' is already locked.")
    locked.append(name)
    _save_locks(lf, locked)


def unlock_profile(name: str, lock_file: Path | None = None) -> None:
    lf = lock_file or _get_lock_file()
    locked = _load_locks(lf)
    if name not in locked:
        raise LockError(f"Profile '{name}' is not locked.")
    locked.remove(name)
    _save_locks(lf, locked)


def is_locked(name: str, lock_file: Path | None = None) -> bool:
    lf = lock_file or _get_lock_file()
    return name in _load_locks(lf)


def list_locked(lock_file: Path | None = None) -> list[str]:
    lf = lock_file or _get_lock_file()
    return list(_load_locks(lf))


def assert_not_locked(name: str, lock_file: Path | None = None) -> None:
    """Raise LockError if the profile is locked. Call before mutating a profile."""
    if is_locked(name, lock_file):
        raise LockError(f"Profile '{name}' is locked and cannot be modified. Run 'envswitch lock unset {name}' to unlock.")
