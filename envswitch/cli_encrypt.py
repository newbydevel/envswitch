"""CLI commands for encrypting and decrypting profile values."""

import click
from envswitch.storage import load_profiles, save_profiles
from envswitch.encrypt import (
    generate_key,
    encrypt_profile,
    decrypt_profile,
    EncryptError,
)


@click.group(name="encrypt")
def cmd_encrypt():
    """Encrypt or decrypt profile values."""
    pass


@cmd_encrypt.command(name="keygen")
def keygen():
    """Generate a new encryption key."""
    key = generate_key()
    click.echo(key)


@cmd_encrypt.command(name="lock")
@click.argument("profile_name")
@click.option("--key", required=True, envvar="ENVSWITCH_KEY", help="Fernet encryption key.")
@click.option("--only", multiple=True, help="Specific keys to encrypt (default: all).")
def lock_profile(profile_name, key, only):
    """Encrypt values in a profile in-place."""
    profiles = load_profiles()
    if profile_name not in profiles:
        click.echo(f"Profile '{profile_name}' not found.", err=True)
        raise SystemExit(1)
    keys_to_encrypt = list(only) if only else None
    try:
        profiles[profile_name] = encrypt_profile(profiles[profile_name], key, keys_to_encrypt)
        save_profiles(profiles)
        click.echo(f"Profile '{profile_name}' encrypted.")
    except EncryptError as e:
        click.echo(f"Error: {e.message}", err=True)
        raise SystemExit(1)


@cmd_encrypt.command(name="unlock")
@click.argument("profile_name")
@click.option("--key", required=True, envvar="ENVSWITCH_KEY", help="Fernet encryption key.")
def unlock_profile(profile_name, key):
    """Decrypt enc:-prefixed values in a profile in-place."""
    profiles = load_profiles()
    if profile_name not in profiles:
        click.echo(f"Profile '{profile_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        profiles[profile_name] = decrypt_profile(profiles[profile_name], key)
        save_profiles(profiles)
        click.echo(f"Profile '{profile_name}' decrypted.")
    except EncryptError as e:
        click.echo(f"Error: {e.message}", err=True)
        raise SystemExit(1)
