"""Tests for envdiff.sorter."""
import pytest
from envdiff.comparator import DiffResult
from envdiff.sorter import all_keys, sort_keys, group_by_status


@pytest.fixture()
def mixed_result() -> DiffResult:
    return DiffResult(
        missing_in_a={"ZEBRA"},
        missing_in_b={"ALPHA"},
        mismatches={"MIDDLE": ("x", "y")},
        common={"SHARED"},
    )


def test_all_keys_union(mixed_result: DiffResult) -> None:
    keys = all_keys(mixed_result)
    assert set(keys) == {"ZEBRA", "ALPHA", "MIDDLE", "SHARED"}


def test_all_keys_sorted_alpha(mixed_result: DiffResult) -> None:
    keys = all_keys(mixed_result)
    assert keys == sorted(keys)


def test_sort_alpha_default(mixed_result: DiffResult) -> None:
    keys = sort_keys(mixed_result)
    assert keys == sorted(keys)


def test_sort_alpha_explicit(mixed_result: DiffResult) -> None:
    assert sort_keys(mixed_result, by="alpha") == sort_keys(mixed_result)


def test_sort_by_status_order(mixed_result: DiffResult) -> None:
    keys = sort_keys(mixed_result, by="status")
    # missing_in_b first, then missing_in_a, then mismatch, then ok
    assert keys.index("ALPHA") < keys.index("ZEBRA")
    assert keys.index("ZEBRA") < keys.index("MIDDLE")
    assert keys.index("MIDDLE") < keys.index("SHARED")


def test_sort_unknown_strategy_raises(mixed_result: DiffResult) -> None:
    with pytest.raises(ValueError, match="Unknown sort strategy"):
        sort_keys(mixed_result, by="invalid")  # type: ignore[arg-type]


def test_group_by_status_keys(mixed_result: DiffResult) -> None:
    groups = group_by_status(mixed_result)
    assert set(groups.keys()) == {"missing_in_a", "missing_in_b", "mismatch", "ok"}


def test_group_by_status_contents(mixed_result: DiffResult) -> None:
    groups = group_by_status(mixed_result)
    assert groups["missing_in_b"] == ["ALPHA"]
    assert groups["missing_in_a"] == ["ZEBRA"]
    assert groups["mismatch"] == ["MIDDLE"]
    assert groups["ok"] == ["SHARED"]


def test_group_by_status_empty() -> None:
    result = DiffResult(missing_in_a=set(), missing_in_b=set(), mismatches={}, common=set())
    groups = group_by_status(result)
    assert all(v == [] for v in groups.values())
