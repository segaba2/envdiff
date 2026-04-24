import pytest
from envdiff.deduplicator import deduplicate, deduplicate_env, DeduplicateResult


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def pairs(*items):
    """Build a list of (key, value) tuples from alternating args."""
    it = iter(items)
    return list(zip(it, it))


# ---------------------------------------------------------------------------
# deduplicate()
# ---------------------------------------------------------------------------

def test_no_duplicates_returns_all_keys():
    result = deduplicate(pairs("A", "1", "B", "2"))
    assert result.kept == {"A": "1", "B": "2"}
    assert not result.has_duplicates()


def test_first_strategy_keeps_first_occurrence():
    result = deduplicate(pairs("KEY", "first", "KEY", "second"), strategy="first")
    assert result.kept["KEY"] == "first"


def test_last_strategy_keeps_last_occurrence():
    result = deduplicate(pairs("KEY", "first", "KEY", "second"), strategy="last")
    assert result.kept["KEY"] == "second"


def test_dropped_values_recorded():
    result = deduplicate(pairs("KEY", "a", "KEY", "b", "KEY", "c"), strategy="first")
    assert result.dropped["KEY"] == ["b", "c"]


def test_dropped_values_recorded_last_strategy():
    result = deduplicate(pairs("KEY", "a", "KEY", "b", "KEY", "c"), strategy="last")
    # last kept is "c"; dropped are "b" then "a" (reversed order)
    assert result.dropped["KEY"] == ["b", "a"]


def test_has_duplicates_false_when_clean():
    result = deduplicate(pairs("X", "1"))
    assert result.has_duplicates() is False


def test_has_duplicates_true_when_dupes():
    result = deduplicate(pairs("X", "1", "X", "2"))
    assert result.has_duplicates() is True


def test_other_keys_unaffected():
    result = deduplicate(pairs("A", "1", "B", "2", "A", "3"))
    assert result.kept["B"] == "2"
    assert "B" not in result.dropped


def test_empty_entries():
    result = deduplicate([])
    assert result.kept == {}
    assert result.dropped == {}


# ---------------------------------------------------------------------------
# summary()
# ---------------------------------------------------------------------------

def test_summary_no_duplicates():
    result = deduplicate(pairs("A", "1"))
    assert result.summary() == "No duplicate keys found."


def test_summary_lists_dropped_keys():
    result = deduplicate(pairs("FOO", "x", "FOO", "y"))
    summary = result.summary()
    assert "FOO" in summary
    assert "'y'" in summary


# ---------------------------------------------------------------------------
# deduplicate_env() convenience wrapper
# ---------------------------------------------------------------------------

def test_deduplicate_env_returns_clean_result():
    env = {"A": "1", "B": "2"}
    result = deduplicate_env(env)
    assert isinstance(result, DeduplicateResult)
    assert result.kept == env
    assert not result.has_duplicates()
