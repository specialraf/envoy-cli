"""Tests for envoy.export module."""

from __future__ import annotations

import json

import pytest

from envoy.export import export_env, import_env

SAMPLE_DOTENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"


def test_export_dotenv_roundtrip():
    result = export_env(SAMPLE_DOTENV, "dotenv")
    assert "DB_HOST=localhost" in result
    assert "DB_PORT=5432" in result
    assert "SECRET=abc123" in result


def test_export_json_is_valid_json():
    result = export_env(SAMPLE_DOTENV, "json")
    data = json.loads(result)
    assert data["DB_HOST"] == "localhost"
    assert data["DB_PORT"] == "5432"
    assert data["SECRET"] == "abc123"


def test_export_shell_uses_export_keyword():
    result = export_env(SAMPLE_DOTENV, "shell")
    assert 'export DB_HOST="localhost"' in result
    assert 'export SECRET="abc123"' in result


def test_export_unknown_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_env(SAMPLE_DOTENV, "yaml")


def test_import_json_to_dotenv():
    json_text = json.dumps({"FOO": "bar", "BAZ": "qux"})
    result = import_env(json_text, "json")
    assert "FOO=bar" in result
    assert "BAZ=qux" in result


def test_import_invalid_json_raises():
    with pytest.raises(ValueError, match="Invalid JSON"):
        import_env("not json", "json")


def test_import_json_non_object_raises():
    with pytest.raises(ValueError, match="top-level object"):
        import_env("[1, 2, 3]", "json")


def test_import_shell_to_dotenv():
    shell_text = 'export FOO="hello"\nexport BAR="world"\n'
    result = import_env(shell_text, "shell")
    assert "FOO=hello" in result
    assert "BAR=world" in result


def test_import_dotenv_passthrough():
    result = import_env(SAMPLE_DOTENV, "dotenv")
    assert "DB_HOST=localhost" in result


def test_export_strips_quoted_values():
    text = 'KEY="quoted_value"\n'
    result = export_env(text, "json")
    data = json.loads(result)
    assert data["KEY"] == "quoted_value"


def test_export_skips_comments_and_blanks():
    text = "# comment\n\nFOO=1\n"
    result = export_env(text, "json")
    data = json.loads(result)
    assert list(data.keys()) == ["FOO"]
