"""Tests for envswitch.template."""

import pytest
from envswitch.template import (
    TemplateRenderError,
    render_value,
    render_profile,
)


# ---------------------------------------------------------------------------
# render_value
# ---------------------------------------------------------------------------

def test_render_value_simple():
    assert render_value("hello {{NAME}}", {"NAME": "world"}) == "hello world"


def test_render_value_multiple_placeholders():
    result = render_value("{{SCHEME}}://{{HOST}}:{{PORT}}", {"SCHEME": "https", "HOST": "example.com", "PORT": "443"})
    assert result == "https://example.com:443"


def test_render_value_no_placeholders():
    assert render_value("static_value", {}) == "static_value"


def test_render_value_strict_raises_on_missing():
    with pytest.raises(TemplateRenderError) as exc_info:
        render_value("{{MISSING}}", {}, strict=True)
    assert "MISSING" in exc_info.value.missing


def test_render_value_non_strict_keeps_placeholder():
    result = render_value("{{MISSING}}", {}, strict=False)
    assert result == "{{MISSING}}"


def test_render_value_whitespace_inside_braces():
    assert render_value("{{ KEY }}", {"KEY": "val"}) == "val"


# ---------------------------------------------------------------------------
# render_profile
# ---------------------------------------------------------------------------

def test_render_profile_with_explicit_context():
    profile = {"DB_URL": "postgres://{{HOST}}/mydb"}
    context = {"HOST": "localhost"}
    rendered = render_profile(profile, context=context)
    assert rendered["DB_URL"] == "postgres://localhost/mydb"


def test_render_profile_self_context():
    profile = {
        "HOST": "localhost",
        "PORT": "5432",
        "DB_URL": "postgres://{{HOST}}:{{PORT}}/mydb",
    }
    rendered = render_profile(profile)
    assert rendered["DB_URL"] == "postgres://localhost:5432/mydb"
    # Literal keys are passed through unchanged
    assert rendered["HOST"] == "localhost"


def test_render_profile_missing_key_strict():
    profile = {"URL": "http://{{UNDEFINED_HOST}}"}
    with pytest.raises(TemplateRenderError):
        render_profile(profile)


def test_render_profile_missing_key_non_strict():
    profile = {"URL": "http://{{UNDEFINED_HOST}}"}
    rendered = render_profile(profile, strict=False)
    assert rendered["URL"] == "http://{{UNDEFINED_HOST}}"


def test_render_profile_returns_new_dict():
    profile = {"KEY": "value"}
    rendered = render_profile(profile, context={})
    assert rendered is not profile


def test_template_render_error_message():
    err = TemplateRenderError(["FOO", "BAR"])
    assert "FOO" in str(err)
    assert "BAR" in str(err)
