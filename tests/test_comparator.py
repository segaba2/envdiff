"""Tests for envdiff.comparator module."""

import pytest
from envdiff.comparator import compare_envs, DiffResult


ENV_A = {
    "APP_NAME": "myapp",
    "DEBUG": "true",
    "SECRET_KEY": "abc123",
    "ONLY_IN_A": "yes",
}

ENV_B = {
    "APP_NAME": "myapp",
    "DEBUG": "false",
    "SECRET_KEY": "abc123",
    "ONLY_IN_B": "yes",
}


def test_no_diff_identical_envs():
    env = {"KEY": "value", "OTHER": "thing"}
    result = compare_envs(env, env.copy())
    assert not result.has_diff


def test_missing_in_b():
    result = compare_envs(ENV_A, ENV_B)
    assert "ONLY_IN_A" in result.missing_in_b


def test_missing_in_a():
    result = compare_envs(ENV_A, ENV_B)
    assert "ONLY_IN_B" in result.missing_in_a


def test_mismatch_detected():
    result = compare_envs(ENV_A, ENV_B)
    assert "DEBUG" in result.mismatched
    assert result.mismatched["DEBUG"] == ("true", "false")


def test_no_false_mismatch():
    result = compare_envs(ENV_A, ENV_B)
    assert "SECRET_KEY" not in result.mismatched
    assert "APP_NAME" not in result.mismatched


def test_has_diff_true():
    result = compare_envs(ENV_A, ENV_B)
    assert result.has_diff


def test_empty_envs():
    result = compare_envs({}, {})
    assert not result.has_diff


def test_summary_no_diff():
    env = {"X": "1"}
    result = compare_envs(env, env.copy())
    assert result.summary() == "No differences found."


def test_summary_contains_labels():
    result = compare_envs({"A": "1"}, {"B": "2"})
    summary = result.summary(label_a="prod", label_b="dev")
    assert "prod" in summary
    assert "dev" in summary


def test_none_values_compared():
    result = compare_envs({"KEY": None}, {"KEY": ""})
    assert "KEY" in result.mismatched
