"""CLI command for diffing two named env profiles."""

import sys
import click

from envswitch.storage import load_profiles
from envswitch.diff import diff_profiles, format_diff


@click.command("diff")
@click.argument("profile_a")
@click.argument("profile_b")
@click.option("--no-color", is_flag=True, default=False, help="Disable colored output.")
def cmd_diff(profile_a: str, profile_b: str, no_color: bool) -> None:
    """Show differences between two env profiles.

    Compares PROFILE_A (old) against PROFILE_B (new).
    """
    profiles = load_profiles()

    missing = [p for p in (profile_a, profile_b) if p not in profiles]
    if missing:
        for name in missing:
            click.echo(f"Error: profile '{name}' not found.", err=True)
        sys.exit(1)

    env_a = profiles[profile_a]
    env_b = profiles[profile_b]

    added, removed, changed = diff_profiles(env_a, env_b)
    total = len(added) + len(removed) + len(changed)

    click.echo(f"Comparing '{profile_a}' -> '{profile_b}':\n")
    click.echo(format_diff(added, removed, changed, use_color=not no_color))

    if total:
        click.echo(
            f"\n{len(added)} added, {len(removed)} removed, {len(changed)} changed."
        )
