"""Detect deprecated or sunset keys in an env file based on a deprecation map."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DeprecationEntry:
    key: str
    reason: str
    replacement: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "reason": self.reason,
            "replacement": self.replacement,
        }


@dataclass
class DeprecateResult:
    deprecated: List[DeprecationEntry] = field(default_factory=list)
    clean: List[str] = field(default_factory=list)

    @property
    def has_deprecated(self) -> bool:
        return bool(self.deprecated)

    def summary(self) -> str:
        if not self.has_deprecated:
            return "No deprecated keys found."
        lines = [f"{len(self.deprecated)} deprecated key(s) detected:"]
        for entry in self.deprecated:
            repl = f" -> use '{entry.replacement}'" if entry.replacement else ""
            lines.append(f"  {entry.key}: {entry.reason}{repl}")
        return "\n".join(lines)


def deprecate(
    env: Dict[str, str],
    deprecation_map: Dict[str, Dict[str, str]],
) -> DeprecateResult:
    """
    Check *env* against *deprecation_map*.

    deprecation_map format::

        {
            "OLD_KEY": {"reason": "Use NEW_KEY instead", "replacement": "NEW_KEY"},
            "LEGACY_HOST": {"reason": "No longer supported"},
        }
    """
    deprecated: List[DeprecationEntry] = []
    clean: List[str] = []

    for key in env:
        if key in deprecation_map:
            info = deprecation_map[key]
            deprecated.append(
                DeprecationEntry(
                    key=key,
                    reason=info.get("reason", "Deprecated"),
                    replacement=info.get("replacement"),
                )
            )
        else:
            clean.append(key)

    return DeprecateResult(deprecated=deprecated, clean=sorted(clean))
