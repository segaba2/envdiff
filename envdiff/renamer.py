"""Suggest or apply key renames across env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RenameResult:
    applied: Dict[str, str] = field(default_factory=dict)   # old -> new
    skipped: List[str] = field(default_factory=list)        # keys not found
    env: Dict[str, str] = field(default_factory=dict)       # resulting env

    def summary(self) -> str:
        parts = []
        if self.applied:
            parts.append(f"{len(self.applied)} renamed")
        if self.skipped:
            parts.append(f"{len(self.skipped)} not found")
        return ", ".join(parts) if parts else "nothing to rename"


def rename(
    env: Dict[str, str],
    mapping: Dict[str, str],
) -> RenameResult:
    """Return a new env dict with keys renamed according to *mapping*.

    mapping: {old_key: new_key}
    Keys in mapping that are absent from env are recorded as skipped.
    """
    result_env: Dict[str, str] = {}
    applied: Dict[str, str] = {}
    skipped: List[str] = []

    for key, value in env.items():
        if key in mapping:
            new_key = mapping[key]
            result_env[new_key] = value
            applied[key] = new_key
        else:
            result_env[key] = value

    for old_key in mapping:
        if old_key not in env:
            skipped.append(old_key)

    return RenameResult(applied=applied, skipped=skipped, env=result_env)


def suggest_renames(a: Dict[str, str], b: Dict[str, str]) -> List[Tuple[str, str]]:
    """Suggest possible renames: keys only in *a* paired with keys only in *b*
    that share the same value, hinting at a rename between environments.
    """
    only_a = {k: v for k, v in a.items() if k not in b}
    only_b = {k: v for k, v in b.items() if k not in a}

    suggestions: List[Tuple[str, str]] = []
    for ka, va in only_a.items():
        for kb, vb in only_b.items():
            if va == vb and va != "":
                suggestions.append((ka, kb))
    return suggestions
