"""aliaser.py – map canonical key names to one or more aliases.

Allows users to declare that KEY_A is also known as KEY_B (e.g. when
migrating from one naming convention to another).  The module resolves
an env dict through the alias map and reports which aliases were applied,
which were missing from the source, and what the final merged env looks like.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AliasResult:
    env: Dict[str, str]                  # resolved env (canonical keys)
    applied: Dict[str, str]              # alias -> canonical, where alias was found
    missing: List[str]                   # canonical keys absent from source AND aliases
    conflicts: Dict[str, List[str]]      # canonical key -> [alias, ...] when both present

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def summary(self) -> str:
        parts: List[str] = []
        if self.applied:
            parts.append(f"{len(self.applied)} alias(es) applied")
        if self.missing:
            parts.append(f"{len(self.missing)} key(s) missing")
        if self.conflicts:
            parts.append(f"{len(self.conflicts)} conflict(s)")
        return ", ".join(parts) if parts else "no changes"


def alias(
    env: Dict[str, str],
    aliases: Dict[str, str],   # {alias_key: canonical_key}
) -> AliasResult:
    """Resolve *env* through *aliases*.

    For every ``alias_key -> canonical_key`` mapping:
    - If the canonical key is already present, record a conflict if the alias
      is also present with a *different* value.
    - If only the alias is present, promote its value to the canonical key.
    - If neither is present, record the canonical key as missing.
    """
    result: Dict[str, str] = dict(env)
    applied: Dict[str, str] = {}
    conflicts: Dict[str, List[str]] = {}
    missing: List[str] = []

    for alias_key, canonical in aliases.items():
        has_canonical = canonical in result
        has_alias = alias_key in result

        if has_canonical and has_alias:
            if result[alias_key] != result[canonical]:
                conflicts.setdefault(canonical, []).append(alias_key)
            # alias key is redundant; drop it from the resolved env
            del result[alias_key]
        elif has_alias and not has_canonical:
            result[canonical] = result.pop(alias_key)
            applied[alias_key] = canonical
        elif not has_canonical and not has_alias:
            missing.append(canonical)

    return AliasResult(
        env=result,
        applied=applied,
        missing=sorted(set(missing)),
        conflicts=conflicts,
    )
