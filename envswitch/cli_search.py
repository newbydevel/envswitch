"""CLI commands for searching profiles and variables."""

import click
from envswitch.storage import load_profiles
from envswitch.search import search_profiles, search_by_profile, find_key_across_profiles


@click.group("search")
def cmd_search():
    """Search across profiles and variables."""
    pass


@cmd_search.command("query")
@click.argument("query")
@click.option("--profile", "-p", default=None, help="Limit search to a specific profile.")
@click.option("--keys-only", "-k", is_flag=True, default=False, help="Only match against keys, not values.")
def search_query(query: str, profile: str, keys_only: bool):
    """Search for QUERY across all profiles (or a specific one)."""
    profiles = load_profiles()

    if not profiles:
        click.echo("No profiles found.")
        return

    if profile:
        if profile not in profiles:
            click.echo(f"Profile '{profile}' not found.", err=True)
            raise SystemExit(1)
        results = {profile: search_by_profile(profiles, query, profile, key_only=keys_only)} if search_by_profile(profiles, query, profile, key_only=keys_only) else {}
    else:
        results = search_profiles(profiles, query, key_only=keys_only)

    if not results:
        click.echo(f"No matches found for '{query}'.")
        return

    for prof_name, variables in results.items():
        click.echo(f"[{prof_name}]")
        for key, value in variables.items():
            click.echo(f"  {key}={value}")


@cmd_search.command("key")
@click.argument("key")
def search_key(key: str):
    """Find all profiles that define KEY and show their values."""
    profiles = load_profiles()

    if not profiles:
        click.echo("No profiles found.")
        return

    results = find_key_across_profiles(profiles, key)

    if not results:
        click.echo(f"Key '{key}' not found in any profile.")
        return

    click.echo(f"Key '{key}' found in {len(results)} profile(s):")
    for prof_name, value in results.items():
        click.echo(f"  {prof_name}: {value}")
