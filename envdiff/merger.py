"""Merge multiple .env files into a single unified dict, with conflict tracking."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class MergeResult:
    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def summary(self) -> str:
        if not self.has_conflicts:
            return "No conflicts."
        lines = [f"{len(self.conflicts)} conflicting key(s):"]
        for key, sources in self.conflicts.items():
            for src, val in sources:
                lines.append(f"  {key}: {val!r} (from {src})")
        return "\n".join(lines)


def merge(env_maps: Dict[str, Dict[str, str]], strategy: str = "first") -> MergeResult:
    """Merge named env dicts.

    strategy:
      'first'  – keep first value seen (default)
      'last'   – keep last value seen
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown strategy {strategy!r}. Use 'first' or 'last'.")

    merged: Dict[str, str] = {}
    conflicts: Dict[str, List[Tuple[str, str]]] = {}
    seen: Dict[str, str] = {}  # key -> source name

    for source, env in env_maps.items():
        for key, value in env.items():
            if key not in merged:
                merged[key] = value
                seen[key] = source
            else:
                if merged[key] != value:
                    if key not in conflicts:
                        conflicts[key] = [(seen[key], merged[key])]
                    conflicts[key].append((source, value))
                    if strategy == "last":
                        merged[key] = value
                        seen[key] = source

    return MergeResult(merged=merged, conflicts=conflicts)
