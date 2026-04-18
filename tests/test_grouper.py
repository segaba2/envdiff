import pytest
from envdiff.grouper import group, flat_group, GroupResult


@pytest.fixture()
def sample():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "APP_DEBUG": "true",
        "PORT": "8080",
    }


def test_groups_by_detected_prefix(sample):
    result = group(sample)
    assert "DB" in result.groups
    assert "AWS" in result.groups
    assert "APP" in result.groups


def test_ungrouped_key_no_prefix(sample):
    result = group(sample)
    assert "PORT" in result.ungrouped


def test_group_values_correct(sample):
    result = group(sample)
    assert result.groups["DB"]["DB_HOST"] == "localhost"
    assert result.groups["AWS"]["AWS_SECRET"] == "xyz"


def test_explicit_prefixes_filter(sample):
    result = group(sample, prefixes=["DB", "AWS"])
    assert "APP" not in result.groups
    assert "APP_DEBUG" in result.ungrouped


def test_explicit_prefixes_case_insensitive(sample):
    result = group(sample, prefixes=["db"])
    assert "DB" in result.groups


def test_group_names_sorted(sample):
    result = group(sample)
    assert result.group_names() == sorted(result.group_names())


def test_summary_contains_group_names(sample):
    result = group(sample)
    s = result.summary()
    assert "DB" in s
    assert "AWS" in s


def test_summary_ungrouped(sample):
    result = group(sample)
    assert "ungrouped" in result.summary()


def test_flat_group_returns_sorted_keys(sample):
    result = group(sample)
    fg = flat_group(result)
    assert fg["DB"] == sorted(result.groups["DB"].keys())


def test_flat_group_includes_ungrouped(sample):
    result = group(sample)
    fg = flat_group(result)
    assert "(ungrouped)" in fg
    assert "PORT" in fg["(ungrouped)"]


def test_empty_env():
    result = group({})
    assert result.groups == {}
    assert result.ungrouped == {}
    assert result.summary() == "no keys"
