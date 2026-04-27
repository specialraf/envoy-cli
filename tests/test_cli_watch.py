"""Tests for envoy.cli_watch."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from envoy.cli import cli
import envoy.cli_watch  # noqa: F401 – registers the command group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path / "store"))
    return tmp_path


def test_watch_start_file_not_found(runner, store):
    result = runner.invoke(
        cli,
        ["watch", "start", "/nonexistent/.env", "proj", "--password", "pw"],
    )
    assert result.exit_code != 0


def test_watch_start_runs_and_stops_on_ctrl_c(runner, store, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("X=1")

    with patch("envoy.watch.time.sleep", side_effect=KeyboardInterrupt), \
         patch("envoy.watch.save_env"), \
         patch("envoy.watch.record"):
        result = runner.invoke(
            cli,
            ["watch", "start", str(env_file), "proj", "--password", "pw", "--interval", "0"],
        )

    assert result.exit_code == 0
    assert "Watcher stopped" in result.output


def test_watch_start_prints_watching_message(runner, store, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("X=1")

    with patch("envoy.watch.time.sleep", side_effect=KeyboardInterrupt), \
         patch("envoy.watch.save_env"), \
         patch("envoy.watch.record"):
        result = runner.invoke(
            cli,
            ["watch", "start", str(env_file), "myproject", "--password", "pw"],
        )

    assert "myproject" in result.output
    assert "Watching" in result.output
