"""CLI commands for profile groups."""

from __future__ import annotations

import click

from envswitch.storage import get_store_path
from envswitch.group import (
    add_profile_to_group,
    remove_profile_from_group,
    list_groups,
    get_group_members,
    get_groups_for_profile,
    GroupError,
)


@click.group("group")
def cmd_group():
    """Manage profile groups."""


@cmd_group.command("add")
@click.argument("group")
@click.argument("profile")
def group_add(group: str, profile: str):
    """Add PROFILE to GROUP."""
    store_dir = get_store_path()
    try:
        add_profile_to_group(store_dir, group, profile)
        click.echo(f"Added '{profile}' to group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e.message}", err=True)
        raise SystemExit(1)


@cmd_group.command("remove")
@click.argument("group")
@click.argument("profile")
def group_remove(group: str, profile: str):
    """Remove PROFILE from GROUP."""
    store_dir = get_store_path()
    try:
        remove_profile_from_group(store_dir, group, profile)
        click.echo(f"Removed '{profile}' from group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e.message}", err=True)
        raise SystemExit(1)


@cmd_group.command("list")
@click.option("--group", "-g", default=None, help="Show members of a specific group.")
def group_list(group: str | None):
    """List all groups, or members of a specific GROUP."""
    store_dir = get_store_path()
    try:
        if group:
            members = get_group_members(store_dir, group)
            if members:
                click.echo(f"Group '{group}':")
                for m in members:
                    click.echo(f"  {m}")
            else:
                click.echo(f"Group '{group}' is empty.")
        else:
            groups = list_groups(store_dir)
            if not groups:
                click.echo("No groups defined.")
            else:
                for g, members in sorted(groups.items()):
                    click.echo(f"{g}: {', '.join(members)}")
    except GroupError as e:
        click.echo(f"Error: {e.message}", err=True)
        raise SystemExit(1)


@cmd_group.command("which")
@click.argument("profile")
def group_which(profile: str):
    """Show which groups PROFILE belongs to."""
    store_dir = get_store_path()
    result = get_groups_for_profile(store_dir, profile)
    if result:
        click.echo(f"'{profile}' is in: {', '.join(sorted(result))}")
    else:
        click.echo(f"'{profile}' is not in any group.")
