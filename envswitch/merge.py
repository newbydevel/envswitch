"""Merge two env profiles together with configurable conflict resolution."""

from typing import Dict, Literal

MergeStrategy = Literal["ours", "theirs", "error"]


class MergeConflictError(Exception):
    """Raised when conflicting keys exist and strategy is 'error'."""

    def __init__(self, conflicts: list[str]):
        self.conflicts = conflicts
        super().__init__(
            f"Merge conflict on keys: {', '.join(conflicts)}. "
            "Use --strategy ours or --strategy theirs to resolve."
        )


def merge_profiles(
    base: Dict[str, str],
    override: Dict[str, str],
    strategy: MergeStrategy = "theirs",
) -> Dict[str, str]:
    """Merge two env dicts.

    Args:
        base: The base profile variables.
        override: The profile to merge in.
        strategy: How to handle conflicts.
            'ours'   - keep base value on conflict
            'theirs' - use override value on conflict (default)
            'error'  - raise MergeConflictError if any key conflicts

    Returns:
        Merged dict of env variables.
    """
    conflicts = [
        key for key in override if key in base and base[key] != override[key]
    ]

    if strategy == "error" and conflicts:
        raise MergeConflictError(conflicts)

    merged = dict(base)
    for key, value in override.items():
        if key in merged and strategy == "ours":
            continue
        merged[key] = value

    return merged


def merge_profile_names(
    profiles: Dict[str, Dict[str, str]],
    base_name: str,
    override_name: str,
    strategy: MergeStrategy = "theirs",
) -> Dict[str, str]:
    """Merge two named profiles from a profiles store."""
    if base_name not in profiles:
        raise KeyError(f"Profile '{base_name}' not found.")
    if override_name not in profiles:
        raise KeyError(f"Profile '{override_name}' not found.")

    return merge_profiles(profiles[base_name], profiles[override_name], strategy)
