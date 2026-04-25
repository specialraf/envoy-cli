"""CLI commands for sharing .env secrets via time-limited tokens."""

import click
from datetime import datetime

from envoy.share import create_share, redeem_share, revoke_share, list_shares
from envoy.cli import _prompt_password


@click.group("share")
def share_cmd():
    """Share env variables with others via time-limited tokens."""


@share_cmd.command("create")
@click.argument("project")
@click.option("--ttl", default=3600, show_default=True, help="Token TTL in seconds.")
@click.option("--keys", default=None, help="Comma-separated list of keys to share.")
def create_cmd(project: str, ttl: int, keys: str):
    """Create a share token for PROJECT."""
    password = _prompt_password(confirm=False)
    key_list = [k.strip() for k in keys.split(",")] if keys else None
    try:
        token = create_share(project, password, ttl=ttl, keys=key_list)
    except KeyError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Share token (expires in {ttl}s):")
    click.echo(token)


@share_cmd.command("redeem")
@click.argument("token")
@click.option("--format", "fmt", default="dotenv", type=click.Choice(["dotenv", "json"]), show_default=True)
def redeem_cmd(token: str, fmt: str):
    """Redeem a share TOKEN and print the env vars."""
    try:
        env = redeem_share(token)
    except KeyError as exc:
        raise click.ClickException(str(exc))
    except PermissionError as exc:
        raise click.ClickException(str(exc))

    if fmt == "json":
        import json
        click.echo(json.dumps(env, indent=2))
    else:
        for k, v in env.items():
            click.echo(f"{k}={v}")


@share_cmd.command("revoke")
@click.argument("token")
def revoke_cmd(token: str):
    """Revoke a share TOKEN immediately."""
    try:
        revoke_share(token)
    except KeyError as exc:
        raise click.ClickException(str(exc))
    click.echo("Token revoked.")


@share_cmd.command("list")
def list_cmd():
    """List all active share tokens."""
    shares = list_shares()
    if not shares:
        click.echo("No active share tokens.")
        return
    for s in shares:
        exp = datetime.fromtimestamp(s["expires_at"]).strftime("%Y-%m-%d %H:%M:%S")
        click.echo(f"{s['token'][:12]}...  project={s['project']}  expires={exp}")
