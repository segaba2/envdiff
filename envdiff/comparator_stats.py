"""Aggregate statistics across multiple DiffResult objects."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envdiff.comparator import DiffResult


@dataclass
class ComparatorStats:
    total_pairs: int = 0
    total_keys_compared: int = 0
    total_missing_a: int = 0
    total_missing_b: int = 0
    total_mismatches: int = 0
    clean_pairs: int = 0
    dirty_pairs: int = 0
    labels: List[str] = field(default_factory=list)

    @property
    def diff_rate(self) -> float:
        """Fraction of pairs that have at least one diff (0.0–1.0)."""
        if self.total_pairs == 0:
            return 0.0
        return self.dirty_pairs / self.total_pairs

    def summary(self) -> str:
        return (
            f"pairs={self.total_pairs} clean={self.clean_pairs} "
            f"dirty={self.dirty_pairs} "
            f"missing_a={self.total_missing_a} "
            f"missing_b={self.total_missing_b} "
            f"mismatches={self.total_mismatches} "
            f"diff_rate={self.diff_rate:.0%}"
        )


def compute_comparator_stats(
    results: List[DiffResult],
    labels: List[str] | None = None,
) -> ComparatorStats:
    """Compute aggregate stats from a list of DiffResult objects."""
    stats = ComparatorStats()
    stats.total_pairs = len(results)
    stats.labels = list(labels) if labels else []

    for dr in results:
        all_keys = set(dr.missing_in_a) | set(dr.missing_in_b) | set(dr.mismatches)
        stats.total_keys_compared += len(
            set(dr.missing_in_a) | set(dr.missing_in_b) |
            set(dr.mismatches) | set(dr.common)
        )
        stats.total_missing_a += len(dr.missing_in_a)
        stats.total_missing_b += len(dr.missing_in_b)
        stats.total_mismatches += len(dr.mismatches)
        if all_keys:
            stats.dirty_pairs += 1
        else:
            stats.clean_pairs += 1

    return stats
