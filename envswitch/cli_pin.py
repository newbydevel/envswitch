"""CLI commands for pinning profiles to directories."""

import click
from envswitch.pin import pin_profile, unpin_profile, read_pin, PinError
from envswitch.storage import load_profiles


@click.group("pin")
def cmd_pin():
    """Pin a profile to the current (or specified) directory."""


@cmd_pin.command("set")
@click.argument("profile")
@click.option("--dir", "directory", default=None, help="Target directory (default: cwd)")
def pin_set(profile: str, directory: str | None):
    """Pin PROFILE to a directory."""
    profiles = load_profiles()
    if profile not in profiles:
        raise click.ClickException(f"Profile '{profile}' does not exist.")
    pin_file = pin_profile(profile, directory)
    click.echo(f"Pinned '{profile}' to {pin_file.parent}")


@cmd_pin.command("unset")
@click.option("--dir", "directory", default=None, help="Target directory (default: cwd)")
def pin_unset(directory: str | None):
    """Remove the pin from a directory."""
    try:
        pin_file = unpin_profile(directory)
        click.echo(f"Removed pin from {pin_file.parent}")
    except PinError as e:
        raise click.ClickException(str(e))


@cmd_pin.command("show")
@click.option("--dir", "directory", default=None, help="Target directory (default: cwd)")
def pin_show(directory: str | None):
    """Show the pinned profile for a directory."""
    try:
        profile = read_pin(directory)
    except PinError as e:
        raise click.ClickException(str(e))

    if profile is None:
        click.echo("No profile pinned in this directory.")
    else:
        click.echo(f"Pinned profile: {profile}")
