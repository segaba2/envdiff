"""Graph-based diff: build a dependency/relationship graph across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from envdiff.comparator import compare
from envdiff.parser import parse_env_file


@dataclass
class GraphEdge:
    file_a: str
    file_b: str
    missing_in_a: List[str]
    missing_in_b: List[str]
    mismatches: List[str]

    def has_diff(self) -> bool:
        return bool(self.missing_in_a or self.missing_in_b or self.mismatches)

    def to_dict(self) -> dict:
        return {
            "file_a": self.file_a,
            "file_b": self.file_b,
            "missing_in_a": self.missing_in_a,
            "missing_in_b": self.missing_in_b,
            "mismatches": self.mismatches,
            "has_diff": self.has_diff(),
        }


@dataclass
class GraphResult:
    files: List[str]
    edges: List[GraphEdge] = field(default_factory=list)

    def any_diff(self) -> bool:
        return any(e.has_diff() for e in self.edges)

    def isolated_files(self) -> List[str]:
        """Files that share no diff with any other file."""
        connected: Set[str] = set()
        for e in self.edges:
            if e.has_diff():
                connected.add(e.file_a)
                connected.add(e.file_b)
        return sorted(f for f in self.files if f not in connected)

    def summary(self) -> str:
        total = len(self.edges)
        dirty = sum(1 for e in self.edges if e.has_diff())
        return (
            f"{len(self.files)} files, {total} pairs compared, "
            f"{dirty} with differences"
        )


def build_graph(paths: List[str]) -> GraphResult:
    """Compare every unique pair of env files and return a GraphResult."""
    envs: Dict[str, dict] = {}
    for p in paths:
        envs[p] = parse_env_file(p)

    edges: List[GraphEdge] = []
    files = list(paths)
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            a, b = files[i], files[j]
            result = compare(envs[a], envs[b])
            edges.append(
                GraphEdge(
                    file_a=a,
                    file_b=b,
                    missing_in_a=result.missing_in_a,
                    missing_in_b=result.missing_in_b,
                    mismatches=result.mismatches,
                )
            )

    return GraphResult(files=files, edges=edges)
