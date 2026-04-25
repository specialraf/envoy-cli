"""CLI commands for .env template management."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click

from envoy.template import parse_template, render_template, template_from_env


@click.group("template")
def template_cmd() -> None:
    """Manage .env templates."""


@template_cmd.command("render")
@click.argument("template_file", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Output file (default: stdout)")
@click.option("-v", "--var", multiple=True, metavar="KEY=VALUE", help="Variable substitution")
def render_cmd(template_file: str, output: Optional[str], var: tuple) -> None:
    """Render a .env template substituting {{VARS}} with provided values."""
    values: dict[str, str] = {}
    for item in var:
        if "=" not in item:
            click.echo(f"Error: variable {item!r} must be in KEY=VALUE format.", err=True)
            sys.exit(1)
        k, v = item.split("=", 1)
        values[k.strip()] = v.strip()

    text = Path(template_file).read_text()
    parsed = parse_template(text)

    try:
        rendered = render_template(parsed, values)
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if output:
        Path(output).write_text(rendered)
        click.echo(f"Written to {output}")
    else:
        click.echo(rendered, nl=False)


@template_cmd.command("list-vars")
@click.argument("template_file", type=click.Path(exists=True))
def list_vars_cmd(template_file: str) -> None:
    """List all placeholder variables in a template file."""
    text = Path(template_file).read_text()
    parsed = parse_template(text)
    if not parsed.variables:
        click.echo("No variables found.")
        return
    for var in parsed.variables:
        click.echo(var.name)


@template_cmd.command("create")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Output template file (default: stdout)")
def create_cmd(env_file: str, output: Optional[str]) -> None:
    """Generate a template from an existing .env file."""
    text = Path(env_file).read_text()
    tmpl = template_from_env(text)
    if output:
        Path(output).write_text(tmpl)
        click.echo(f"Template written to {output}")
    else:
        click.echo(tmpl, nl=False)
