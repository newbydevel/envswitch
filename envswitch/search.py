"""Search and filter profiles and their variables."""

from typing import Optional


def search_profiles(profiles: dict, query: str, key_only: bool = False) -> dict:
    """
    Search profiles for a query string.

    Returns a filtered dict of {profile_name: {key: value}} where the query
    matches either a key or a value (unless key_only=True).
    """
    query_lower = query.lower()
    results = {}

    for profile_name, variables in profiles.items():
        matched_vars = {}
        for key, value in variables.items():
            key_match = query_lower in key.lower()
            value_match = (not key_only) and (query_lower in value.lower())
            if key_match or value_match:
                matched_vars[key] = value
        if matched_vars:
            results[profile_name] = matched_vars

    return results


def search_by_profile(profiles: dict, query: str, profile_name: str, key_only: bool = False) -> dict:
    """
    Search within a single named profile.

    Returns matching {key: value} pairs or empty dict if profile not found.
    """
    if profile_name not in profiles:
        return {}
    return search_profiles({profile_name: profiles[profile_name]}, query, key_only).get(profile_name, {})


def find_key_across_profiles(profiles: dict, key: str) -> dict:
    """
    Find all profiles that contain an exact key match.

    Returns {profile_name: value} for each profile that has the key.
    """
    results = {}
    key_lower = key.lower()
    for profile_name, variables in profiles.items():
        for k, v in variables.items():
            if k.lower() == key_lower:
                results[profile_name] = v
                break
    return results
