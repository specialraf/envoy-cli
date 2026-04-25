"""Tests for envoy.lint."""
import pytest
from envoy.lint import lint_env, LintIssue, LintResult


def test_lint_clean_env_returns_ok():
    content = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n"
    result = lint_env(content)
    assert result.ok


def test_lint_skips_comments_and_blanks():
    content = "# comment\n\nDB_HOST=localhost\n"
    result = lint_env(content)
    assert result.ok


def test_lint_detects_missing_equals():
    content = "DB_HOST\n"
    result = lint_env(content)
    assert not result.ok
    assert any("Missing '='" in i.message for i in result.issues)


def test_lint_detects_empty_key():
    content = "=value\n"
    result = lint_env(content)
    assert not result.ok
    assert any("Empty key" in i.message for i in result.issues)


def test_lint_detects_key_with_whitespace():
    content = "MY KEY=value\n"
    result = lint_env(content)
    assert not result.ok
    assert any("whitespace" in i.message for i in result.issues)


def test_lint_detects_lowercase_key():
    content = "db_host=localhost\n"
    result = lint_env(content)
    assert not result.ok
    assert any("uppercase" in i.message for i in result.issues)


def test_lint_detects_duplicate_key():
    content = "DB_HOST=localhost\nDB_HOST=remotehost\n"
    result = lint_env(content)
    assert not result.ok
    messages = [i.message for i in result.issues]
    assert any("Duplicate" in m for m in messages)


def test_lint_detects_unmatched_quote():
    content = 'SECRET="open\n'
    result = lint_env(content)
    assert not result.ok
    assert any("Unmatched quote" in i.message for i in result.issues)


def test_lint_matched_quotes_are_ok():
    content = 'SECRET="open sesame"\n'
    result = lint_env(content)
    assert result.ok


def test_lint_result_str_no_issues():
    result = LintResult()
    assert str(result) == "No issues found."


def test_lint_result_str_with_issues():
    issue = LintIssue(line_number=3, line="bad line", message="some error")
    result = LintResult(issues=[issue])
    text = str(result)
    assert "Line 3" in text
    assert "some error" in text


def test_lint_multiple_issues_reported():
    content = "db_host=localhost\ndb_host=other\n"
    result = lint_env(content)
    # lowercase key × 2, duplicate key × 1
    assert len(result.issues) >= 3
