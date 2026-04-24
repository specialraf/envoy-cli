"""CLI commands for diffing .env files."""

from __future__ import annotations

import click

from envoy.diff import diff_envs, format_diff
from envoy.storage import load_env
from envoy.cli import _prompt_password


@click.group("diff")
def diff_cmd() -> None:
    """Compare .env versions or files."""


@diff_cmd.command("projects")
@click.argument("project_a")
@click.argument("project_b")
@click.option("--password", "-p", default=None, help="Encryption password.")
def diff_projects(project_a: str, project_b: str, password: str | None) -> None:
    """Show diff between two stored projects."""
    pwd = password or _prompt_password()
    try:
        env_a = load_env(project_a, pwd)
    except KeyError:
        raise click.ClickException(f"Project '{project_a}' not found.")
    try:
        env_b = load_env(project_b, pwd)
    except KeyError:
        raise click.ClickException(f"Project '{project_b}' not found.")

    result = diff_envs(env_a, env_b)
    if not result.has_changes:
        click.echo("No differences found.")
        return

    for line in format_diff(result):
        if line.startswith("+"):
            click.echo(click.style(line, fg="green"))
        elif line.startswith("-"):
            click.echo(click.style(line, fg="red"))
        else:
            click.echo(click.style(line, fg="yellow"))


@diff_cmd.command("file")
@click.argument("project")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--password", "-p", default=None, help="Encryption password.")
def diff_file(project: str, filepath: str, password: str | None) -> None:
    """Show diff between a stored project and a local .env file."""
    pwd = password or _prompt_password()
    try:
        stored = load_env(project, pwd)
    except KeyError:
        raise click.ClickException(f"Project '{project}' not found.")

    with open(filepath, "r", encoding="utf-8") as fh:
        local = fh.read()

    result = diff_envs(stored, local)
    if not result.has_changes:
        click.echo("No differences found.")
        return

    for line in format_diff(result):
        if line.startswith("+"):
            click.echo(click.style(line, fg="green"))
        elif line.startswith("-"):
            click.echo(click.style(line, fg="red"))
        else:
            click.echo(click.style(line, fg="yellow"))
