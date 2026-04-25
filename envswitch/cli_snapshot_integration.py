"""Integration helpers: wire snapshot commands into the main CLI."""

from typing import Optional
from envswitch import snapshot as snap


def auto_snapshot_before_apply(profile_name: str, variables: dict, label: Optional[str] = None) -> dict:
    """Create a snapshot of current profile variables before applying a new one.

    Useful to call from apply_with_history so users can always roll back.
    Returns the created snapshot dict.
    """
    effective_label = label or f"auto-before-apply"
    return snap.create_snapshot(profile_name, variables, label=effective_label)


def restore_snapshot_to_profile(snapshot_id: int, profiles: dict) -> dict:
    """Return updated profiles dict with snapshot variables applied to its profile.

    Does NOT write to disk — caller is responsible for saving.
    Raises ValueError if snapshot not found.
    """
    s = snap.get_snapshot_by_id(snapshot_id)
    if s is None:
        raise ValueError(f"Snapshot id={snapshot_id} not found.")
    profile_name = s["profile"]
    profiles[profile_name] = dict(s["variables"])
    return profiles


def get_latest_snapshot_for_profile(profile_name: str) -> Optional[dict]:
    """Return the most recent snapshot for a given profile, or None."""
    snapshots = snap.list_snapshots(profile_name)
    if not snapshots:
        return None
    return snapshots[-1]
