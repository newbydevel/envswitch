"""CLI commands for renaming and copying profiles."""

import click
from envswitch.storage import get_store_path
from envswitch.rename import rename_profile, copy_profile, RenameError


@click.group()
def cmd_rename():
    """Rename or copy env profiles."""
    pass


@cmd_rename.command("rename")
@click.argument("old_name")
@click.argument("new_name")
def rename_cmd(old_name, new_name):
    """Rename a profile from OLD_NAME to NEW_NAME."""
    store_path = get_store_path()
    try:
        rename_profile(store_path, old_name, new_name)
        click.echo(f"Renamed profile '{old_name}' to '{new_name}'.")
    except RenameError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_rename.command("copy")
@click.argument("source")
@click.argument("dest")
def copy_cmd(source, dest):
    """Copy profile SOURCE to a new profile DEST."""
    store_path = get_store_path()
    try:
        copy_profile(store_path, source, dest)
        click.echo(f"Copied profile '{source}' to '{dest}'.")
    except RenameError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
