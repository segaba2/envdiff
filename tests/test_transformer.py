"""Tests for envdiff.transformer."""
import pytest
from envdiff.transformer import transform, TransformResult


@pytest.fixture()
def base_env():
    return {
        "db_host": "localhost",
        "DB_PORT": "5432",
        "api_key": "  secret  ",
        "debug": "true",
    }


def test_no_transform_returns_copy(base_env):
    result = transform(base_env)
    assert result.transformed == base_env
    assert result.transformed is not base_env


def test_upper_keys(base_env):
    result = transform(base_env, upper_keys=True)
    assert "DB_HOST" in result.transformed
    assert "db_host" not in result.transformed
    assert "DB_PORT" in result.transformed


def test_upper_keys_applied_list(base_env):
    result = transform(base_env, upper_keys=True)
    assert "DB_HOST" in result.applied
    assert "API_KEY" in result.applied
    # DB_PORT was already upper – not in applied
    assert "DB_PORT" not in result.applied


def test_strip_values(base_env):
    result = transform(base_env, strip_values=True)
    assert result.transformed["api_key"] == "secret"
    assert result.transformed["db_host"] == "localhost"  # unchanged


def test_strip_values_applied_list(base_env):
    result = transform(base_env, strip_values=True)
    assert "api_key" in result.applied
    assert "db_host" not in result.applied


def test_rename(base_env):
    result = transform(base_env, rename={"debug": "DEBUG_MODE"})
    assert "DEBUG_MODE" in result.transformed
    assert "debug" not in result.transformed
    assert result.transformed["DEBUG_MODE"] == "true"


def test_rename_missing_key_ignored(base_env):
    result = transform(base_env, rename={"nonexistent": "NEW_KEY"})
    assert "NEW_KEY" not in result.transformed
    assert len(result.transformed) == len(base_env)


def test_value_fn_applied(base_env):
    def redact(key, value):
        if "key" in key.lower():
            return "***"
        return None

    result = transform(base_env, value_fn=redact)
    assert result.transformed["api_key"] == "***"
    assert result.transformed["db_host"] == "localhost"


def test_value_fn_no_change_not_in_applied(base_env):
    result = transform(base_env, value_fn=lambda k, v: None)
    assert result.applied == []


def test_combined_upper_and_strip(base_env):
    result = transform(base_env, upper_keys=True, strip_values=True)
    assert result.transformed["API_KEY"] == "secret"
    assert "api_key" not in result.transformed


def test_summary_string(base_env):
    result = transform(base_env, upper_keys=True)
    s = result.summary()
    assert "transformed" in s
    assert "skipped" in s
