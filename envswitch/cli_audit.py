"""CLI commands for the envswitch audit log."""

from __future__ import annotations

import click
from envswitch.audit import (
    get_audit_path,
    load_audit,
    get_events_for_profile,
    clear_audit,
)


@click.group("audit")
def cmd_audit():
    """View and manage the audit log."""


@cmd_audit.command("list")
@click.option("--profile", "-p", default=None, help="Filter by profile name.")
@click.option("--limit", "-n", default=20, show_default=True, help="Max entries to show.")
def audit_list(profile: str, limit: int):
    """List recent audit log entries."""
    path = get_audit_path()
    if profile:
        entries = get_events_for_profile(path, profile)
    else:
        entries = load_audit(path)

    if not entries:
        click.echo("No audit entries found.")
        return

    for entry in entries[-limit:]:
        ts = entry.get("timestamp", "unknown")
        action = entry.get("action", "?")
        prof = entry.get("profile", "?")
        details = entry.get("details")
        line = f"[{ts}] {action} -> {prof}"
        if details:
            detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
            line += f" ({detail_str})"
        click.echo(line)


@cmd_audit.command("clear")
@click.confirmation_option(prompt="Clear the entire audit log?")
def audit_clear():
    """Clear all audit log entries."""
    path = get_audit_path()
    clear_audit(path)
    click.echo("Audit log cleared.")
