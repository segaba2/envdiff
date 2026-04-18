"""Redact sensitive values in env dictionaries before output."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SECRET_PATTERN = re.compile(
    r"(secret|password|passwd|token|api[_-]?key|private[_-]?key|auth|credential)",
    re.IGNORECASE,
)

REDACTED = "***REDACTED***"


@dataclass
class RedactResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    def summary(self) -> str:
        n = len(self.redacted_keys)
        if n == 0:
            return "No keys redacted."
        keys = ", ".join(sorted(self.redacted_keys))
        return f"{n} key(s) redacted: {keys}"


def _is_sensitive(key: str) -> bool:
    return bool(_SECRET_PATTERN.search(key))


def redact(
    env: Dict[str, str],
    extra_patterns: Optional[List[str]] = None,
    placeholder: str = REDACTED,
) -> RedactResult:
    """Return a RedactResult with sensitive values replaced by placeholder."""
    compiled_extras = [
        re.compile(p, re.IGNORECASE) for p in (extra_patterns or [])
    ]

    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        if _is_sensitive(key) or any(p.search(key) for p in compiled_extras):
            redacted[key] = placeholder
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactResult(
        original=dict(env),
        redacted=redacted,
        redacted_keys=redacted_keys,
    )


def redact_for_display(
    env: Dict[str, str],
    extra_patterns: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Convenience wrapper returning only the redacted dict."""
    return redact(env, extra_patterns).redacted
