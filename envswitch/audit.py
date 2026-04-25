"""Audit log for envswitch — tracks profile operations with timestamps."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

AUDIT_FILENAME = "audit_log.json"


def get_audit_path(base_dir: Optional[Path] = None) -> Path:
    if base_dir is None:
        base_dir = Path.home() / ".envswitch"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / AUDIT_FILENAME


def load_audit(audit_path: Path) -> List[Dict[str, Any]]:
    if not audit_path.exists():
        return []
    with audit_path.open("r") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def save_audit(audit_path: Path, entries: List[Dict[str, Any]]) -> None:
    with audit_path.open("w") as f:
        json.dump(entries, f, indent=2)


def record_event(
    audit_path: Path,
    action: str,
    profile: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    entries = load_audit(audit_path)
    entry: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "profile": profile,
    }
    if details:
        entry["details"] = details
    entries.append(entry)
    save_audit(audit_path, entries)
    return entry


def get_events_for_profile(audit_path: Path, profile: str) -> List[Dict[str, Any]]:
    return [e for e in load_audit(audit_path) if e.get("profile") == profile]


def clear_audit(audit_path: Path) -> None:
    save_audit(audit_path, [])
