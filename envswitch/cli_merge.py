"""CLI command for merging two env profiles into a new profile."""

import click
from envswitch.storage import load_profiles, save_profiles, get_store_path
from envswitch.merge import merge_profile_names, MergeConflictError


@click.command("merge")
@click.argument("base")
@click.argument("override")
@click.argument("output")
@click.option(
    "--strategy",
    type=click.Choice(["ours", "theirs", "error"]),
    default="theirs",
    show_default=True,
    help="How to resolve conflicting keys.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite output profile if it already exists.",
)
def cmd_merge(base: str, override: str, output: str, strategy: str, overwrite: bool):
    """Merge BASE and OVERRIDE profiles into a new OUTPUT profile.

    Conflicting keys are resolved using --strategy (default: theirs).
    """
    store_path = get_store_path()
    profiles = load_profiles(store_path)

    if base not in profiles:
        click.echo(f"Error: profile '{base}' not found.", err=True)
        raise SystemExit(1)

    if override not in profiles:
        click.echo(f"Error: profile '{override}' not found.", err=True)
        raise SystemExit(1)

    if output in profiles and not overwrite:
        click.echo(
            f"Error: profile '{output}' already exists. Use --overwrite to replace it.",
            err=True,
        )
        raise SystemExit(1)

    try:
        merged = merge_profile_names(profiles, base, override, strategy=strategy)  # type: ignore[arg-type]
    except MergeConflictError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    profiles[output] = merged
    save_profiles(store_path, profiles)

    click.echo(
        f"Merged '{base}' + '{override}' → '{output}' "
        f"({len(merged)} vars, strategy={strategy})"
    )
