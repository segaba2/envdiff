"""Integration tests: parse a real file then transform it."""
from pathlib import Path

import pytest

from envdiff.parser import parse_env_file
from envdiff.transformer import transform


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(
        "service_url=https://example.com\n"
        "secret_token=  abc123  \n"
        "LOG_LEVEL=debug\n"
        "old_name=value\n"
    )
    return f


def test_parse_then_upper_keys(env_file):
    env = parse_env_file(env_file)
    result = transform(env, upper_keys=True)
    assert "SERVICE_URL" in result.transformed
    assert "service_url" not in result.transformed


def test_parse_then_strip_values(env_file):
    env = parse_env_file(env_file)
    result = transform(env, strip_values=True)
    assert result.transformed["secret_token"] == "abc123"


def test_parse_then_rename(env_file):
    env = parse_env_file(env_file)
    result = transform(env, rename={"old_name": "new_name"})
    assert "new_name" in result.transformed
    assert "old_name" not in result.transformed
    assert result.transformed["new_name"] == "value"


def test_all_transforms_combined(env_file):
    env = parse_env_file(env_file)
    result = transform(
        env,
        upper_keys=True,
        strip_values=True,
        rename={"OLD_NAME": "RENAMED"},  # upper_keys runs first
    )
    assert "RENAMED" in result.transformed
    assert result.transformed["SECRET_TOKEN"] == "abc123"
    assert result.transformed["LOG_LEVEL"] == "debug"


def test_value_fn_integration(env_file):
    env = parse_env_file(env_file)

    def mask_secrets(key, value):
        if "secret" in key.lower() or "token" in key.lower():
            return "[REDACTED]"
        return None

    result = transform(env, value_fn=mask_secrets)
    assert result.transformed["secret_token"] == "[REDACTED]"
    assert result.transformed["service_url"] == "https://example.com"
