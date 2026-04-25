"""Validation helpers for env profiles and variable names."""

import re
from typing import Dict, List

# Valid env var names: letters, digits, underscores, must not start with digit
ENV_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


class ValidationError(Exception):
    """Raised when a profile or env var fails validation."""
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


def validate_key(key: str) -> bool:
    """Return True if key is a valid environment variable name."""
    return bool(ENV_KEY_RE.match(key))


def validate_profile_name(name: str) -> bool:
    """Profile names must be non-empty alphanumeric/dash/underscore strings."""
    return bool(name) and bool(re.match(r'^[A-Za-z0-9_-]+$', name))


def validate_profile(name: str, variables: Dict[str, str]) -> List[str]:
    """Validate a profile name and its variables.

    Returns a list of error strings (empty list means valid).
    """
    errors = []

    if not validate_profile_name(name):
        errors.append(
            f"Invalid profile name '{name}': use only letters, digits, hyphens, underscores."
        )

    if not isinstance(variables, dict):
        errors.append("Variables must be a dictionary.")
        return errors

    for key in variables:
        if not validate_key(key):
            errors.append(
                f"Invalid variable name '{key}': must match [A-Za-z_][A-Za-z0-9_]*."
            )

    return errors


def assert_valid_profile(name: str, variables: Dict[str, str]) -> None:
    """Raise ValidationError if the profile is invalid."""
    errors = validate_profile(name, variables)
    if errors:
        raise ValidationError(
            f"Profile '{name}' failed validation with {len(errors)} error(s).",
            errors=errors,
        )
