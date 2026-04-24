"""Tests for envdiff.promoter."""
from __future__ import annotations

import pytest

from envdiff.promoter import PromoteResult, promote


@pytest.fixture
def source() -> dict:
    return {"DB_HOST": "prod-db", "DB_PORT": "5432", "SECRET_KEY": "s3cr3t"}


@pytest.fixture
def destination() -> dict:
    return {"DB_HOST": "localhost", "APP_ENV": "staging"}


def test_new_key_promoted(source, destination):
    result = promote(source, destination)
    assert result.promoted["DB_PORT"] == "5432"
    assert result.promoted["SECRET_KEY"] == "s3cr3t"


def test_existing_key_not_overwritten_by_default(source, destination):
    result = promote(source, destination)
    # DB_HOST exists in destination with different value -> conflict, not overwritten
    assert result.promoted.get("DB_HOST") == "localhost"


def test_conflict_recorded(source, destination):
    result = promote(source, destination)
    assert "DB_HOST" in result.conflicts
    assert result.conflicts["DB_HOST"] == ("prod-db", "localhost")


def test_overwrite_resolves_conflict(source, destination):
    result = promote(source, destination, overwrite=True)
    assert result.promoted["DB_HOST"] == "prod-db"
    assert "DB_HOST" in result.conflicts  # still recorded


def test_identical_value_skipped(source):
    dst = {"DB_PORT": "5432"}
    result = promote(source, dst)
    assert "DB_PORT" in result.skipped
    assert "DB_PORT" not in result.conflicts


def test_explicit_keys_limits_promotion(source, destination):
    result = promote(source, destination, keys=["DB_PORT"])
    assert "DB_PORT" in result.promoted
    assert "SECRET_KEY" not in result.promoted


def test_missing_explicit_key_ignored(source, destination):
    result = promote(source, destination, keys=["NONEXISTENT"])
    # nothing promoted from source, destination preserved
    assert result.promoted == destination


def test_has_conflicts_true(source, destination):
    result = promote(source, destination)
    assert result.has_conflicts() is True


def test_has_conflicts_false():
    result = promote({"A": "1"}, {})
    assert result.has_conflicts() is False


def test_summary_no_conflicts():
    result = promote({"X": "1"}, {})
    assert "promoted" in result.summary()
    assert "conflict" not in result.summary()


def test_summary_with_conflicts(source, destination):
    result = promote(source, destination)
    assert "conflict" in result.summary()


def test_empty_source_returns_destination_unchanged(destination):
    result = promote({}, destination)
    assert result.promoted == destination
    assert not result.conflicts
