"""Deduplicator: remove duplicate keys from a parsed env dict, keeping a
configurable occurrence (first or last) and reporting what was dropped."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal


@dataclass
class DeduplicateResult:
    kept: Dict[str, str]
    dropped: Dict[str, List[str]]  # key -> list of dropped values

    def has_duplicates(self) -> bool:
        return bool(self.dropped)

    def summary(self) -> str:
        if not self.has_duplicates():
            return "No duplicate keys found."
        lines = [f"Removed {len(self.dropped)} duplicate key(s):"]
        for key, vals in sorted(self.dropped.items()):
            dropped_repr = ", ".join(repr(v) for v in vals)
            lines.append(f"  {key}: dropped {dropped_repr}")
        return "\n".join(lines)


def deduplicate(
    entries: List[tuple],
    strategy: Literal["first", "last"] = "first",
) -> DeduplicateResult:
    """Deduplicate a list of (key, value) pairs (preserving parse order).

    Parameters
    ----------
    entries:
        Ordered sequence of (key, value) pairs as returned by a line-by-line
        parser that does *not* collapse duplicates itself.
    strategy:
        ``"first"`` keeps the first occurrence; ``"last"`` keeps the last.
    """
    seen: Dict[str, List[str]] = {}
    for key, value in entries:
        seen.setdefault(key, []).append(value)

    kept: Dict[str, str] = {}
    dropped: Dict[str, List[str]] = {}

    for key, values in seen.items():
        if strategy == "last":
            values = list(reversed(values))
        kept[key] = values[0]
        if len(values) > 1:
            dropped[key] = values[1:]

    return DeduplicateResult(kept=kept, dropped=dropped)


def deduplicate_env(
    env: Dict[str, str],
) -> DeduplicateResult:
    """Convenience wrapper when duplicates have already been collapsed into a
    plain dict (no duplicates possible — returns a clean result)."""
    return DeduplicateResult(kept=dict(env), dropped={})
