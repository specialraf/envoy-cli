"""CLI entry-point for envoy."""

from __future__ import annotations

import getpass
import sys

import click

from envoy import storage, sync


def _prompt_password(confirm: bool = False) -> str:
    password = getpass.getpass("Password: ")
    if confirm:
        second = getpass.getpass("Confirm password: ")
        if password != second:
            click.echo("Passwords do not match.", err=True)
            sys.exit(1)
    return password


@click.group()
def cli() -> None:
    """envoy — manage and sync encrypted .env files."""


@cli.command("set")
@click.argument("project")
@click.argument("env_file", type=click.Path(exists=True))
def set_cmd(project: str, env_file: str) -> None:
    """Store ENV_FILE contents under PROJECT."""
    password = _prompt_password(confirm=True)
    with open(env_file) as fh:
        content = fh.read()
    storage.save_env(project, content, password)
    click.echo(f"Saved '{project}'.")


@cli.command("get")
@click.argument("project")
@click.option("--output", "-o", default="-", help="Output file (default: stdout)")
def get_cmd(project: str, output: str) -> None:
    """Retrieve and decrypt env vars for PROJECT."""
    password = _prompt_password()
    try:
        content = storage.load_env(project, password)
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    except ValueError as exc:
        click.echo(f"Decryption error: {exc}", err=True)
        sys.exit(1)
    if output == "-":
        click.echo(content, nl=False)
    else:
        with open(output, "w") as fh:
            fh.write(content)
        click.echo(f"Written to {output}")


@cli.command("list")
def list_cmd() -> None:
    """List stored projects."""
    projects = storage.list_projects()
    if not projects:
        click.echo("No projects stored.")
    else:
        for p in sorted(projects):
            click.echo(p)


@cli.command("push")
@click.argument("project")
def push_cmd(project: str) -> None:
    """Push encrypted env blob for PROJECT to remote store."""
    password = _prompt_password()
    try:
        blob = storage.load_raw(project)
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    try:
        sync.push(project, blob)
    except (RuntimeError, EnvironmentError) as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    click.echo(f"Pushed '{project}' to remote.")


@cli.command("pull")
@click.argument("project")
def pull_cmd(project: str) -> None:
    """Pull encrypted env blob for PROJECT from remote store."""
    try:
        blob = sync.pull(project)
    except (KeyError, RuntimeError, EnvironmentError) as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    storage.save_raw(project, blob)
    click.echo(f"Pulled '{project}' from remote.")


if __name__ == "__main__":
    cli()
