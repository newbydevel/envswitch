"""Rename and copy profile utilities for envswitch."""

from envswitch.storage import load_profiles, save_profiles


class RenameError(Exception):
    pass


def rename_profile(store_path: str, old_name: str, new_name: str) -> None:
    """Rename an existing profile from old_name to new_name."""
    profiles = load_profiles(store_path)

    if old_name not in profiles:
        raise RenameError(f"Profile '{old_name}' does not exist.")

    if new_name in profiles:
        raise RenameError(f"Profile '{new_name}' already exists.")

    if not new_name or not new_name.strip():
        raise RenameError("New profile name cannot be empty.")

    profiles[new_name] = profiles.pop(old_name)
    save_profiles(store_path, profiles)


def copy_profile(store_path: str, source_name: str, dest_name: str) -> None:
    """Copy an existing profile to a new name."""
    profiles = load_profiles(store_path)

    if source_name not in profiles:
        raise RenameError(f"Profile '{source_name}' does not exist.")

    if dest_name in profiles:
        raise RenameError(f"Profile '{dest_name}' already exists.")

    if not dest_name or not dest_name.strip():
        raise RenameError("Destination profile name cannot be empty.")

    profiles[dest_name] = dict(profiles[source_name])
    save_profiles(store_path, profiles)
