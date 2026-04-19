"""Extended diff utilities: multi-file diff and summary stats."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envdiff.comparator import DiffResult, compare
from envdiff.parser import parse_env_file


@dataclass
class MultiDiffResult:
    pairs: Dict[str, DiffResult] = field(default_factory=dict)

    def any_diff(self) -> bool:
        return any(r.has_diff() for r in self.pairs.values())

    def summary(self) -> str:
        lines = []
        for label, result in self.pairs.items():
            status = "DIFF" if result.has_diff() else "OK"
            lines.append(f"{label}: {status}")
        return "\n".join(lines)

    def total_missing_a(self) -> int:
        return sum(len(r.missing_in_a) for r in self.pairs.values())

    def total_missing_b(self) -> int:
        return sum(len(r.missing_in_b) for r in self.pairs.values())

    def total_mismatches(self) -> int:
        return sum(len(r.mismatches) for r in self.pairs.values())


def diff_many(base: str, others: List[str]) -> MultiDiffResult:
    """Diff base env file against each file in others."""
    base_env = parse_env_file(base)
    result = MultiDiffResult()
    for path in others:
        other_env = parse_env_file(path)
        label = f"{base} vs {path}"
        result.pairs[label] = compare(base_env, other_env)
    return result
