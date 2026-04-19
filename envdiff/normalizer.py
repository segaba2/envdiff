"""Normalize .env key/value pairs for consistent comparison."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NormalizeResult:
    normalized: Dict[str, str]
    changes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if not self.changes:
            return "No normalization changes."
        return f"{len(self.changes)} change(s): " + "; ".join(self.changes)


def _strip_inline_comment(value: str) -> str:
    """Remove trailing inline comments (unquoted # and beyond)."""
    if value.startswith(("'", '"')):
        return value
    idx = value.find(" #")
    if idx != -1:
        return value[:idx].rstrip()
    return value


def _unquote(value: str) -> str:
    """Strip matching surrounding quotes."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def normalize(
    env: Dict[str, str],
    uppercase_keys: bool = True,
    strip_quotes: bool = True,
    strip_inline_comments: bool = True,
) -> NormalizeResult:
    """Return a normalized copy of env with a record of changes made."""
    normalized: Dict[str, str] = {}
    changes: List[str] = []

    for key, value in env.items():
        new_key = key.upper() if uppercase_keys else key
        if new_key != key:
            changes.append(f"key '{key}' -> '{new_key}'")

        new_value = value
        if strip_inline_comments:
            stripped = _strip_inline_comment(new_value)
            if stripped != new_value:
                changes.append(f"'{new_key}' inline comment removed")
                new_value = stripped

        if strip_quotes:
            unquoted = _unquote(new_value)
            if unquoted != new_value:
                changes.append(f"'{new_key}' quotes removed")
                new_value = unquoted

        normalized[new_key] = new_value

    return NormalizeResult(normalized=normalized, changes=changes)
