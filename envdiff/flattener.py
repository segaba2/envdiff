"""Flatten nested env-like structures into a single-level dict.

Supports keys separated by a configurable delimiter (default ``__``).
Useful when env files contain compound keys such as
``DB__HOST=localhost`` that represent nested configuration.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenResult:
    flat: Dict[str, str]
    mapping: Dict[str, str]  # flat_key -> original_key
    skipped: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Flattened keys : {len(self.flat)}",
            f"Skipped keys   : {len(self.skipped)}",
        ]
        return "\n".join(lines)


def flatten(
    env: Dict[str, str],
    delimiter: str = "__",
    max_depth: Optional[int] = None,
) -> FlattenResult:
    """Flatten *env* by splitting keys on *delimiter*.

    The resulting key is the full original key lowercased with the
    delimiter replaced by a dot, e.g. ``DB__HOST`` -> ``db.host``.
    If *max_depth* is given, splitting stops after that many levels.

    Keys that do not contain the delimiter are kept as-is (lowercased).
    """
    flat: Dict[str, str] = {}
    mapping: Dict[str, str] = {}
    skipped: List[str] = []

    for original_key, value in env.items():
        if not original_key:
            skipped.append(original_key)
            continue

        parts = original_key.split(delimiter)
        if max_depth is not None:
            # re-join any overflow back into the last segment
            if len(parts) > max_depth + 1:
                parts = parts[: max_depth] + [delimiter.join(parts[max_depth :])]

        flat_key = ".".join(p.lower() for p in parts if p)
        if not flat_key:
            skipped.append(original_key)
            continue

        if flat_key in flat:
            # collision – keep first, record skip
            skipped.append(original_key)
            continue

        flat[flat_key] = value
        mapping[flat_key] = original_key

    return FlattenResult(flat=flat, mapping=mapping, skipped=skipped)


def unflatten(
    flat: Dict[str, str],
    delimiter: str = "__",
) -> Dict[str, str]:
    """Reverse a flatten operation: convert dot-separated keys back to
    uppercase delimiter-separated keys, e.g. ``db.host`` -> ``DB__HOST``.
    """
    result: Dict[str, str] = {}
    for key, value in flat.items():
        original = delimiter.join(part.upper() for part in key.split("."))
        result[original] = value
    return result
