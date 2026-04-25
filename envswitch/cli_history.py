"""CLI commands for profile apply history."""

import click
from envswitch.history import load_history, get_last_applied, clear_history


@click.group("history")
def cmd_history():
    """Commands for viewing profile apply history."""
    pass


@cmd_history.command("list")
def history_list():
    """List all directories and their last applied profile."""
    history = load_history()
    if not history:
        click.echo("No history recorded yet.")
        return
    click.echo(f"{'Directory':<50} {'Profile':<20}")
    click.echo("-" * 72)
    for directory, profile in sorted(history.items()):
        click.echo(f"{directory:<50} {profile:<20}")


@cmd_history.command("current")
@click.argument("directory", required=False)
def history_current(directory):
    """Show the last applied profile for a directory (defaults to cwd)."""
    profile = get_last_applied(directory=directory)
    if profile is None:
        target = directory or "current directory"
        click.echo(f"No profile recorded for {target}.")
    else:
        target = directory or "current directory"
        click.echo(f"Last applied profile for {target}: {profile}")


@cmd_history.command("clear")
@click.confirmation_option(prompt="Are you sure you want to clear all history?")
def history_clear():
    """Clear all apply history."""
    clear_history()
    click.echo("History cleared.")
