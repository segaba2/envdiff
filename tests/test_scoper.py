"""Tests for envdiff.scoper."""
import pytest
from envdiff.scoper import scope, ScopeResult


@pytest.fixture
def env():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_HOST": "db.local",
        "DB_PORT": "5432",
        "SECRET_KEY": "abc123",
    }


def test_returns_scope_result(env):
    result = scope(env, "app")
    assert isinstance(result, ScopeResult)


def test_default_prefix_from_scope_name(env):
    result = scope(env, "app")
    assert "APP_HOST" in result.matched
    assert "APP_PORT" in result.matched


def test_excluded_keys_not_in_matched(env):
    result = scope(env, "app")
    assert "DB_HOST" in result.excluded
    assert "SECRET_KEY" in result.excluded


def test_explicit_prefixes(env):
    result = scope(env, "database", prefixes=["DB_"])
    assert "DB_HOST" in result.matched
    assert "DB_PORT" in result.matched
    assert "APP_HOST" not in result.matched


def test_multiple_prefixes(env):
    result = scope(env, "infra", prefixes=["APP_", "DB_"])
    assert len(result.matched) == 4
    assert "SECRET_KEY" in result.excluded


def test_strip_prefix_removes_leading_prefix(env):
    result = scope(env, "app", strip_prefix=True)
    assert "HOST" in result.matched
    assert "PORT" in result.matched
    assert "APP_HOST" not in result.matched


def test_strip_prefix_values_unchanged(env):
    result = scope(env, "app", strip_prefix=True)
    assert result.matched["HOST"] == "localhost"


def test_summary_string(env):
    result = scope(env, "app")
    s = result.summary()
    assert "app" in s
    assert "2 matched" in s


def test_to_dict_keys(env):
    result = scope(env, "db", prefixes=["DB_"])
    d = result.to_dict()
    assert set(d.keys()) == {"scope", "matched", "excluded", "strip_prefix"}


def test_empty_env():
    result = scope({}, "app")
    assert result.matched == {}
    assert result.excluded == {}


def test_no_matching_keys(env):
    result = scope(env, "xyz")
    assert result.matched == {}
    assert len(result.excluded) == len(env)
