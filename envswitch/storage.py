"""Handles reading and writing of .env profiles to disk."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

DEFAULT_STORE_DIR = Path.home() / ".envswitch"
PROFILES_FILE = "profiles.json"


def get_store_path(store_dir: Optional[Path] = None) -> Path:
    """Return the path to the profiles store directory."""
    return store_dir or DEFAULT_STORE_DIR


def load_profiles(store_dir: Optional[Path] = None) -> Dict[str, Dict[str, str]]:
    """Load all saved profiles from disk. Returns empty dict if none exist."""
    store = get_store_path(store_dir)
    profiles_path = store / PROFILES_FILE

    if not profiles_path.exists():
        return {}

    with open(profiles_path, "r") as f:
        return json.load(f)


def save_profiles(
    profiles: Dict[str, Dict[str, str]], store_dir: Optional[Path] = None
) -> None:
    """Persist profiles to disk."""
    store = get_store_path(store_dir)
    store.mkdir(parents=True, exist_ok=True)

    profiles_path = store / PROFILES_FILE
    with open(profiles_path, "w") as f:
        json.dump(profiles, f, indent=2)


def add_profile(
    name: str,
    env_vars: Dict[str, str],
    store_dir: Optional[Path] = None,
    overwrite: bool = False,
) -> None:
    """Add or update a named profile."""
    profiles = load_profiles(store_dir)

    if name in profiles and not overwrite:
        raise ValueError(f"Profile '{name}' already exists. Use overwrite=True to replace it.")

    profiles[name] = env_vars
    save_profiles(profiles, store_dir)


def delete_profile(name: str, store_dir: Optional[Path] = None) -> None:
    """Remove a profile by name."""
    profiles = load_profiles(store_dir)

    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found.")

    del profiles[name]
    save_profiles(profiles, store_dir)


def get_profile(name: str, store_dir: Optional[Path] = None) -> Dict[str, str]:
    """Retrieve a single profile by name."""
    profiles = load_profiles(store_dir)

    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found.")

    return profiles[name]
