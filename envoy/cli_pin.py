"""CLI commands for managing project pins."""

import click
from envoy.pin import pin_project, unpin_project, get_pin, list_pins


@click.group("pin")
def pin_cmd():
    """Lock projects to specific snapshots."""


@pin_cmd.command("set")
@click.argument("project")
@click.argument("snapshot")
@click.option("--note", default=None, help="Optional note describing why this pin exists.")
def set_pin(project: str, snapshot: str, note: str):
    """Pin PROJECT to SNAPSHOT."""
    entry = pin_project(project, snapshot, note=note)
    click.echo(f"Pinned '{entry.project}' -> '{entry.snapshot}'.")
    if entry.note:
        click.echo(f"Note: {entry.note}")


@pin_cmd.command("remove")
@click.argument("project")
def remove_pin(project: str):
    """Remove the pin for PROJECT."""
    try:
        unpin_project(project)
        click.echo(f"Unpinned '{project}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc))


@pin_cmd.command("show")
@click.argument("project")
def show_pin(project: str):
    """Show the pin for PROJECT."""
    entry = get_pin(project)
    if entry is None:
        raise click.ClickException(f"Project '{project}' is not pinned.")
    click.echo(f"Project:  {entry.project}")
    click.echo(f"Snapshot: {entry.snapshot}")
    if entry.note:
        click.echo(f"Note:     {entry.note}")


@pin_cmd.command("list")
def list_cmd():
    """List all pinned projects."""
    pins = list_pins()
    if not pins:
        click.echo("No projects are pinned.")
        return
    for entry in pins:
        note_str = f"  # {entry.note}" if entry.note else ""
        click.echo(f"{entry.project:<20} -> {entry.snapshot}{note_str}")
