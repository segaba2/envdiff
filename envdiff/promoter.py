"""Promote keys from one environment file to another, tracking additions and conflicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PromoteResult:
    promoted: Dict[str, str] = field(default_factory=dict)
    skipped: Dict[str, str] = field(default_factory=dict)
    conflicts: Dict[str, tuple] = field(default_factory=dict)  # key -> (src_val, dst_val)

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def summary(self) -> str:
        parts = []
        if self.promoted:
            parts.append(f"{len(self.promoted)} promoted")
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped (already present)")
        if self.conflicts:
            parts.append(f"{len(self.conflicts)} conflict(s)")
        return ", ".join(parts) if parts else "nothing to promote"


def promote(
    source: Dict[str, str],
    destination: Dict[str, str],
    keys: List[str] | None = None,
    overwrite: bool = False,
) -> PromoteResult:
    """Promote keys from *source* into *destination*.

    Args:
        source:      Parsed env dict to copy keys from.
        destination: Parsed env dict to copy keys into.
        keys:        Explicit list of keys to promote; if None, promote all source keys.
        overwrite:   When True, overwrite conflicting keys; otherwise record them.

    Returns:
        PromoteResult with the merged env under `promoted`, plus metadata.
    """
    result = PromoteResult(promoted=dict(destination))
    candidates = keys if keys is not None else list(source.keys())

    for key in candidates:
        if key not in source:
            continue
        src_val = source[key]
        if key in destination:
            dst_val = destination[key]
            if src_val == dst_val:
                result.skipped[key] = src_val
            elif overwrite:
                result.promoted[key] = src_val
                result.conflicts[key] = (src_val, dst_val)
            else:
                result.conflicts[key] = (src_val, dst_val)
        else:
            result.promoted[key] = src_val

    return result
