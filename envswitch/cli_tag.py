"""CLI commands for tagging profiles."""

import click
from envswitch.tag import add_tag, remove_tag, list_tags, get_profiles_by_tag, TagError
from envswitch.storage import load_profiles


@click.group("tag")
def cmd_tag():
    """Tag profiles for grouping and filtering."""
    pass


@cmd_tag.command("add")
@click.argument("profile")
@click.argument("tag")
def tag_add(profile, tag):
    """Add a tag to a profile.

    Example: envswitch tag add production backend
    """
    try:
        add_tag(profile, tag)
        click.echo(f"Tagged '{profile}' with '{tag}'.")
    except TagError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_tag.command("remove")
@click.argument("profile")
@click.argument("tag")
def tag_remove(profile, tag):
    """Remove a tag from a profile.

    Example: envswitch tag remove production backend
    """
    try:
        remove_tag(profile, tag)
        click.echo(f"Removed tag '{tag}' from '{profile}'.")
    except TagError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_tag.command("list")
@click.argument("profile", required=False)
def tag_list(profile):
    """List tags for a profile, or list all tagged profiles.

    If PROFILE is given, shows tags for that profile.
    Otherwise, shows all profiles and their tags.
    """
    profiles = load_profiles()

    if not profiles:
        click.echo("No profiles found.")
        return

    if profile:
        if profile not in profiles:
            click.echo(f"Error: profile '{profile}' not found.", err=True)
            raise SystemExit(1)
        tags = list_tags(profile)
        if tags:
            click.echo(f"{profile}: {', '.join(sorted(tags))}")
        else:
            click.echo(f"{profile}: (no tags)")
    else:
        any_tags = False
        for name in sorted(profiles):
            tags = list_tags(name)
            if tags:
                click.echo(f"{name}: {', '.join(sorted(tags))}")
                any_tags = True
        if not any_tags:
            click.echo("No profiles have tags.")


@cmd_tag.command("find")
@click.argument("tag")
def tag_find(tag):
    """Find all profiles that have a given tag.

    Example: envswitch tag find backend
    """
    matches = get_profiles_by_tag(tag)
    if not matches:
        click.echo(f"No profiles tagged with '{tag}'.")
    else:
        click.echo(f"Profiles tagged '{tag}':")
        for name in sorted(matches):
            click.echo(f"  {name}")
