"""Tests for envoy.template."""

from __future__ import annotations

import pytest

from envoy.template import (
    ParsedTemplate,
    TemplateVar,
    parse_template,
    render_template,
    template_from_env,
)


SIMPLE_TEMPLATE = "DB_HOST={{ HOST }}\nDB_PORT={{ PORT }}\n"


def test_parse_template_finds_variables():
    parsed = parse_template(SIMPLE_TEMPLATE)
    names = {v.name for v in parsed.variables}
    assert names == {"HOST", "PORT"}


def test_parse_template_no_duplicates():
    text = "A={{ X }}\nB={{ X }}\n"
    parsed = parse_template(text)
    assert len(parsed.variables) == 1
    assert parsed.variables[0].name == "X"


def test_parse_template_empty_returns_no_vars():
    parsed = parse_template("KEY=value\n")
    assert parsed.variables == []


def test_render_template_substitutes_values():
    parsed = parse_template(SIMPLE_TEMPLATE)
    rendered = render_template(parsed, {"HOST": "localhost", "PORT": "5432"})
    assert "DB_HOST=localhost" in rendered
    assert "DB_PORT=5432" in rendered


def test_render_template_missing_required_raises():
    parsed = parse_template(SIMPLE_TEMPLATE)
    with pytest.raises(KeyError, match="HOST"):
        render_template(parsed, {"PORT": "5432"})


def test_render_template_uses_default_when_missing():
    parsed = parse_template("LEVEL={{ LEVEL }}\n")
    parsed.variables[0].default = "info"
    parsed.variables[0].required = False
    rendered = render_template(parsed, {})
    assert "LEVEL=info" in rendered


def test_render_template_optional_var_empty_when_no_default():
    parsed = parse_template("EXTRA={{ EXTRA }}\n")
    parsed.variables[0].required = False
    rendered = render_template(parsed, {})
    assert "EXTRA=" in rendered


def test_template_from_env_replaces_values():
    env = "HOST=localhost\nPORT=5432\n"
    tmpl = template_from_env(env)
    assert "{{ HOST }}" in tmpl
    assert "{{ PORT }}" in tmpl
    assert "localhost" not in tmpl
    assert "5432" not in tmpl


def test_template_from_env_preserves_comments():
    env = "# a comment\nHOST=localhost\n"
    tmpl = template_from_env(env)
    assert "# a comment" in tmpl


def test_template_roundtrip():
    env = "DB=postgres\nSECRET=abc123\n"
    tmpl_text = template_from_env(env)
    parsed = parse_template(tmpl_text)
    rendered = render_template(parsed, {"DB": "postgres", "SECRET": "abc123"})
    assert "DB=postgres" in rendered
    assert "SECRET=abc123" in rendered
