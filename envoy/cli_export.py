"""CLI commands for exporting and importing env files."""

from __future__ import annotations

import sys

import click

from .cli import _prompt_password
from .export import SUPPORTED_FORMATS, export_env, import_env
from .storage import load_env, save_env


@click.group("export")
def export_cmd() -> None:
    """Export or import .env data in various formats."""


@export_cmd.command("dump")
@click.argument("project")
@click.option(
    "--format", "fmt",
    default="dotenv",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS),
    help="Output format.",
)
@click.option("--output", "-o", type=click.Path(), default=None, help="Write to file instead of stdout.")
def dump_cmd(project: str, fmt: str, output: str | None) -> None:
    """Export a stored project env to stdout or a file."""
    password = _prompt_password(confirm=False)
    try:
        raw = load_env(project, password)
    except KeyError:
        click.echo(f"Project '{project}' not found.", err=True)
        sys.exit(1)
    except ValueError:
        click.echo("Wrong password.", err=True)
        sys.exit(1)

    result = export_env(raw, fmt)

    if output:
        with open(output, "w") as fh:
            fh.write(result)
        click.echo(f"Exported to {output}")
    else:
        click.echo(result, nl=False)


@export_cmd.command("load")
@click.argument("project")
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--format", "fmt",
    default="dotenv",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS),
    help="Input format.",
)
def load_cmd(project: str, file: str, fmt: str) -> None:
    """Import an env file into a project from the given format."""
    with open(file) as fh:
        text = fh.read()

    try:
        dotenv_text = import_env(text, fmt)
    except ValueError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        sys.exit(1)

    password = _prompt_password(confirm=True)
    save_env(project, dotenv_text, password)
    click.echo(f"Imported '{file}' into project '{project}'.")
