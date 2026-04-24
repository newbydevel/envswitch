"""Parse .env file content into key/value pairs and serialize back."""

from typing import Dict


def parse_env_string(content: str) -> Dict[str, str]:
    """
    Parse a .env file string into a dictionary.

    Handles:
    - KEY=VALUE pairs
    - Quoted values (single and double)
    - Inline comments after #
    - Blank lines and comment-only lines
    """
    result: Dict[str, str] = {}

    for line in content.splitlines():
        line = line.strip()

        # Skip blank lines and comments
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, _, raw_value = line.partition("=")
        key = key.strip()

        if not key:
            continue

        value = raw_value.strip()

        # Strip inline comments (only outside quotes)
        if not (value.startswith('"') or value.startswith("'")):
            value = value.split("#")[0].strip()

        # Strip surrounding quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]

        result[key] = value

    return result


def parse_env_file(filepath: str) -> Dict[str, str]:
    """Read a .env file from disk and parse it."""
    with open(filepath, "r") as f:
        content = f.read()
    return parse_env_string(content)


def serialize_env(env_vars: Dict[str, str]) -> str:
    """Serialize a dict of env vars back into .env file format."""
    lines = []
    for key, value in env_vars.items():
        # Quote values that contain spaces or special chars
        if " " in value or "#" in value or not value:
            value = f'"{value}"'
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"
