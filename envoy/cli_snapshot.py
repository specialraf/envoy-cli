"""CLI commands for project snapshots."""

from __future__ import annotations

import click

from envoy.cli import _prompt_password
from envoy.storage import _get_store_path
from envoy.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
)


@click.group("snapshot")
def snapshot_cmd() -> None:
    """Manage point-in-time snapshots of a project's env."""


@snapshot_cmd.command("create")
@click.argument("project")
@click.option("--label", default=None, help="Human-readable label for the snapshot.")
def create_cmd(project: str, label: str | None) -> None:
    """Snapshot the current env for PROJECT."""
    password = _prompt_password(confirm=False)
    store_path = _get_store_path()
    try:
        name = create_snapshot(store_path, project, password, label=label)
        click.echo(f"Snapshot created: {name}")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@snapshot_cmd.command("list")
@click.argument("project")
def list_cmd(project: str) -> None:
    """List all snapshots for PROJECT."""
    store_path = _get_store_path()
    snapshots = list_snapshots(store_path, project)
    if not snapshots:
        click.echo("No snapshots found.")
        return
    for snap in snapshots:
        label_str = f"  ({snap['label']})" if snap.get("label") else ""
        click.echo(f"{snap['name']}{label_str}")


@snapshot_cmd.command("restore")
@click.argument("project")
@click.argument("name")
def restore_cmd(project: str, name: str) -> None:
    """Restore snapshot NAME for PROJECT."""
    password = _prompt_password(confirm=False)
    store_path = _get_store_path()
    try:
        restore_snapshot(store_path, project, name, password)
        click.echo(f"Restored snapshot '{name}' to project '{project}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@snapshot_cmd.command("delete")
@click.argument("project")
@click.argument("name")
def delete_cmd(project: str, name: str) -> None:
    """Delete snapshot NAME for PROJECT."""
    store_path = _get_store_path()
    try:
        delete_snapshot(store_path, project, name)
        click.echo(f"Deleted snapshot '{name}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
