"""Clone a profile to a new name with optional value overrides."""

from typing import Dict, Optional
from envswitch.storage import load_profiles, save_profiles


class CloneError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def clone_profile(
    source: str,
    destination: str,
    overrides: Optional[Dict[str, str]] = None,
    store_path: Optional[str] = None,
) -> Dict[str, str]:
    """Clone source profile into destination, applying optional key overrides.

    Args:
        source: Name of the profile to clone.
        destination: Name for the new cloned profile.
        overrides: Optional dict of key/value pairs to override in the clone.
        store_path: Optional path to the profiles store file.

    Returns:
        The cloned profile dict.

    Raises:
        CloneError: If source doesn't exist or destination already exists.
    """
    kwargs = {"store_path": store_path} if store_path else {}
    profiles = load_profiles(**kwargs)

    if source not in profiles:
        raise CloneError(f"Source profile '{source}' does not exist.")

    if destination in profiles:
        raise CloneError(f"Destination profile '{destination}' already exists.")

    cloned = dict(profiles[source])

    if overrides:
        cloned.update(overrides)

    profiles[destination] = cloned
    save_profiles(profiles, **kwargs)

    return cloned
