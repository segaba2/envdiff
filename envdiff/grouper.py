"""Group env keys by namespace prefix (e.g. DB_, AWS_, APP_)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class GroupResult:
    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ungrouped: Dict[str, str] = field(default_factory=dict)

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def summary(self) -> str:
        parts = [f"{name!r}: {len(keys)} key(s)" for name, keys in sorted(self.groups.items())]
        if self.ungrouped:
            parts.append(f"(ungrouped): {len(self.ungrouped)} key(s)")
        return ", ".join(parts) if parts else "no keys"


def _extract_prefix(key: str, sep: str = "_") -> str | None:
    """Return the first segment before sep if the key contains sep."""
    idx = key.find(sep)
    if idx > 0:
        return key[:idx]
    return None


def group(env: Dict[str, str], prefixes: List[str] | None = None, sep: str = "_") -> GroupResult:
    """
    Group keys by prefix.

    If *prefixes* is given only those prefixes are treated as group headers.
    Otherwise every detected prefix becomes a group.
    """
    groups: Dict[str, Dict[str, str]] = {}
    ungrouped: Dict[str, str] = {}

    allowed: Set[str] | None = set(p.upper() for p in prefixes) if prefixes else None

    for key, value in env.items():
        prefix = _extract_prefix(key, sep)
        if prefix is not None:
            prefix_up = prefix.upper()
            if allowed is None or prefix_up in allowed:
                groups.setdefault(prefix_up, {})[key] = value
                continue
        ungrouped[key] = value

    return GroupResult(groups=groups, ungrouped=ungrouped)


def flat_group(result: GroupResult) -> Dict[str, List[str]]:
    """Return a mapping of group name -> sorted list of keys."""
    out = {name: sorted(keys) for name, keys in result.groups.items()}
    if result.ungrouped:
        out["(ungrouped)"] = sorted(result.ungrouped.keys())
    return out
