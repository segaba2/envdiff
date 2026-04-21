"""Tests for envdiff.interpolator."""

import pytest
from envdiff.interpolator import interpolate, InterpolateResult


@pytest.fixture
def simple_env():
    return {
        "BASE": "/home/user",
        "DATA_DIR": "$BASE/data",
        "CACHE_DIR": "${DATA_DIR}/cache",
        "PLAIN": "hello",
    }


def test_returns_interpolate_result(simple_env):
    result = interpolate(simple_env)
    assert isinstance(result, InterpolateResult)


def test_plain_value_unchanged(simple_env):
    result = interpolate(simple_env)
    assert result.env["PLAIN"] == "hello"


def test_simple_reference_expanded(simple_env):
    result = interpolate(simple_env)
    assert result.env["DATA_DIR"] == "/home/user/data"


def test_chained_reference_expanded(simple_env):
    result = interpolate(simple_env)
    assert result.env["CACHE_DIR"] == "/home/user/data/cache"


def test_resolved_keys_listed(simple_env):
    result = interpolate(simple_env)
    assert "DATA_DIR" in result.resolved
    assert "CACHE_DIR" in result.resolved


def test_plain_key_not_in_resolved(simple_env):
    result = interpolate(simple_env)
    assert "PLAIN" not in result.resolved


def test_unresolved_reference_kept_as_is():
    env = {"FOO": "$MISSING_VAR/path"}
    result = interpolate(env)
    assert "FOO" in result.unresolved
    assert "$MISSING_VAR" in result.env["FOO"]


def test_has_unresolved_true_when_missing():
    env = {"A": "$GHOST"}
    result = interpolate(env)
    assert result.has_unresolved is True


def test_has_unresolved_false_when_all_resolved(simple_env):
    result = interpolate(simple_env)
    assert result.has_unresolved is False


def test_original_env_not_mutated(simple_env):
    original = dict(simple_env)
    interpolate(simple_env)
    assert simple_env == original


def test_empty_env():
    result = interpolate({})
    assert result.env == {}
    assert result.resolved == []
    assert result.unresolved == []


def test_self_reference_does_not_hang():
    env = {"LOOP": "$LOOP/x"}
    result = interpolate(env)
    assert "LOOP" in result.unresolved
