"""trimmer.py – strip unused or stale keys from an env file.

A key is considered *stale* when it appears in the env but not in a
reference set (e.g. a template or another env file).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class TrimResult:
    kept: Dict[str, str]
    removed: List[str]
    source_keys: Set[str]

    # ------------------------------------------------------------------
    def has_removals(self) -> bool:
        return bool(self.removed)

    def summary(self) -> str:
        if not self.has_removals():
            return "No stale keys found – nothing to trim."
        keys = ", ".join(sorted(self.removed))
        return (
            f"{len(self.removed)} stale key(s) removed: {keys}. "
            f"{len(self.kept)} key(s) retained."
        )


def trim(
    env: Dict[str, str],
    reference: Set[str],
    *,
    ignore_case: bool = False,
) -> TrimResult:
    """Return a TrimResult keeping only keys present in *reference*.

    Parameters
    ----------
    env:
        Parsed env mapping (key -> value).
    reference:
        Set of key names that are considered *active*.
    ignore_case:
        When True, key comparison is case-insensitive.
    """
    if ignore_case:
        ref_normalised: Set[str] = {k.upper() for k in reference}

        def _in_ref(k: str) -> bool:
            return k.upper() in ref_normalised
    else:
        def _in_ref(k: str) -> bool:  # type: ignore[misc]
            return k in reference

    kept: Dict[str, str] = {}
    removed: List[str] = []

    for key, value in env.items():
        if _in_ref(key):
            kept[key] = value
        else:
            removed.append(key)

    return TrimResult(kept=kept, removed=sorted(removed), source_keys=set(reference))


def trim_to_template(
    env: Dict[str, str],
    template: Dict[str, str],
    *,
    ignore_case: bool = False,
) -> TrimResult:
    """Convenience wrapper: derive the reference set from a template dict."""
    return trim(env, set(template.keys()), ignore_case=ignore_case)
