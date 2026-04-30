"""stacker.py – layer multiple .env files into a single resolved view.

Later files in the stack override earlier ones; every key tracks which
file it came from and whether it was overridden.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class StackEntry:
    key: str
    value: str
    source: str          # path of the winning file
    overridden_by: Optional[str] = None  # path that last overwrote a previous value

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "source": self.source,
            "overridden_by": self.overridden_by,
        }


@dataclass
class StackResult:
    entries: List[StackEntry] = field(default_factory=list)
    files: List[str] = field(default_factory=list)

    # --- convenience helpers ---

    @property
    def resolved(self) -> Dict[str, str]:
        """Flat key→value mapping of the final merged environment."""
        return {e.key: e.value for e in self.entries}

    @property
    def overridden_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.overridden_by]

    def summary(self) -> str:
        n = len(self.entries)
        ov = len(self.overridden_keys)
        return (
            f"{n} key(s) resolved from {len(self.files)} file(s); "
            f"{ov} key(s) overridden"
        )


def stack(paths: List[str]) -> StackResult:
    """Layer *paths* in order; later files win on key collision."""
    merged: Dict[str, StackEntry] = {}

    for path in paths:
        env = parse_env_file(Path(path))
        for key, value in env.items():
            if key in merged:
                merged[key] = StackEntry(
                    key=key,
                    value=value,
                    source=path,
                    overridden_by=path,
                )
            else:
                merged[key] = StackEntry(key=key, value=value, source=path)

    return StackResult(
        entries=sorted(merged.values(), key=lambda e: e.key),
        files=list(paths),
    )
