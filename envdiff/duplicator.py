"""Detect duplicate values across keys in one or more env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateResult:
    """Holds groups of keys that share the same value."""
    duplicates: Dict[str, List[str]] = field(default_factory=dict)  # value -> [keys]
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    def summary(self) -> str:
        if not self.has_duplicates:
            return "No duplicate values found."
        lines = ["Duplicate values detected:"]
        for val, keys in sorted(self.duplicates.items()):
            display = repr(val) if val else "(blank)"
            lines.append(f"  {display}: {', '.join(sorted(keys))}")
        return "\n".join(lines)


def find_duplicates(env: Dict[str, str], ignore_blank: bool = True) -> DuplicateResult:
    """Return keys that share identical values.

    Args:
        env: Parsed environment mapping.
        ignore_blank: If True, blank/empty values are not flagged as duplicates.
    """
    value_map: Dict[str, List[str]] = {}
    for key, val in env.items():
        if ignore_blank and val == "":
            continue
        value_map.setdefault(val, []).append(key)

    duplicates = {val: keys for val, keys in value_map.items() if len(keys) > 1}
    return DuplicateResult(duplicates=duplicates, env=env)
