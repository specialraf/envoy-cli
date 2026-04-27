"""Tests for envoy.search module."""

import pytest

from envoy.storage import save_env
from envoy.search import search_projects, SearchMatch


PASSWORD = "hunter2"


@pytest.fixture()
def store(tmp_path, monkeypatch):
    """Redirect storage to a temp directory and populate test projects."""
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))

    save_env("alpha", PASSWORD, "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n")
    save_env("beta", PASSWORD, "API_URL=https://api.example.com\nAPI_KEY=xyz789\n")
    save_env("gamma", PASSWORD, "DB_HOST=remotehost\nDEBUG=true\n")

    return tmp_path


def test_search_finds_key_match(store):
    result = search_projects("DB_HOST", PASSWORD)
    assert result.found
    projects = {m.project for m in result.matches}
    assert "alpha" in projects
    assert "gamma" in projects


def test_search_finds_value_match(store):
    result = search_projects("localhost", PASSWORD)
    assert result.found
    assert any(m.project == "alpha" and m.key == "DB_HOST" for m in result.matches)


def test_search_matched_on_both(store):
    # 'api' appears in both key (API_URL, API_KEY) and value (https://api.example.com)
    result = search_projects("api", PASSWORD, case_sensitive=False)
    both_matches = [m for m in result.matches if m.matched_on == "both"]
    # API_URL value contains 'api' and key contains 'api'
    assert any(m.key == "API_URL" for m in both_matches)


def test_search_keys_only(store):
    result = search_projects("key", PASSWORD, keys_only=True)
    assert result.found
    for m in result.matches:
        assert "key" in m.key.lower()
        assert m.matched_on == "key"


def test_search_values_only(store):
    result = search_projects("true", PASSWORD, values_only=True)
    assert result.found
    for m in result.matches:
        assert "true" in m.value.lower()
        assert m.matched_on == "value"


def test_search_restricted_to_project(store):
    result = search_projects("DB_HOST", PASSWORD, project="alpha")
    assert result.found
    assert all(m.project == "alpha" for m in result.matches)


def test_search_no_matches_returns_empty(store):
    result = search_projects("NONEXISTENT_KEY_XYZ", PASSWORD)
    assert not result.found
    assert result.matches == []


def test_search_case_sensitive(store):
    result_insensitive = search_projects("db_host", PASSWORD, case_sensitive=False)
    result_sensitive = search_projects("db_host", PASSWORD, case_sensitive=True)
    assert result_insensitive.found
    assert not result_sensitive.found


def test_search_skips_project_with_wrong_password(store):
    # Should not raise; simply skip the unreadable project
    result = search_projects("DB_HOST", "wrongpassword")
    assert not result.found
