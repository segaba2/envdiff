import pytest
from envdiff.merger import merge, MergeResult


A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
B = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc"}
C = {"HOST": "staging.example.com", "SECRET": "xyz"}


def test_merge_no_conflict():
    result = merge({"a": {"KEY": "val"}, "b": {"OTHER": "x"}})
    assert result.merged == {"KEY": "val", "OTHER": "x"}
    assert not result.has_conflicts


def test_merge_first_strategy_keeps_first():
    result = merge({"a": A, "b": B}, strategy="first")
    assert result.merged["HOST"] == "localhost"
    assert "HOST" in result.conflicts


def test_merge_last_strategy_keeps_last():
    result = merge({"a": A, "b": B}, strategy="last")
    assert result.merged["HOST"] == "prod.example.com"
    assert "HOST" in result.conflicts


def test_merge_no_conflict_on_same_value():
    result = merge({"a": A, "b": B})
    assert "PORT" not in result.conflicts
    assert result.merged["PORT"] == "5432"


def test_merge_collects_all_sources_in_conflict():
    result = merge({"a": A, "b": B, "c": C})
    assert "HOST" in result.conflicts
    sources = [src for src, _ in result.conflicts["HOST"]]
    assert "a" in sources
    assert "b" in sources


def test_merge_union_of_keys():
    result = merge({"a": A, "b": B})
    assert "DEBUG" in result.merged
    assert "SECRET" in result.merged


def test_summary_no_conflicts():
    result = merge({"a": {"X": "1"}, "b": {"Y": "2"}})
    assert result.summary() == "No conflicts."


def test_summary_with_conflicts():
    result = merge({"a": A, "b": B})
    summary = result.summary()
    assert "HOST" in summary
    assert "localhost" in summary


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        merge({"a": A}, strategy="random")


def test_empty_inputs():
    result = merge({})
    assert result.merged == {}
    assert not result.has_conflicts
