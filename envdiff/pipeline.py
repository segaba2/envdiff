"""Fluent pipeline for parsing, filtering, sorting, diffing, and optionally merging env files."""

from __future__ import annotations
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file
from envdiff.filter import filter_keys, filter_prefix
from envdiff.sorter import sort_keys
from envdiff.comparator import DiffResult, compare
from envdiff.merger import MergeResult, merge as _merge


class Pipeline:
    def __init__(self) -> None:
        self._files: Dict[str, str] = {}  # label -> path
        self._exclude: List[str] = []
        self._prefix: Optional[str] = None
        self._sort: str = "alpha"
        self._envs: Dict[str, Dict[str, str]] = {}

    def files(self, **labeled_paths: str) -> "Pipeline":
        self._files.update(labeled_paths)
        return self

    def exclude(self, *patterns: str) -> "Pipeline":
        self._exclude.extend(patterns)
        return self

    def prefix(self, prefix: str) -> "Pipeline":
        self._prefix = prefix
        return self

    def sort(self, order: str = "alpha") -> "Pipeline":
        self._sort = order
        return self

    def _load(self) -> None:
        self._envs = {}
        for label, path in self._files.items():
            env = parse_env_file(path)
            if self._prefix:
                env = filter_prefix(env, self._prefix)
            if self._exclude:
                env = filter_keys(env, self._exclude)
            self._envs[label] = env

    def diff(self) -> DiffResult:
        self._load()
        labels = list(self._envs)
        if len(labels) < 2:
            raise ValueError("Need at least two files to diff.")
        a_label, b_label = labels[0], labels[1]
        result = compare(self._envs[a_label], self._envs[b_label])
        keys = sort_keys(result, order=self._sort)
        return result

    def merge(self, strategy: str = "first") -> MergeResult:
        self._load()
        return _merge(self._envs, strategy=strategy)

    def envs(self) -> Dict[str, Dict[str, str]]:
        self._load()
        return dict(self._envs)
