"""CLI commands for backup and restore of envoy projects."""

from __future__ import annotations

from pathlib import Path

import click

from envoy.backup import backup_all, restore_all
from envoy.cli import _prompt_password


@click.group("backup")
def backup_cmd() -> None:
    """Backup and restore .env snapshots."""


@backup_cmd.command("create")
@click.option("--dest", default=".", show_default=True, help="Directory to store the archive.")
@click.password_option("--password", prompt="Master password", help="Encryption password.")
def create_backup(dest: str, password: str) -> None:
    """Create a backup archive of all projects."""
    try:
        archive = backup_all(password, Path(dest))
        click.echo(f"Backup created: {archive}")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@backup_cmd.command("restore")
@click.argument("archive", type=click.Path(exists=True, path_type=Path))
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing projects.")
@click.password_option("--password", prompt="Master password", help="Encryption password.")
def restore_backup(archive: Path, overwrite: bool, password: str) -> None:
    """Restore projects from a backup archive."""
    try:
        restored = restore_all(password, archive, overwrite=overwrite)
        if restored:
            click.echo(f"Restored {len(restored)} project(s): {', '.join(restored)}")
        else:
            click.echo("Nothing restored (projects already exist; use --overwrite to force).")
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
