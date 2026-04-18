"""Filtering utilities for envdiff — allow ignoring keys by pattern."""

from __future__ import annotations

import fnmatch
from typing import Iterable


def matches_any(key: str, patterns: Iterable[str]) -> bool:
    """Return True if *key* matches any of the given glob patterns."""
    return any(fnmatch.fnmatch(key, pattern) for pattern in patterns)


def filter_keys(
    env: dict[str, str],
    ignore_patterns: Iterable[str],
) -> dict[str, str]:
    """Return a copy of *env* with keys matching *ignore_patterns* removed.

    Parameters
    ----------
    env:
        Parsed environment mapping.
    ignore_patterns:
        Iterable of glob-style patterns (e.g. ``["SECRET_*", "CI_*"]``).
    """
    patterns = list(ignore_patterns)
    if not patterns:
        return dict(env)
    return {k: v for k, v in env.items() if not matches_any(k, patterns)}


def filter_prefix(
    env: dict[str, str],
    prefix: str,
) -> dict[str, str]:
    """Return only keys that start with *prefix* (case-sensitive)."""
    return {k: v for k, v in env.items() if k.startswith(prefix)}
