"""CLI commands for snapshot management."""

import click
from envswitch import snapshot as snap
from envswitch.storage import load_profiles


@click.group("snapshot")
def cmd_snapshot():
    """Capture and restore profile snapshots."""
    pass


@cmd_snapshot.command("save")
@click.argument("profile")
@click.option("--label", "-l", default="", help="Optional label for this snapshot.")
def snapshot_save(profile: str, label: str):
    """Save a snapshot of PROFILE's current variables."""
    profiles = load_profiles()
    if profile not in profiles:
        raise click.ClickException(f"Profile '{profile}' not found.")
    variables = profiles[profile]
    s = snap.create_snapshot(profile, variables, label=label or None)
    tag = f" [{s['label']}]" if s["label"] else ""
    click.echo(f"Snapshot saved for '{profile}'{tag} at {s['timestamp']} (id={s['id']})")


@cmd_snapshot.command("list")
@click.argument("profile", required=False)
def snapshot_list(profile):
    """List snapshots, optionally filtered by PROFILE."""
    snapshots = snap.list_snapshots(profile)
    if not snapshots:
        click.echo("No snapshots found.")
        return
    for s in snapshots:
        label = f" [{s['label']}]" if s.get("label") else ""
        click.echo(f"  {s['id']}  {s['profile']}{label}  {s['timestamp']}")


@cmd_snapshot.command("show")
@click.argument("snapshot_id", type=int)
def snapshot_show(snapshot_id: int):
    """Show variables stored in a snapshot by ID."""
    s = snap.get_snapshot_by_id(snapshot_id)
    if s is None:
        raise click.ClickException(f"Snapshot id={snapshot_id} not found.")
    label = f" [{s['label']}]" if s.get("label") else ""
    click.echo(f"Profile: {s['profile']}{label}  ({s['timestamp']})")
    for k, v in s["variables"].items():
        click.echo(f"  {k}={v}")


@cmd_snapshot.command("delete")
@click.argument("snapshot_id", type=int)
def snapshot_delete(snapshot_id: int):
    """Delete a snapshot by ID."""
    ok = snap.delete_snapshot(snapshot_id)
    if not ok:
        raise click.ClickException(f"Snapshot id={snapshot_id} not found.")
    click.echo(f"Snapshot {snapshot_id} deleted.")
