"""Tag profiles with labels for easier grouping and filtering."""

from __future__ import annotations

from envswitch.storage import load_profiles, save_profiles


class TagError(Exception):
    pass


def _get_tags(profile: dict) -> list[str]:
    return profile.get("__tags__", [])


def add_tag(profile_name: str, tag: str, store_path=None) -> list[str]:
    """Add a tag to a profile. Returns updated tag list."""
    profiles = load_profiles(store_path)
    if profile_name not in profiles:
        raise TagError(f"Profile '{profile_name}' not found.")
    tags = _get_tags(profiles[profile_name])
    if tag in tags:
        raise TagError(f"Tag '{tag}' already exists on profile '{profile_name}'.")
    tags.append(tag)
    profiles[profile_name]["__tags__"] = tags
    save_profiles(profiles, store_path)
    return tags


def remove_tag(profile_name: str, tag: str, store_path=None) -> list[str]:
    """Remove a tag from a profile. Returns updated tag list."""
    profiles = load_profiles(store_path)
    if profile_name not in profiles:
        raise TagError(f"Profile '{profile_name}' not found.")
    tags = _get_tags(profiles[profile_name])
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found on profile '{profile_name}'.")
    tags.remove(tag)
    profiles[profile_name]["__tags__"] = tags
    save_profiles(profiles, store_path)
    return tags


def list_tags(profile_name: str, store_path=None) -> list[str]:
    """Return the tags for a given profile."""
    profiles = load_profiles(store_path)
    if profile_name not in profiles:
        raise TagError(f"Profile '{profile_name}' not found.")
    return _get_tags(profiles[profile_name])


def find_profiles_by_tag(tag: str, store_path=None) -> list[str]:
    """Return all profile names that have the given tag."""
    profiles = load_profiles(store_path)
    return [
        name
        for name, data in profiles.items()
        if tag in _get_tags(data)
    ]
