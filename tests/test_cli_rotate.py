"""Tests for the rotate CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy.cli_rotate import rotate_cmd
from envoy.storage import save_env


OLD_PASS = "old-secret"
NEW_PASS = "new-secret"
SAMPLE_ENV = "FOO=bar\n"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_PATH", str(tmp_path / "store.json"))
    return tmp_path


def test_rotate_project_success(runner, store):
    save_env("myapp", SAMPLE_ENV, OLD_PASS)
    result = runner.invoke(
        rotate_cmd,
        ["project", "myapp"],
        input=f"{OLD_PASS}\n{NEW_PASS}\n{NEW_PASS}\n",
    )
    assert result.exit_code == 0
    assert "Rotated" in result.output


def test_rotate_project_password_mismatch(runner, store):
    save_env("myapp", SAMPLE_ENV, OLD_PASS)
    result = runner.invoke(
        rotate_cmd,
        ["project", "myapp"],
        input=f"{OLD_PASS}\n{NEW_PASS}\ndifferent\n",
    )
    assert result.exit_code != 0
    assert "do not match" in result.output


def test_rotate_project_not_found(runner, store):
    result = runner.invoke(
        rotate_cmd,
        ["project", "ghost"],
        input=f"{OLD_PASS}\n{NEW_PASS}\n{NEW_PASS}\n",
    )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_rotate_project_wrong_old_password(runner, store):
    """Rotating with an incorrect old password should fail with an error."""
    save_env("myapp", SAMPLE_ENV, OLD_PASS)
    result = runner.invoke(
        rotate_cmd,
        ["project", "myapp"],
        input=f"wrong-pass\n{NEW_PASS}\n{NEW_PASS}\n",
    )
    assert result.exit_code != 0
    assert "Invalid password" in result.output or "decrypt" in result.output.lower()


def test_rotate_all_success(runner, store):
    for name in ("a", "b"):
        save_env(name, SAMPLE_ENV, OLD_PASS)
    result = runner.invoke(
        rotate_cmd,
        ["all"],
        input=f"{OLD_PASS}\n{NEW_PASS}\n{NEW_PASS}\n",
    )
    assert result.exit_code == 0
    assert "2 project" in result.output


def test_rotate_all_empty_store(runner, store):
    result = runner.invoke(
        rotate_cmd,
        ["all"],
        input=f"{OLD_PASS}\n{NEW_PASS}\n{NEW_PASS}\n",
    )
    assert result.exit_code == 0
    assert "No projects" in result.output
