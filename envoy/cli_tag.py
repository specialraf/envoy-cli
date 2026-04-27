"""CLI commands for tagging env projects."""

from __future__ import annotations

import click

from envoy import tag as tag_mod


@click.group("tag")
def tag_cmd() -> None:
    """Manage tags for projects."""


@tag_cmd.command("add")
@click.argument("project")
@click.argument("tag")
def add_cmd(project: str, tag: str) -> None:
    """Add TAG to PROJECT."""
    updated = tag_mod.add_tag(project, tag)
    click.echo(f"Tags for '{project}': {', '.join(updated) if updated else '(none)'}")


@tag_cmd.command("remove")
@click.argument("project")
@click.argument("tag")
def remove_cmd(project: str, tag: str) -> None:
    """Remove TAG from PROJECT."""
    updated = tag_mod.remove_tag(project, tag)
    click.echo(f"Tags for '{project}': {', '.join(updated) if updated else '(none)'}")


@tag_cmd.command("list")
@click.argument("project")
def list_cmd(project: str) -> None:
    """List all tags assigned to PROJECT."""
    tags = tag_mod.list_tags(project)
    if tags:
        for t in tags:
            click.echo(t)
    else:
        click.echo(f"No tags for '{project}'.")


@tag_cmd.command("find")
@click.argument("tag")
def find_cmd(tag: str) -> None:
    """Find all projects that carry TAG."""
    projects = tag_mod.projects_with_tag(tag)
    if projects:
        for p in projects:
            click.echo(p)
    else:
        click.echo(f"No projects tagged '{tag}'.")


@tag_cmd.command("clear")
@click.argument("project")
@click.confirmation_option(prompt="Remove all tags from this project?")
def clear_cmd(project: str) -> None:
    """Remove all tags from PROJECT."""
    tag_mod.clear_tags(project)
    click.echo(f"All tags cleared for '{project}'.")
