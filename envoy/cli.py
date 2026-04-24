"""Command-line interface for envoy-cli."""

import getpass
import sys
from pathlib import Path
from typing import Optional

import click

from envoy.storage import save_env, load_env, list_projects, delete_env


def _prompt_password(confirm: bool = False) -> str:
    password = getpass.getpass("Master password: ")
    if confirm:
        repeat = getpass.getpass("Confirm password: ")
        if password != repeat:
            click.echo("Passwords do not match.", err=True)
            sys.exit(1)
    return password


@click.group()
@click.version_option(prog_name="envoy")
def cli() -> None:
    """envoy — manage and sync .env files with encrypted local storage."""


@cli.command("set")
@click.argument("project")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
def set_cmd(project: str, env_file: str) -> None:
    """Encrypt and store ENV_FILE under PROJECT."""
    content = Path(env_file).read_text()
    password = _prompt_password(confirm=True)
    save_env(project, content, password)
    click.echo(f"✓ Stored env for '{project}'.")


@cli.command("get")
@click.argument("project")
@click.option("-o", "--output", default=None,
              help="Write to file instead of stdout.")
def get_cmd(project: str, output: Optional[str]) -> None:
    """Decrypt and retrieve the env for PROJECT."""
    password = _prompt_password()
    try:
        content = load_env(project, password)
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    except Exception:
        click.echo("Decryption failed — wrong password?", err=True)
        sys.exit(1)

    if output:
        Path(output).write_text(content)
        click.echo(f"✓ Written to '{output}'.")
    else:
        click.echo(content, nl=False)


@cli.command("list")
def list_cmd() -> None:
    """List all stored project names."""
    projects = list_projects()
    if not projects:
        click.echo("No projects stored yet.")
    else:
        for name in projects:
            click.echo(name)


@cli.command("delete")
@click.argument("project")
@click.confirmation_option(prompt="Are you sure you want to delete this env?")
def delete_cmd(project: str) -> None:
    """Delete the stored env for PROJECT."""
    try:
        delete_env(project)
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    click.echo(f"✓ Deleted env for '{project}'.")


if __name__ == "__main__":
    cli()
