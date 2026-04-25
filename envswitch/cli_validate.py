"""CLI command for validating stored profiles."""

import click
from envswitch.storage import load_profiles
from envswitch.validate import validate_profile


@click.command("validate")
@click.argument("name", required=False)
def cmd_validate(name):
    """Validate one or all profiles for correctness.

    If NAME is given, validate only that profile.
    Otherwise validate all stored profiles.
    """
    profiles = load_profiles()

    if not profiles:
        click.echo("No profiles found.")
        return

    targets = {name: profiles[name]} if name else profiles

    if name and name not in profiles:
        click.echo(f"Profile '{name}' not found.", err=True)
        raise SystemExit(1)

    all_valid = True
    for profile_name, variables in targets.items():
        errors = validate_profile(profile_name, variables)
        if errors:
            all_valid = False
            click.echo(f"[FAIL] {profile_name}")
            for err in errors:
                click.echo(f"  - {err}")
        else:
            click.echo(f"[OK]   {profile_name}")

    if not all_valid:
        raise SystemExit(1)
