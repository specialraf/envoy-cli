"""CLI commands for project alias management."""

from __future__ import annotations

import click

from envoy.alias import (
    add_alias,
    aliases_for_project,
    list_aliases,
    remove_alias,
    resolve_alias,
)


@click.group("alias")
def alias_cmd() -> None:
    """Manage short aliases for projects."""


@alias_cmd.command("add")
@click.argument("alias")
@click.argument("project")
def add_cmd(alias: str, project: str) -> None:
    """Assign ALIAS as a short name for PROJECT."""
    try:
        add_alias(alias, project)
        click.echo(f"Alias '{alias}' -> '{project}' saved.")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@alias_cmd.command("remove")
@click.argument("alias")
def remove_cmd(alias: str) -> None:
    """Remove an existing ALIAS."""
    try:
        remove_alias(alias)
        click.echo(f"Alias '{alias}' removed.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@alias_cmd.command("resolve")
@click.argument("alias")
def resolve_cmd(alias: str) -> None:
    """Print the project name that ALIAS points to."""
    project = resolve_alias(alias)
    if project is None:
        raise click.ClickException(f"Alias '{alias}' not found.")
    click.echo(project)


@alias_cmd.command("list")
def list_cmd() -> None:
    """List all defined aliases."""
    entries = list_aliases()
    if not entries:
        click.echo("No aliases defined.")
        return
    for entry in entries:
        click.echo(f"{entry['alias']:<20} -> {entry['project']}")


@alias_cmd.command("find")
@click.argument("project")
def find_cmd(project: str) -> None:
    """List all aliases that point to PROJECT."""
    aliases = aliases_for_project(project)
    if not aliases:
        click.echo(f"No aliases found for project '{project}'.")
        return
    for a in sorted(aliases):
        click.echo(a)
