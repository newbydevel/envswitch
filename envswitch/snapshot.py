"""Snapshot support: capture and restore .env state at a point in time."""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from envswitch.storage import get_store_path


def get_snapshot_path() -> Path:
    return get_store_path().parent / "snapshots.json"


def load_snapshots() -> List[Dict]:
    path = get_snapshot_path()
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_snapshots(snapshots: List[Dict]) -> None:
    path = get_snapshot_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(snapshots, f, indent=2)


def create_snapshot(profile_name: str, variables: Dict[str, str], label: Optional[str] = None) -> Dict:
    snapshot = {
        "id": int(time.time() * 1000),
        "profile": profile_name,
        "label": label or "",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "variables": variables,
    }
    snapshots = load_snapshots()
    snapshots.append(snapshot)
    save_snapshots(snapshots)
    return snapshot


def list_snapshots(profile_name: Optional[str] = None) -> List[Dict]:
    snapshots = load_snapshots()
    if profile_name:
        return [s for s in snapshots if s["profile"] == profile_name]
    return snapshots


def get_snapshot_by_id(snapshot_id: int) -> Optional[Dict]:
    for s in load_snapshots():
        if s["id"] == snapshot_id:
            return s
    return None


def delete_snapshot(snapshot_id: int) -> bool:
    snapshots = load_snapshots()
    new_snapshots = [s for s in snapshots if s["id"] != snapshot_id]
    if len(new_snapshots) == len(snapshots):
        return False
    save_snapshots(new_snapshots)
    return True
