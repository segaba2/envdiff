"""Compute statistical summaries across multiple DiffResults."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import DiffResult


@dataclass
class DiffStats:
    """Aggregated statistics over a collection of DiffResults."""

    total_pairs: int
    pairs_with_diff: int
    pairs_clean: int
    total_missing_a: int
    total_missing_b: int
    total_mismatches: int
    most_common_missing: List[str] = field(default_factory=list)

    @property
    def diff_rate(self) -> float:
        """Fraction of pairs that have at least one difference."""
        if self.total_pairs == 0:
            return 0.0
        return self.pairs_with_diff / self.total_pairs

    def summary(self) -> str:
        lines = [
            f"Pairs compared : {self.total_pairs}",
            f"Pairs with diff: {self.pairs_with_diff} ({self.diff_rate:.0%})",
            f"Missing in A   : {self.total_missing_a}",
            f"Missing in B   : {self.total_missing_b}",
            f"Mismatches     : {self.total_mismatches}",
        ]
        if self.most_common_missing:
            lines.append("Most absent keys: " + ", ".join(self.most_common_missing[:5]))
        return "\n".join(lines)


def compute_stats(results: List[DiffResult]) -> DiffStats:
    """Compute aggregate statistics from a list of DiffResult objects."""
    pairs_with_diff = 0
    total_missing_a = 0
    total_missing_b = 0
    total_mismatches = 0
    key_absence_count: Dict[str, int] = {}

    for r in results:
        has_any = bool(r.missing_in_a or r.missing_in_b or r.mismatches)
        if has_any:
            pairs_with_diff += 1
        total_missing_a += len(r.missing_in_a)
        total_missing_b += len(r.missing_in_b)
        total_mismatches += len(r.mismatches)
        for k in list(r.missing_in_a) + list(r.missing_in_b):
            key_absence_count[k] = key_absence_count.get(k, 0) + 1

    most_common = sorted(key_absence_count, key=lambda k: -key_absence_count[k])

    return DiffStats(
        total_pairs=len(results),
        pairs_with_diff=pairs_with_diff,
        pairs_clean=len(results) - pairs_with_diff,
        total_missing_a=total_missing_a,
        total_missing_b=total_missing_b,
        total_mismatches=total_mismatches,
        most_common_missing=most_common,
    )
