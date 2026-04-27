"""Integration helpers: auto-decrypt profile values before applying to environment."""

import os
from envswitch.encrypt import decrypt_profile, EncryptError


def resolve_enc_key(key_override: str | None = None) -> str | None:
    """Return encryption key from override or ENVSWITCH_KEY env var."""
    return key_override or os.environ.get("ENVSWITCH_KEY")


def maybe_decrypt_profile(
    profile: dict,
    key: str | None = None,
    strict: bool = False,
) -> dict:
    """
    If any values are enc:-prefixed and a key is available, decrypt them.
    If strict=True, raises EncryptError when encrypted values exist but no key is provided.
    Returns the (possibly decrypted) profile dict.
    """
    enc_key = resolve_enc_key(key)
    has_encrypted = any(
        isinstance(v, str) and v.startswith("enc:") for v in profile.values()
    )

    if not has_encrypted:
        return profile

    if enc_key is None:
        if strict:
            raise EncryptError(
                "Profile contains encrypted values but no ENVSWITCH_KEY is set."
            )
        return profile

    return decrypt_profile(profile, enc_key)


def profile_has_encrypted_values(profile: dict) -> bool:
    """Return True if any value in the profile is enc:-prefixed."""
    return any(isinstance(v, str) and v.startswith("enc:") for v in profile.values())


def warn_if_encrypted(profile: dict, profile_name: str) -> None:
    """Print a warning if the profile still contains encrypted values."""
    if profile_has_encrypted_values(profile):
        import click
        click.echo(
            f"Warning: profile '{profile_name}' contains encrypted values. "
            "Set ENVSWITCH_KEY or use 'envswitch encrypt unlock' to decrypt.",
            err=True,
        )
