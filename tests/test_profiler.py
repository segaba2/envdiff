"""Tests for envdiff.profiler."""
import pytest
from envdiff.profiler import profile, ProfileResult


@pytest.fixture()
def sample() -> dict:
    return {
        "APP_NAME": "myapp",
        "DB_HOST": "localhost",
        "DB_PASS": "secret",
        "API_KEY": "secret",   # duplicate value with DB_PASS
        "EMPTY_VAR": "",
        "ANOTHER_EMPTY": "",
        "LONG_KEY_NAME_HERE": "short",
        "X": "a_much_longer_value_string",
    }


def test_total_keys(sample):
    r = profile(sample)
    assert r.total_keys == 8


def test_blank_values(sample):
    r = profile(sample)
    assert set(r.blank_values) == {"EMPTY_VAR", "ANOTHER_EMPTY"}


def test_duplicate_values(sample):
    r = profile(sample)
    assert "secret" in r.duplicate_values
    assert set(r.duplicate_values["secret"]) == {"DB_PASS", "API_KEY"}


def test_no_false_duplicates(sample):
    r = profile(sample)
    # unique values should not appear
    for v, ks in r.duplicate_values.items():
        assert len(ks) > 1


def test_longest_key(sample):
    r = profile(sample)
    assert r.longest_key == "LONG_KEY_NAME_HERE"


def test_longest_value_key(sample):
    r = profile(sample)
    assert r.longest_value_key == "X"


def test_empty_env():
    r = profile({})
    assert r.total_keys == 0
    assert r.blank_values == []
    assert r.duplicate_values == {}
    assert r.longest_key == ""
    assert r.longest_value_key == ""


def test_summary_contains_counts(sample):
    r = profile(sample)
    s = r.summary()
    assert "8" in s
    assert "2" in s  # blank values count


def test_profile_result_is_dataclass():
    r = ProfileResult()
    assert r.total_keys == 0
