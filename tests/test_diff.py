"""Tests for envoy.diff module."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy.diff import DiffResult, _parse_env, diff_envs, format_diff


ENV_A = """
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=abc123
# a comment
DEBUG=true
"""

ENV_B = """
DB_HOST=localhost
DB_PORT=5433
NEW_KEY=hello
DEBUG=true
"""


def test_parse_env_basic():
    result = _parse_env("FOO=bar\nBAZ=qux")
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_skips_comments_and_blanks():
    result = _parse_env("# comment\n\nFOO=bar")
    assert result == {"FOO": "bar"}


def test_parse_env_skips_lines_without_equals():
    result = _parse_env("NOEQUALSSIGN\nFOO=bar")
    assert result == {"FOO": "bar"}


def test_diff_envs_detects_added():
    result = diff_envs(ENV_A, ENV_B)
    assert "NEW_KEY" in result.added
    assert result.added["NEW_KEY"] == "hello"


def test_diff_envs_detects_removed():
    result = diff_envs(ENV_A, ENV_B)
    assert "SECRET_KEY" in result.removed


def test_diff_envs_detects_changed():
    result = diff_envs(ENV_A, ENV_B)
    assert "DB_PORT" in result.changed
    assert result.changed["DB_PORT"] == ("5432", "5433")


def test_diff_envs_detects_unchanged():
    result = diff_envs(ENV_A, ENV_B)
    assert "DB_HOST" in result.unchanged
    assert "DEBUG" in result.unchanged


def test_has_changes_true_when_differences():
    result = diff_envs(ENV_A, ENV_B)
    assert result.has_changes is True


def test_has_changes_false_when_identical():
    result = diff_envs(ENV_A, ENV_A)
    assert result.has_changes is False


def test_format_diff_prefixes():
    result = diff_envs(ENV_A, ENV_B)
    lines = format_diff(result)
    prefixes = {line[0] for line in lines}
    assert prefixes <= {"+", "-", "~"}


def test_format_diff_empty_when_no_changes():
    result = diff_envs(ENV_A, ENV_A)
    assert format_diff(result) == []
