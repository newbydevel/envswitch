"""Export profiles to various formats for use in different shells/tools."""

from typing import Dict


def export_as_bash(env_vars: Dict[str, str]) -> str:
    """Export env vars as bash export statements."""
    lines = []
    for key, value in env_vars.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines)


def export_as_fish(env_vars: Dict[str, str]) -> str:
    """Export env vars as fish shell set statements."""
    lines = []
    for key, value in env_vars.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'set -x {key} "{escaped}"')
    return "\n".join(lines)


def export_as_dotenv(env_vars: Dict[str, str]) -> str:
    """Export env vars as a plain .env file."""
    lines = []
    for key, value in env_vars.items():
        needs_quotes = any(c in value for c in (' ', '"', "'", '#', '=', '\n'))
        if needs_quotes:
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f'{key}={value}')
    return "\n".join(lines)


def export_as_json(env_vars: Dict[str, str]) -> str:
    """Export env vars as a JSON object."""
    import json
    return json.dumps(env_vars, indent=2)


FORMATS = {
    "bash": export_as_bash,
    "fish": export_as_fish,
    "dotenv": export_as_dotenv,
    "json": export_as_json,
}


def export_profile(env_vars: Dict[str, str], fmt: str) -> str:
    """Export a profile's env vars in the given format.

    Args:
        env_vars: Dictionary of environment variable key/value pairs.
        fmt: One of 'bash', 'fish', 'dotenv', 'json'.

    Returns:
        String representation in the requested format.

    Raises:
        ValueError: If the format is not supported.
    """
    if fmt not in FORMATS:
        supported = ", ".join(FORMATS.keys())
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {supported}")
    return FORMATS[fmt](env_vars)
