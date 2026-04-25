"""Main CLI entry point for envoy."""

from __future__ import annotations

import click

from envoy.storage import save_env, load_env, list_projects, delete_env
from envoy.cli_config import config_cmd
from envoy.cli_diff import diff_cmd
from envoy.cli_rotate import rotate_cmd
from envoy.cli_export import export_cmd
from envoy.cli_backup import backup_cmd
from envoy.cli_share import share_cmd
from envoy.cli_template import template_cmd


def _prompt_password(confirm: bool = False) -> str:
    password = click.prompt("Password", hide_input=True)
    if confirm:
        click.prompt("Confirm password", hide_input=True, confirmation_prompt=True)
    return password


@click.group()
def cli() -> None:
    """envoy — manage and sync .env files with encrypted storage."""


@cli.command("set")
@click.argument("project")
@click.argument("env_file", type=click.Path(exists=True))
def set_cmd(project: str, env_file: str) -> None:
    """Store an .env file for PROJECT."""
    import pathlib

    password = _prompt_password(confirm=True)
    content = pathlib.Path(env_file).read_text()
    save_env(project, content, password)
    click.echo(f"Saved {project}")


@cli.command("get")
@click.argument("project")
@click.option("-o", "--output", default=None, help="Write to file instead of stdout")
def get_cmd(project: str, output: str | None) -> None:
    """Retrieve the .env file for PROJECT."""
    import pathlib

    password = _prompt_password()
    try:
        content = load_env(project, password)
    except KeyError:
        click.echo(f"Project {project!r} not found.", err=True)
        raise SystemExit(1)
    except ValueError:
        click.echo("Wrong password or corrupted data.", err=True)
        raise SystemExit(1)

    if output:
        pathlib.Path(output).write_text(content)
        click.echo(f"Written to {output}")
    else:
        click.echo(content, nl=False)


@cli.command("list")
def list_cmd() -> None:
    """List all stored projects."""
    projects = list_projects()
    if not projects:
        click.echo("No projects stored.")
        return
    for p in projects:
        click.echo(p)


@cli.command("delete")
@click.argument("project")
def delete_cmd(project: str) -> None:
    """Delete the stored .env for PROJECT."""
    try:
        delete_env(project)
        click.echo(f"Deleted {project}")
    except KeyError:
        click.echo(f"Project {project!r} not found.", err=True)
        raise SystemExit(1)


cli.add_command(config_cmd, "config")
cli.add_command(diff_cmd, "diff")
cli.add_command(rotate_cmd, "rotate")
cli.add_command(export_cmd, "export")
cli.add_command(backup_cmd, "backup")
cli.add_command(share_cmd, "share")
cli.add_command(template_cmd, "template")

if __name__ == "__main__":
    cli()
