"""Integration helpers: hook history recording into the apply command."""

from typing import Optional
from envswitch.history import record_apply, get_last_applied


def apply_with_history(
    profile_name: str,
    env_vars: dict,
    target_file: str = ".env",
    directory: Optional[str] = None,
) -> None:
    """Write env vars to a .env file and record the apply in history."""
    lines = []
    for key, value in env_vars.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')

    with open(target_file, "w") as f:
        f.write("\n".join(lines))
        if lines:
            f.write("\n")

    record_apply(profile_name, directory=directory)


def suggest_last_profile(directory: Optional[str] = None) -> Optional[str]:
    """Return a suggestion for which profile to apply based on history."""
    return get_last_applied(directory=directory)
