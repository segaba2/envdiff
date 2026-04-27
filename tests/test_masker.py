"""Tests for envdiff.masker."""
import pytest
from envdiff.masker import mask, MaskResult, _DEFAULT_PLACEHOLDER


@pytest.fixture()
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "AUTH_TOKEN": "tok-xyz",
    }


def test_returns_mask_result(sample_env):
    result = mask(sample_env)
    assert isinstance(result, MaskResult)


def test_sensitive_keys_replaced(sample_env):
    result = mask(sample_env)
    assert result.masked["DB_PASSWORD"] == _DEFAULT_PLACEHOLDER
    assert result.masked["API_KEY"] == _DEFAULT_PLACEHOLDER
    assert result.masked["AUTH_TOKEN"] == _DEFAULT_PLACEHOLDER


def test_non_sensitive_keys_preserved(sample_env):
    result = mask(sample_env)
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["DEBUG"] == "true"


def test_masked_keys_list(sample_env):
    result = mask(sample_env)
    assert "DB_PASSWORD" in result.masked_keys
    assert "API_KEY" in result.masked_keys
    assert "AUTH_TOKEN" in result.masked_keys
    assert "APP_NAME" not in result.masked_keys


def test_original_unchanged(sample_env):
    mask(sample_env)
    assert sample_env["DB_PASSWORD"] == "s3cr3t"


def test_explicit_keys_override_autodetect(sample_env):
    result = mask(sample_env, keys=["APP_NAME"])
    assert result.masked["APP_NAME"] == _DEFAULT_PLACEHOLDER
    # password NOT masked because explicit list was given
    assert result.masked["DB_PASSWORD"] == "s3cr3t"


def test_custom_placeholder(sample_env):
    result = mask(sample_env, placeholder="<hidden>")
    assert result.masked["DB_PASSWORD"] == "<hidden>"


def test_extra_patterns(sample_env):
    env = {"APP_NAME": "myapp", "STRIPE_LIVE_KEY": "sk_live_xyz"}
    result = mask(env, extra_patterns=[r"(?i)stripe"])
    assert result.masked["STRIPE_LIVE_KEY"] == _DEFAULT_PLACEHOLDER
    assert result.masked["APP_NAME"] == "myapp"


def test_summary_no_masked():
    result = mask({"HOST": "localhost", "PORT": "5432"})
    assert "No keys masked" in result.summary()


def test_summary_with_masked(sample_env):
    result = mask(sample_env)
    s = result.summary()
    assert "masked" in s
    # counts should reflect at least the three sensitive keys
    assert "3/" in s or "3 " in s or "/5" in s


def test_empty_env():
    result = mask({})
    assert result.masked == {}
    assert result.masked_keys == []
