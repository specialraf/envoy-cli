"""Tests for the export CLI commands."""

from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from envoy.cli_export import export_cmd
from envoy.storage import save_env

SAMPLE = "API_KEY=secret\nDEBUG=true\n"
PASSWORD = "testpass"


@pytest.fixture()
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    save_env("myproject", SAMPLE, PASSWORD)
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def test_dump_dotenv_to_stdout(store, runner):
    result = runner.invoke(export_cmd, ["dump", "myproject"], input=PASSWORD + "\n")
    assert result.exit_code == 0
    assert "API_KEY=secret" in result.output


def test_dump_json_format(store, runner):
    result = runner.invoke(export_cmd, ["dump", "myproject", "--format", "json"], input=PASSWORD + "\n")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["API_KEY"] == "secret"


def test_dump_shell_format(store, runner):
    result = runner.invoke(export_cmd, ["dump", "myproject", "--format", "shell"], input=PASSWORD + "\n")
    assert result.exit_code == 0
    assert 'export API_KEY="secret"' in result.output


def test_dump_missing_project_exits_nonzero(store, runner):
    result = runner.invoke(export_cmd, ["dump", "ghost"], input=PASSWORD + "\n")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_dump_wrong_password_exits_nonzero(store, runner):
    result = runner.invoke(export_cmd, ["dump", "myproject"], input="wrongpass\n")
    assert result.exit_code != 0
    assert "Wrong password" in result.output


def test_dump_to_file(store, runner, tmp_path):
    out_file = str(tmp_path / "exported.env")
    result = runner.invoke(
        export_cmd, ["dump", "myproject", "--output", out_file], input=PASSWORD + "\n"
    )
    assert result.exit_code == 0
    assert os.path.exists(out_file)
    content = open(out_file).read()
    assert "API_KEY=secret" in content


def test_load_dotenv_file(store, runner, tmp_path):
    env_file = tmp_path / "new.env"
    env_file.write_text("NEW_KEY=newval\n")
    result = runner.invoke(
        export_cmd,
        ["load", "newproject", str(env_file)],
        input=f"{PASSWORD}\n{PASSWORD}\n",
    )
    assert result.exit_code == 0
    assert "newproject" in result.output


def test_load_json_file(store, runner, tmp_path):
    json_file = tmp_path / "vars.json"
    json_file.write_text(json.dumps({"FROM_JSON": "yes"}))
    result = runner.invoke(
        export_cmd,
        ["load", "jsonproject", str(json_file), "--format", "json"],
        input=f"{PASSWORD}\n{PASSWORD}\n",
    )
    assert result.exit_code == 0
