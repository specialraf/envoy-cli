"""CLI sub-commands for reading and writing envoy configuration."""

import click
from envoy.config import get_value, set_value, load_config, DEFAULT_CONFIG


@click.group("config")
def config_cmd():
    """Manage envoy-cli configuration."""


@config_cmd.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a configuration KEY to VALUE.

    Example: envoy config set remote_url https://my-server.com
    """
    try:
        # Coerce numeric strings for known numeric fields
        if key == "timeout":
            value = int(value)  # type: ignore[assignment]
        set_value(key, value)
        click.echo(f"Config updated: {key} = {value}")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError:
        raise click.ClickException(f"Invalid value for {key!r}: expected a number.")


@config_cmd.command("get")
@click.argument("key")
def config_get(key: str):
    """Print the current value of a configuration KEY."""
    if key not in DEFAULT_CONFIG:
        raise click.ClickException(f"Unknown config key: {key!r}")
    value = get_value(key)
    click.echo(f"{key} = {value}")


@config_cmd.command("list")
def config_list():
    """List all current configuration values."""
    config = load_config()
    for k, v in config.items():
        # Mask token for security
        display = "****" if k == "token" and v else v
        click.echo(f"{k} = {display}")
