"""Resolve final effective env by merging multiple files with override chain."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class ResolveResult:
    effective: Dict[str, str]
    sources: Dict[str, str]  # key -> path that last set it
    overrides: Dict[str, List[str]]  # key -> list of paths that defined it

    def summary(self) -> str:
        total = len(self.effective)
        contested = sum(1 for v in self.overrides.values() if len(v) > 1)
        return f"{total} keys resolved; {contested} overridden across files"


def resolve(paths: List[str | Path], base: Optional[str | Path] = None) -> ResolveResult:
    """Merge env files left-to-right; later files override earlier ones.

    If *base* is given it is loaded first (lowest priority).
    """
    ordered: List[Path] = []
    if base is not None:
        ordered.append(Path(base))
    ordered.extend(Path(p) for p in paths)

    effective: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    overrides: Dict[str, List[str]] = {}

    for path in ordered:
        env = parse_env_file(path)
        for key, value in env.items():
            overrides.setdefault(key, [])
            overrides[key].append(str(path))
            effective[key] = value
            sources[key] = str(path)

    return ResolveResult(effective=effective, sources=sources, overrides=overrides)
