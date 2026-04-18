"""Utilities for sorting and grouping DiffResult keys."""
from __future__ import annotations
from typing import Literal
from envdiff.comparator import DiffResult

SortKey = Literal["alpha", "status"]

STATUS_ORDER = {"missing_in_b": 0, "missing_in_a": 1, "mismatch": 2, "ok": 3}


def _status(key: str, result: DiffResult) -> str:
    if key in result.missing_in_b:
        return "missing_in_b"
    if key in result.missing_in_a:
        return "missing_in_a"
    if key in result.mismatches:
        return "mismatch"
    return "ok"


def all_keys(result: DiffResult) -> list[str]:
    """Return the union of all keys referenced in the diff result."""
    return sorted(
        set(result.missing_in_a)
        | set(result.missing_in_b)
        | set(result.mismatches)
        | set(result.common)
    )


def sort_keys(result: DiffResult, by: SortKey = "alpha") -> list[str]:
    """Return all keys sorted by the given strategy.

    Parameters
    ----------
    result:
        The diff result whose keys should be sorted.
    by:
        ``'alpha'`` – alphabetical order (default).
        ``'status'`` – group by severity (missing > mismatch > ok).
    """
    keys = all_keys(result)
    if by == "alpha":
        return keys
    if by == "status":
        return sorted(keys, key=lambda k: (STATUS_ORDER[_status(k, result)], k))
    raise ValueError(f"Unknown sort strategy: {by!r}")


def group_by_status(result: DiffResult) -> dict[str, list[str]]:
    """Return a dict mapping status label -> sorted list of keys."""
    groups: dict[str, list[str]] = {
        "missing_in_b": [],
        "missing_in_a": [],
        "mismatch": [],
        "ok": [],
    }
    for key in all_keys(result):
        groups[_status(key, result)].append(key)
    return groups
