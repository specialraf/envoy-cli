"""CLI commands for key rotation."""

from __future__ import annotations

import click

from envoy.rotate import rotate_project, rotate_all
from envoy.cli import _prompt_password


@click.group("rotate")
def rotate_cmd() -> None:
    """Re-encrypt stored .env files with a new master password."""


@rotate_cmd.command("project")
@click.argument("project")
def rotate_project_cmd(project: str) -> None:
    """Rotate encryption key for a single PROJECT."""
    old_password = _prompt_password("Current master password")
    new_password = _prompt_password("New master password")
    confirm = _prompt_password("Confirm new master password")
    if new_password != confirm:
        raise click.ClickException("Passwords do not match.")
    try:
        rotate_project(project, old_password, new_password)
        click.echo(f"✓ Rotated encryption for project '{project}'.")
    except KeyError:
        raise click.ClickException(f"Project '{project}' not found.")
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Rotation failed: {exc}")


@rotate_cmd.command("all")
def rotate_all_cmd() -> None:
    """Rotate encryption key for ALL stored projects."""
    old_password = _prompt_password("Current master password")
    new_password = _prompt_password("New master password")
    confirm = _prompt_password("Confirm new master password")
    if new_password != confirm:
        raise click.ClickException("Passwords do not match.")
    try:
        rotated = rotate_all(old_password, new_password)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Rotation failed: {exc}")
    if rotated:
        click.echo(f"✓ Rotated {len(rotated)} project(s): {', '.join(rotated)}")
    else:
        click.echo("No projects found to rotate.")
