"""Main CLI entry-point for envoy."""

from __future__ import annotations

import click

from envoy.storage import save_env, load_env, list_projects, delete_project


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
    """Store ENV_FILE contents under PROJECT."""
    password = _prompt_password(confirm=True)
    with open(env_file) as fh:
        content = fh.read()
    save_env(project, content, password)
    click.echo(f"Saved '{project}'.")


@cli.command("get")
@click.argument("project")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Write to file instead of stdout.")
def get_cmd(project: str, output: str | None) -> None:
    """Retrieve the .env for PROJECT."""
    password = _prompt_password()
    try:
        content = load_env(project, password)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError as exc:
        raise click.ClickException("Decryption failed — wrong password?") from exc
    if output:
        with open(output, "w") as fh:
            fh.write(content)
        click.echo(f"Written to {output}.")
    else:
        click.echo(content, nl=False)


@cli.command("list")
def list_cmd() -> None:
    """List all stored projects."""
    projects = list_projects()
    if not projects:
        click.echo("No projects stored.")
        return
    for name in sorted(projects):
        click.echo(name)


@cli.command("delete")
@click.argument("project")
@click.confirmation_option(prompt="Are you sure you want to delete this project?")
def delete_cmd(project: str) -> None:
    """Delete a stored PROJECT."""
    try:
        delete_project(project)
        click.echo(f"Deleted '{project}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


# Register sub-command groups
from envoy.cli_config import config_cmd  # noqa: E402
from envoy.cli_diff import diff_cmd  # noqa: E402
from envoy.cli_rotate import rotate_cmd  # noqa: E402
from envoy.cli_export import export_cmd  # noqa: E402
from envoy.cli_backup import backup_cmd  # noqa: E402
from envoy.cli_share import share_cmd  # noqa: E402
from envoy.cli_template import template_cmd  # noqa: E402
from envoy.cli_snapshot import snapshot_cmd  # noqa: E402
from envoy.cli_watch import watch_cmd  # noqa: E402
from envoy.cli_tag import tag_cmd  # noqa: E402
from envoy.cli_pin import pin_cmd  # noqa: E402
from envoy.cli_alias import alias_cmd  # noqa: E402

cli.add_command(config_cmd)
cli.add_command(diff_cmd)
cli.add_command(rotate_cmd)
cli.add_command(export_cmd)
cli.add_command(backup_cmd)
cli.add_command(share_cmd)
cli.add_command(template_cmd)
cli.add_command(snapshot_cmd)
cli.add_command(watch_cmd)
cli.add_command(tag_cmd)
cli.add_command(pin_cmd)
cli.add_command(alias_cmd)
