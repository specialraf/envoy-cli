"""CLI commands for the watch feature."""

import click
from envoy.cli import cli, _prompt_password
from envoy.watch import watch_file


@cli.group("watch")
def watch_cmd() -> None:
    """Watch a .env file and auto-sync changes to the store."""


@watch_cmd.command("start")
@click.argument("file", type=click.Path(exists=True))
@click.argument("project")
@click.option("--interval", default=1.0, show_default=True, help="Poll interval in seconds.")
@click.option("--password", envvar="ENVOY_PASSWORD", default=None, help="Encryption password.")
def start_cmd(file: str, project: str, interval: float, password: str) -> None:
    """Watch FILE and sync changes into PROJECT on every save."""
    if not password:
        password = _prompt_password(confirm=False)

    click.echo(f"Watching {file} → project '{project}' (interval={interval}s). Press Ctrl+C to stop.")
    try:
        watch_file(
            path=file,
            project=project,
            password=password,
            interval=interval,
            on_change=lambda _: click.echo(f"  ↺  synced '{project}'"),
        )
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except KeyboardInterrupt:
        click.echo("\nWatcher stopped.")
