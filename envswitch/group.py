"""Profile grouping — assign profiles to named groups and list by group."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envswitch.storage import load_profiles


class GroupError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _get_group_file(store_dir: Path) -> Path:
    return store_dir / "groups.json"


def _load_groups(store_dir: Path) -> Dict[str, List[str]]:
    path = _get_group_file(store_dir)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_groups(store_dir: Path, groups: Dict[str, List[str]]) -> None:
    path = _get_group_file(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(groups, f, indent=2)


def add_profile_to_group(store_dir: Path, group: str, profile: str) -> None:
    profiles = load_profiles(store_dir)
    if profile not in profiles:
        raise GroupError(f"Profile '{profile}' does not exist.")
    groups = _load_groups(store_dir)
    members = groups.setdefault(group, [])
    if profile in members:
        raise GroupError(f"Profile '{profile}' is already in group '{group}'.")
    members.append(profile)
    _save_groups(store_dir, groups)


def remove_profile_from_group(store_dir: Path, group: str, profile: str) -> None:
    groups = _load_groups(store_dir)
    if group not in groups or profile not in groups[group]:
        raise GroupError(f"Profile '{profile}' is not in group '{group}'.")
    groups[group].remove(profile)
    if not groups[group]:
        del groups[group]
    _save_groups(store_dir, groups)


def list_groups(store_dir: Path) -> Dict[str, List[str]]:
    return _load_groups(store_dir)


def get_group_members(store_dir: Path, group: str) -> List[str]:
    groups = _load_groups(store_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    return list(groups[group])


def get_groups_for_profile(store_dir: Path, profile: str) -> List[str]:
    groups = _load_groups(store_dir)
    return [g for g, members in groups.items() if profile in members]
