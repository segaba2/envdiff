"""Compare two parsed .env mappings and produce a structured diff result."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from envdiff.filter import filter_keys


@dataclass
class DiffResult:
    """Holds the outcome of comparing two .env files."""

    missing_in_a: list[str] = field(default_factory=list)
    missing_in_b: list[str] = field(default_factory=list)
    mismatched: dict[str, tuple[str, str]] = field(default_factory=dict)

    def has_diff(self) -> bool:  # noqa: D401
        return bool(self.missing_in_a or self.missing_in_b or self.mismatched)

    def summary(self) -> str:
        parts = []
        if self.missing_in_a:
            parts.append(f"{len(self.missing_in_a)} key(s) missing in A")
        if self.missing_in_b:
            parts.append(f"{len(self.missing_in_b)} key(s) missing in B")
        if self.mismatched:
            parts.append(f"{len(self.mismatched)} key(s) mismatched")
        return ", ".join(parts) if parts else "No differences"


def has_diff(result: DiffResult) -> bool:
    return result.has_diff()


def summary(result: DiffResult) -> str:
    return result.summary()


def compare_envs(
    a: dict[str, str],
    b: dict[str, str],
    *,
    ignore_patterns: Iterable[str] = (),
) -> DiffResult:
    """Compare env mappings *a* and *b*, returning a :class:`DiffResult`.

    Parameters
    ----------
    a, b:
        Parsed environment mappings to compare.
    ignore_patterns:
        Optional glob patterns for keys to skip during comparison.
    """
    patterns = list(ignore_patterns)
    a = filter_keys(a, patterns)
    b = filter_keys(b, patterns)

    keys_a = set(a)
    keys_b = set(b)

    missing_in_a = sorted(keys_b - keys_a)
    missing_in_b = sorted(keys_a - keys_b)
    mismatched = {
        k: (a[k], b[k])
        for k in keys_a & keys_b
        if a[k] != b[k]
    }

    return DiffResult(
        missing_in_a=missing_in_a,
        missing_in_b=missing_in_b,
        mismatched=mismatched,
    )
