"""sanitizer.py – strip or replace unsafe characters from env values."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Characters considered unsafe in env values for shell / CI contexts
_UNSAFE_RE = re.compile(r"[\x00-\x1f\x7f`$!;|&<>]")
_NEWLINE_RE = re.compile(r"[\r\n]+")


@dataclass
class SanitizeResult:
    sanitized: Dict[str, str]
    changed_keys: List[str]
    original: Dict[str, str]

    def has_changes(self) -> bool:
        return bool(self.changed_keys)

    def summary(self) -> str:
        if not self.has_changes():
            return "All values are clean – no sanitization needed."
        keys = ", ".join(sorted(self.changed_keys))
        return f"{len(self.changed_keys)} value(s) sanitized: {keys}"


def _sanitize_value(
    value: str,
    replacement: str = "",
    strip_newlines: bool = True,
) -> str:
    """Return a sanitized copy of *value*."""
    if strip_newlines:
        value = _NEWLINE_RE.sub(" ", value)
    value = _UNSAFE_RE.sub(replacement, value)
    return value


def sanitize(
    env: Dict[str, str],
    replacement: str = "",
    strip_newlines: bool = True,
    only_keys: Optional[List[str]] = None,
) -> SanitizeResult:
    """Sanitize *env* values, returning a :class:`SanitizeResult`.

    Parameters
    ----------
    env:
        Mapping of key → value to sanitize.
    replacement:
        String used to replace each unsafe character (default: remove).
    strip_newlines:
        When *True* embedded newlines are replaced with a space.
    only_keys:
        If given, restrict sanitization to these keys only.
    """
    sanitized: Dict[str, str] = {}
    changed: List[str] = []

    for key, value in env.items():
        if only_keys is not None and key not in only_keys:
            sanitized[key] = value
            continue

        clean = _sanitize_value(value, replacement=replacement, strip_newlines=strip_newlines)
        sanitized[key] = clean
        if clean != value:
            changed.append(key)

    return SanitizeResult(
        sanitized=sanitized,
        changed_keys=sorted(changed),
        original=dict(env),
    )
