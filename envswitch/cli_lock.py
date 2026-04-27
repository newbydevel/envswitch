"""CLI commands for locking and unlocking env profiles.

Locked profiles cannot be modified or deleted until explicitly unlocked.
"""

import click
from envswitch.lock import lock_profile, unlock_profile, is_locked, list_locked, LockError


@click.group("lock")
def cmd_lock():
    """Lock or unlock profiles to prevent accidental changes."""
    pass


@cmd_lock.command("set")
@click.argument("profile")
@click.option("--reason", "-r", default=None, help="Optional reason for locking.")
def lock_set(profile, reason):
    """Lock a profile to prevent modifications."""
    try:
        lock_profile(profile, reason=reason)
        if reason:
            click.echo(f"Profile '{profile}' locked. Reason: {reason}")
        else:
            click.echo(f"Profile '{profile}' locked.")
    except LockError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_lock.command("unset")
@click.argument("profile")
def lock_unset(profile):
    """Unlock a previously locked profile."""
    try:
        unlock_profile(profile)
        click.echo(f"Profile '{profile}' unlocked.")
    except LockError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_lock.command("show")
@click.argument("profile")
def lock_show(profile):
    """Show whether a profile is locked."""
    if is_locked(profile):
        click.echo(f"Profile '{profile}' is LOCKED.")
    else:
        click.echo(f"Profile '{profile}' is not locked.")


@cmd_lock.command("list")
def lock_list():
    """List all currently locked profiles."""
    locked = list_locked()
    if not locked:
        click.echo("No profiles are currently locked.")
        return

    click.echo(f"{'Profile':<25} {'Reason'}")
    click.echo("-" * 50)
    for entry in locked:
        name = entry.get("profile", "?")
        reason = entry.get("reason") or "-"
        click.echo(f"{name:<25} {reason}")
