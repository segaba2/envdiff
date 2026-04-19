"""Multi-file diff: compare many pairs and aggregate results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from envdiff.differ import diff_files
from envdiff.comparator import DiffResult


@dataclass
class MultiDiffResult:
    pairs: List[Tuple[str, str]]
    diffs: List[DiffResult]

    @property
    def any_diff(self) -> bool:
        from envdiff.comparator import has_diff
        return any(has_diff(d) for d in self.diffs)

    @property
    def total_missing_a(self) -> int:
        return sum(len(d.missing_in_a) for d in self.diffs)

    @property
    def total_missing_b(self) -> int:
        return sum(len(d.missing_in_b) for d in self.diffs)

    @property
    def total_mismatches(self) -> int:
        return sum(len(d.mismatches) for d in self.diffs)

    def summary(self) -> str:
        if not self.any_diff:
            return "All pairs identical."
        parts = []
        if self.total_missing_a:
            parts.append(f"missing_in_a={self.total_missing_a}")
        if self.total_missing_b:
            parts.append(f"missing_in_b={self.total_missing_b}")
        if self.total_mismatches:
            parts.append(f"mismatches={self.total_mismatches}")
        return "Differences found: " + ", ".join(parts)


def diff_many(
    pairs: List[Tuple[str, str]],
    exclude: Optional[List[str]] = None,
    prefix: Optional[str] = None,
) -> MultiDiffResult:
    """Run diff_files on each pair and collect results."""
    results: List[DiffResult] = []
    for a, b in pairs:
        dr = diff_files(a, b, exclude=exclude or [], prefix=prefix)
        results.append(dr)
    return MultiDiffResult(pairs=list(pairs), diffs=results)
