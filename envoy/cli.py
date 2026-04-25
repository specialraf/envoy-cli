"""Main CLI entry point for envoy."""

import click

from envoy.storage import save_env, load_env, list_projects, delete_project
from envoy.cli_config import config_cmd
from envoy.cli_diff import diff_cmd
from envoy.cli_rotate import rotate_cmd
from envoy.cli_export import export_cmd
from envoy.cli_backup import backup_cmd
from envoy.cli_share import share_cmd


def _prompt_password(confirm: bool = False) -> str:
    """Prompt the user for a master password."""
    return click.prompt(
        "Master password",
        hide_input=True,
        confirmation_prompt=confirm,
    )


@click.group()
def cli():
    """envoy — manage and sync .env files with encrypted storage."""


@cli.command("set")
@click.argument("project")
@click.argument("key")
@click.argument("value")
def set_cmd(project: str, key: str, value: str):
    """Set KEY=VALUE in PROJECT's env store."""
    password = _prompt_password(confirm=False)
    try:
        env = load_env(project, password)
    except KeyError:
        env = {}
    env[key] = value
    save_env(project, env, password)
    click.echo(f"Set {key} in {project}.")


@cli.command("get")
@click.argument("project")
@click.argument("key")
def get_cmd(project: str, key: str):
    """Get the value of KEY from PROJECT's env store."""
    password = _prompt_password(confirm=False)
    try:
        env = load_env(project, password)
    except KeyError:
        raise click.ClickException(f"Project '{project}' not found.")
    if key not in env:
        raise click.ClickException(f"Key '{key}' not found in project '{project}'.")
    click.echo(env[key])


@cli.command("list")
def list_cmd():
    """List all stored projects."""
    projects = list_projects()
    if not projects:
        click.echo("No projects found.")
        return
    for p in projects:
        click.echo(p)


@cli.command("delete")
@click.argument("project")
@click.confirmation_option(prompt="Are you sure you want to delete this project?")
def delete_cmd(project: str):
    """Delete a project from the env store."""
    try:
        delete_project(project)
    except KeyError:
        raise click.ClickException(f"Project '{project}' not found.")
    click.echo(f"Deleted project '{project}'.")


cli.add_command(config_cmd, "config")
cli.add_command(diff_cmd, "diff")
cli.add_command(rotate_cmd, "rotate")
cli.add_command(export_cmd, "export")
cli.add_command(backup_cmd, "backup")
cli.add_command(share_cmd, "share")


if __name__ == "__main__":
    cli()
