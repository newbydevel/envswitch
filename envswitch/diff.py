"""Utilities for diffing two env profiles."""

from typing import Dict, Tuple, List


EnvMap = Dict[str, str]


def diff_profiles(
    old: EnvMap, new: EnvMap
) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]], List[Tuple[str, str, str]]]:
    """Compare two env profiles.

    Returns:
        added:   keys present in new but not old  -> [(key, value), ...]
        removed: keys present in old but not new  -> [(key, value), ...]
        changed: keys whose value changed         -> [(key, old_val, new_val), ...]
    """
    old_keys = set(old)
    new_keys = set(new)

    added = [(k, new[k]) for k in sorted(new_keys - old_keys)]
    removed = [(k, old[k]) for k in sorted(old_keys - new_keys)]
    changed = [
        (k, old[k], new[k])
        for k in sorted(old_keys & new_keys)
        if old[k] != new[k]
    ]

    return added, removed, changed


def format_diff(
    added: List[Tuple[str, str]],
    removed: List[Tuple[str, str]],
    changed: List[Tuple[str, str, str]],
    use_color: bool = True,
) -> str:
    """Render diff results as a human-readable string."""
    GREEN = "\033[32m" if use_color else ""
    RED = "\033[31m" if use_color else ""
    YELLOW = "\033[33m" if use_color else ""
    RESET = "\033[0m" if use_color else ""

    lines: List[str] = []

    for key, val in added:
        lines.append(f"{GREEN}+ {key}={val}{RESET}")

    for key, val in removed:
        lines.append(f"{RED}- {key}={val}{RESET}")

    for key, old_val, new_val in changed:
        lines.append(f"{YELLOW}~ {key}: {old_val!r} -> {new_val!r}{RESET}")

    if not lines:
        return "No differences."

    return "\n".join(lines)
