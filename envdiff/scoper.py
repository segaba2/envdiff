"""Scope filtering: restrict env keys to a named scope defined by prefix rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    scope: str
    matched: Dict[str, str] = field(default_factory=dict)
    excluded: Dict[str, str] = field(default_factory=dict)
    strip_prefix: bool = False

    def summary(self) -> str:
        return (
            f"Scope '{self.scope}': {len(self.matched)} matched, "
            f"{len(self.excluded)} excluded"
        )

    def to_dict(self) -> dict:
        return {
            "scope": self.scope,
            "matched": self.matched,
            "excluded": self.excluded,
            "strip_prefix": self.strip_prefix,
        }


def scope(
    env: Dict[str, str],
    scope_name: str,
    prefixes: Optional[List[str]] = None,
    strip_prefix: bool = False,
) -> ScopeResult:
    """Filter *env* to keys whose names start with any of *prefixes*.

    If *prefixes* is None or empty the scope name itself (upper-cased + '_')
    is used as the sole prefix.

    When *strip_prefix* is True the leading prefix is removed from matched keys.
    """
    if not prefixes:
        prefixes = [scope_name.upper() + "_"]

    matched: Dict[str, str] = {}
    excluded: Dict[str, str] = {}

    for key, value in env.items():
        hit = next((p for p in prefixes if key.startswith(p)), None)
        if hit:
            out_key = key[len(hit):] if strip_prefix else key
            matched[out_key] = value
        else:
            excluded[key] = value

    return ScopeResult(
        scope=scope_name,
        matched=matched,
        excluded=excluded,
        strip_prefix=strip_prefix,
    )
