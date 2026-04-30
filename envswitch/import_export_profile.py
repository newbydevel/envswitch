"""Import and export profiles to/from external files (dotenv, JSON)."""

import json
from pathlib import Path
from typing import Dict

from envswitch.parser import parse_env_file, parse_env_string, serialize_env
from envswitch.storage import load_profiles, save_profiles
from envswitch.validate import validate_profile_name, ValidationError


class ImportExportError(Exception):
    pass


def export_profile_to_file(profile_name: str, dest_path: str, fmt: str = "dotenv") -> None:
    """Export a named profile to a file in dotenv or JSON format."""
    profiles = load_profiles()
    if profile_name not in profiles:
        raise ImportExportError(f"Profile '{profile_name}' not found.")

    data = profiles[profile_name]
    path = Path(dest_path)

    if fmt == "dotenv":
        path.write_text(serialize_env(data), encoding="utf-8")
    elif fmt == "json":
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        raise ImportExportError(f"Unsupported format: '{fmt}'. Use 'dotenv' or 'json'.")


def import_profile_from_file(profile_name: str, src_path: str, fmt: str = "dotenv", overwrite: bool = False) -> None:
    """Import a profile from a dotenv or JSON file into the store."""
    try:
        validate_profile_name(profile_name)
    except ValidationError as e:
        raise ImportExportError(str(e)) from e

    path = Path(src_path)
    if not path.exists():
        raise ImportExportError(f"File not found: '{src_path}'")

    raw = path.read_text(encoding="utf-8")

    if fmt == "dotenv":
        data: Dict[str, str] = parse_env_string(raw)
    elif fmt == "json":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ImportExportError(f"Invalid JSON: {e}") from e
        if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
            raise ImportExportError("JSON must be a flat string-to-string mapping.")
    else:
        raise ImportExportError(f"Unsupported format: '{fmt}'. Use 'dotenv' or 'json'.")

    profiles = load_profiles()
    if profile_name in profiles and not overwrite:
        raise ImportExportError(f"Profile '{profile_name}' already exists. Use overwrite=True to replace it.")

    profiles[profile_name] = data
    save_profiles(profiles)
