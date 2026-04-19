"""Matrix diff: compare every file against every other file in a set."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from envdiff.comparator import DiffResult, compare
from envdiff.parser import parse_env_file


@dataclass
class MatrixResult:
    files: List[str]
    cells: Dict[Tuple[str, str], DiffResult] = field(default_factory=dict)

    def any_diff(self) -> bool:
        return any(r.has_diff() for r in self.cells.values())

    def pairs_with_diff(self) -> List[Tuple[str, str]]:
        return [pair for pair, r in self.cells.items() if r.has_diff()]

    def summary(self) -> str:
        total = len(self.cells)
        dirty = len(self.pairs_with_diff())
        return f"{dirty}/{total} pairs have differences"


def diff_matrix(paths: List[str]) -> MatrixResult:
    """Parse all files then compare every ordered pair (a, b) where a != b."""
    envs: Dict[str, dict] = {}
    for p in paths:
        envs[p] = parse_env_file(p)

    result = MatrixResult(files=list(paths))
    for i, a in enumerate(paths):
        for b in paths[i + 1 :]:
            result.cells[(a, b)] = compare(envs[a], envs[b])
    return result
