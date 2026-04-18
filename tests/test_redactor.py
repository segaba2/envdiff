"""Tests for envdiff.redactor."""

import pytest
from envdiff.redactor import redact, redact_for_display, REDACTED, RedactResult


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "AUTH_TOKEN": "tok_xyz",
        "PORT": "8080",
        "PRIVATE_KEY": "-----BEGIN RSA",
    }


def test_sensitive_keys_are_redacted(sample_env):
    result = redact(sample_env)
    assert result.redacted["DB_PASSWORD"] == REDACTED
    assert result.redacted["API_KEY"] == REDACTED
    assert result.redacted["AUTH_TOKEN"] == REDACTED
    assert result.redacted["PRIVATE_KEY"] == REDACTED


def test_non_sensitive_keys_preserved(sample_env):
    result = redact(sample_env)
    assert result.redacted["APP_NAME"] == "myapp"
    assert result.redacted["PORT"] == "8080"


def test_redacted_keys_list(sample_env):
    result = redact(sample_env)
    assert "DB_PASSWORD" in result.redacted_keys
    assert "API_KEY" in result.redacted_keys
    assert "APP_NAME" not in result.redacted_keys


def test_original_unchanged(sample_env):
    result = redact(sample_env)
    assert result.original["DB_PASSWORD"] == "s3cr3t"


def test_custom_placeholder(sample_env):
    result = redact(sample_env, placeholder="[HIDDEN]")
    assert result.redacted["DB_PASSWORD"] == "[HIDDEN]"


def test_extra_patterns(sample_env):
    extra = {"APP_NAME": "myapp", "PORT": "8080"}
    result = redact(extra, extra_patterns=["PORT"])
    assert result.redacted["PORT"] == REDACTED
    assert result.redacted["APP_NAME"] == "myapp"


def test_summary_no_redactions():
    result = redact({"HOST": "localhost"})
    assert result.summary() == "No keys redacted."


def test_summary_with_redactions(sample_env):
    result = redact(sample_env)
    assert "key(s) redacted" in result.summary()


def test_redact_for_display_returns_dict(sample_env):
    out = redact_for_display(sample_env)
    assert isinstance(out, dict)
    assert out["DB_PASSWORD"] == REDACTED


def test_empty_env():
    result = redact({})
    assert result.redacted == {}
    assert result.redacted_keys == []
