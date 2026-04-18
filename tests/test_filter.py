"""Tests for envdiff.filter."""

import pytest
from envdiff.filter import filter_keys, filter_prefix, matches_any


SAMPLE: dict[str, str] = {
    "APP_NAME": "myapp",
    "APP_ENV": "production",
    "SECRET_KEY": "abc123",
    "SECRET_TOKEN": "xyz",
    "CI_BUILD": "42",
    "DATABASE_URL": "postgres://localhost/db",
}


def test_matches_any_true():
    assert matches_any("SECRET_KEY", ["SECRET_*"]) is True


def test_matches_any_false():
    assert matches_any("APP_NAME", ["SECRET_*", "CI_*"]) is False


def test_matches_any_exact():
    assert matches_any("CI_BUILD", ["CI_BUILD"]) is True


def test_filter_keys_removes_matching():
    result = filter_keys(SAMPLE, ["SECRET_*"])
    assert "SECRET_KEY" not in result
    assert "SECRET_TOKEN" not in result
    assert "APP_NAME" in result


def test_filter_keys_multiple_patterns():
    result = filter_keys(SAMPLE, ["SECRET_*", "CI_*"])
    assert "SECRET_KEY" not in result
    assert "CI_BUILD" not in result
    assert "DATABASE_URL" in result


def test_filter_keys_no_patterns_returns_copy():
    result = filter_keys(SAMPLE, [])
    assert result == SAMPLE
    assert result is not SAMPLE


def test_filter_keys_no_match_leaves_all():
    result = filter_keys(SAMPLE, ["NONEXISTENT_*"])
    assert result == SAMPLE


def test_filter_prefix_basic():
    result = filter_prefix(SAMPLE, "APP_")
    assert set(result.keys()) == {"APP_NAME", "APP_ENV"}


def test_filter_prefix_no_match():
    result = filter_prefix(SAMPLE, "REDIS_")
    assert result == {}


def test_filter_prefix_full_key():
    result = filter_prefix(SAMPLE, "DATABASE_URL")
    assert result == {"DATABASE_URL": "postgres://localhost/db"}
