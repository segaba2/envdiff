"""Tests for envdiff.flattener."""
from __future__ import annotations

import pytest

from envdiff.flattener import FlattenResult, flatten, unflatten


@pytest.fixture()
def nested_env() -> dict:
    return {
        "DB__HOST": "localhost",
        "DB__PORT": "5432",
        "APP__DEBUG": "true",
        "PLAIN_KEY": "value",
    }


# ---------------------------------------------------------------------------
# flatten()
# ---------------------------------------------------------------------------

def test_returns_flatten_result(nested_env):
    result = flatten(nested_env)
    assert isinstance(result, FlattenResult)


def test_flat_keys_use_dot_separator(nested_env):
    result = flatten(nested_env)
    assert "db.host" in result.flat
    assert "db.port" in result.flat
    assert "app.debug" in result.flat


def test_plain_key_lowercased(nested_env):
    result = flatten(nested_env)
    assert "plain_key" in result.flat


def test_values_preserved(nested_env):
    result = flatten(nested_env)
    assert result.flat["db.host"] == "localhost"
    assert result.flat["db.port"] == "5432"


def test_mapping_tracks_original_key(nested_env):
    result = flatten(nested_env)
    assert result.mapping["db.host"] == "DB__HOST"
    assert result.mapping["plain_key"] == "PLAIN_KEY"


def test_no_skipped_in_clean_env(nested_env):
    result = flatten(nested_env)
    assert result.skipped == []


def test_collision_records_skipped():
    env = {"A__B": "first", "a__b": "second"}
    result = flatten(env)
    assert len(result.flat) == 1
    assert len(result.skipped) == 1


def test_custom_delimiter():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432"}
    result = flatten(env, delimiter=".")
    assert "db.host" in result.flat
    assert "db.port" in result.flat


def test_max_depth_limits_splitting():
    env = {"A__B__C__D": "deep"}
    result = flatten(env, max_depth=2)
    # parts: ['A', 'B', 'C__D'] -> 'a.b.c__d'
    assert "a.b.c__d" in result.flat


def test_summary_string(nested_env):
    result = flatten(nested_env)
    s = result.summary()
    assert "Flattened" in s
    assert "Skipped" in s


# ---------------------------------------------------------------------------
# unflatten()
# ---------------------------------------------------------------------------

def test_unflatten_reverses_flatten():
    flat = {"db.host": "localhost", "app.debug": "true"}
    result = unflatten(flat)
    assert result["DB__HOST"] == "localhost"
    assert result["APP__DEBUG"] == "true"


def test_unflatten_custom_delimiter():
    flat = {"db.host": "localhost"}
    result = unflatten(flat, delimiter=".")
    assert result["DB.HOST"] == "localhost"


def test_roundtrip(nested_env):
    flat_result = flatten(nested_env)
    restored = unflatten(flat_result.flat)
    for original_key, value in nested_env.items():
        assert restored.get(original_key) == value
