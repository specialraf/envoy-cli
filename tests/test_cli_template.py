"""Tests for envoy.cli_template CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy.cli_template import template_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def simple_template(tmp_path):
    f = tmp_path / "sample.env.tmpl"
    f.write_text("HOST={{ HOST }}\nPORT={{ PORT }}\n")
    return str(f)


@pytest.fixture()
def simple_env(tmp_path):
    f = tmp_path / ".env"
    f.write_text("HOST=localhost\nPORT=5432\n")
    return str(f)


def test_render_outputs_substituted_env(runner, simple_template):
    result = runner.invoke(
        template_cmd, ["render", simple_template, "-v", "HOST=db.example.com", "-v", "PORT=5432"]
    )
    assert result.exit_code == 0
    assert "HOST=db.example.com" in result.output
    assert "PORT=5432" in result.output


def test_render_missing_var_exits_nonzero(runner, simple_template):
    result = runner.invoke(template_cmd, ["render", simple_template, "-v", "HOST=localhost"])
    assert result.exit_code != 0
    assert "PORT" in result.output


def test_render_bad_var_format_exits_nonzero(runner, simple_template):
    result = runner.invoke(template_cmd, ["render", simple_template, "-v", "BADVAR"])
    assert result.exit_code != 0


def test_render_writes_to_output_file(runner, simple_template, tmp_path):
    out = tmp_path / "out.env"
    result = runner.invoke(
        template_cmd,
        ["render", simple_template, "-o", str(out), "-v", "HOST=h", "-v", "PORT=1"],
    )
    assert result.exit_code == 0
    assert out.read_text() == "HOST=h\nPORT=1\n"


def test_list_vars_shows_variable_names(runner, simple_template):
    result = runner.invoke(template_cmd, ["list-vars", simple_template])
    assert result.exit_code == 0
    assert "HOST" in result.output
    assert "PORT" in result.output


def test_list_vars_no_vars_message(runner, tmp_path):
    f = tmp_path / "plain.env"
    f.write_text("KEY=value\n")
    result = runner.invoke(template_cmd, ["list-vars", str(f)])
    assert result.exit_code == 0
    assert "No variables" in result.output


def test_create_generates_template_from_env(runner, simple_env):
    result = runner.invoke(template_cmd, ["create", simple_env])
    assert result.exit_code == 0
    assert "{{ HOST }}" in result.output
    assert "{{ PORT }}" in result.output
    assert "localhost" not in result.output


def test_create_writes_to_file(runner, simple_env, tmp_path):
    out = tmp_path / "out.tmpl"
    result = runner.invoke(template_cmd, ["create", simple_env, "-o", str(out)])
    assert result.exit_code == 0
    content = out.read_text()
    assert "{{ HOST }}" in content
