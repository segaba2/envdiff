"""Tests for envdiff.duplicator."""
import pytest
from envdiff.duplicator import find_duplicates, DuplicateResult


@pytest.fixture
def env_with_dupes():
    return {
        "DB_HOST": "localhost",
        "CACHE_HOST": "localhost",
        "SECRET_KEY": "abc123",
        "API_KEY": "abc123",
        "PORT": "8080",
    }


@pytest.fixture
def clean_env():
    return {
        "HOST": "localhost",
        "PORT": "8080",
        "DEBUG": "true",
    }


def test_detects_duplicate_values(env_with_dupes):
    result = find_duplicates(env_with_dupes)
    assert result.has_duplicates


def test_duplicate_groups_correct_keys(env_with_dupes):
    result = find_duplicates(env_with_dupes)
    assert set(result.duplicates["localhost"]) == {"DB_HOST", "CACHE_HOST"}
    assert set(result.duplicates["abc123"]) == {"SECRET_KEY", "API_KEY"}


def test_unique_value_not_flagged(env_with_dupes):
    result = find_duplicates(env_with_dupes)
    assert "8080" not in result.duplicates


def test_no_duplicates_in_clean_env(clean_env):
    result = find_duplicates(clean_env)
    assert not result.has_duplicates


def test_blank_values_ignored_by_default():
    env = {"A": "", "B": "", "C": "value"}
    result = find_duplicates(env, ignore_blank=True)
    assert not result.has_duplicates


def test_blank_values_flagged_when_not_ignored():
    env = {"A": "", "B": "", "C": "value"}
    result = find_duplicates(env, ignore_blank=False)
    assert result.has_duplicates
    assert set(result.duplicates[""]) == {"A", "B"}


def test_summary_no_duplicates(clean_env):
    result = find_duplicates(clean_env)
    assert result.summary() == "No duplicate values found."


def test_summary_with_duplicates(env_with_dupes):
    result = find_duplicates(env_with_dupes)
    summary = result.summary()
    assert "Duplicate values detected:" in summary
    assert "localhost" in summary
    assert "abc123" in summary


def test_result_stores_original_env(env_with_dupes):
    result = find_duplicates(env_with_dupes)
    assert result.env == env_with_dupes
