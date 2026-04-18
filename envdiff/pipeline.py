"""Pipeline builder: chain diff steps with a fluent API."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.differ import diff_files
from envdiff.reporter import render, exit_code


@dataclass
class Pipeline:
    """Fluent builder for a full envdiff run."""

    _path_a: str = ""
    _path_b: str = ""
    _exclude: List[str] = field(default_factory=list)
    _prefix: Optional[str] = None
    _sort: str = "alpha"
    _format: str = "text"
    _color: bool = True

    def files(self, path_a: str, path_b: str) -> Pipeline:
        self._path_a = path_a
        self._path_b = path_b
        return self

    def exclude(self, *patterns: str) -> Pipeline:
        self._exclude.extend(patterns)
        return self

    def prefix(self, prefix: str) -> Pipeline:
        self._prefix = prefix
        return self

    def sort(self, strategy: str) -> Pipeline:
        self._sort = strategy
        return self

    def format(self, fmt: str) -> Pipeline:
        self._format = fmt
        return self

    def no_color(self) -> Pipeline:
        self._color = False
        return self

    def run(self) -> int:
        """Execute the pipeline and return an exit code (0 = no diff)."""
        if not self._path_a or not self._path_b:
            raise ValueError("Both file paths must be set before calling run().")

        result = diff_files(
            self._path_a,
            self._path_b,
            exclude_patterns=self._exclude or None,
            prefix=self._prefix,
            sort=self._sort,
        )
        output = render(result, fmt=self._format, color=self._color)
        print(output, end="")
        return exit_code(result)
