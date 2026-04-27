"""Trace the origin of each key across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class TraceEntry:
    key: str
    value: str
    source: str  # file path string

    def to_dict(self) -> dict:
        return {"key": self.key, "value": self.value, "source": self.source}


@dataclass
class TraceResult:
    # key -> list of (source, value) in file order
    traces: Dict[str, List[TraceEntry]] = field(default_factory=dict)

    def sources_for(self, key: str) -> List[str]:
        """Return file paths that define *key*."""
        return [e.source for e in self.traces.get(key, [])]

    def winning_entry(self, key: str) -> Optional[TraceEntry]:
        """Last file wins (override semantics)."""
        entries = self.traces.get(key, [])
        return entries[-1] if entries else None

    def all_keys(self) -> List[str]:
        return sorted(self.traces.keys())

    def summary(self) -> str:
        lines = []
        for key in self.all_keys():
            entries = self.traces[key]
            winner = entries[-1]
            conflict = len(entries) > 1 and len({e.value for e in entries}) > 1
            tag = " [conflict]" if conflict else ""
            lines.append(f"{key}={winner.value!r} <- {winner.source}{tag}")
        return "\n".join(lines) if lines else "(no keys traced)"


def trace(files: List[str]) -> TraceResult:
    """Parse *files* in order and record every definition of every key."""
    result = TraceResult()
    for path_str in files:
        path = Path(path_str)
        env = parse_env_file(path)
        for key, value in env.items():
            entry = TraceEntry(key=key, value=value, source=str(path))
            result.traces.setdefault(key, []).append(entry)
    return result
