"""masker.py – selectively mask env values for safe output.

Provides pattern-based masking so callers can replace sensitive values
with a configurable placeholder before printing or logging.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_DEFAULT_PLACEHOLDER = "***"

_SENSITIVE_PATTERNS: List[str] = [
    r"(?i)secret",
    r"(?i)password",
    r"(?i)passwd",
    r"(?i)token",
    r"(?i)api[_-]?key",
    r"(?i)private[_-]?key",
    r"(?i)auth",
    r"(?i)credential",
]


@dataclass
class MaskResult:
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)

    def summary(self) -> str:
        total = len(self.original)
        count = len(self.masked_keys)
        if count == 0:
            return f"No keys masked ({total} total)."
        keys = ", ".join(sorted(self.masked_keys))
        return f"{count}/{total} key(s) masked: {keys}"


def _is_sensitive(key: str, extra_patterns: Optional[List[str]] = None) -> bool:
    patterns = _SENSITIVE_PATTERNS + (extra_patterns or [])
    return any(re.search(p, key) for p in patterns)


def mask(
    env: Dict[str, str],
    *,
    keys: Optional[List[str]] = None,
    extra_patterns: Optional[List[str]] = None,
    placeholder: str = _DEFAULT_PLACEHOLDER,
) -> MaskResult:
    """Return a MaskResult where sensitive values are replaced by *placeholder*.

    Parameters
    ----------
    env:
        Parsed key/value mapping.
    keys:
        Explicit list of keys to mask.  When provided, pattern matching is
        skipped and only these keys are masked.
    extra_patterns:
        Additional regex patterns applied alongside the built-in set.
    placeholder:
        Replacement string for masked values (default ``"***"``).
    """
    masked: Dict[str, str] = {}
    masked_keys: List[str] = []

    for k, v in env.items():
        if keys is not None:
            should_mask = k in keys
        else:
            should_mask = _is_sensitive(k, extra_patterns)

        if should_mask:
            masked[k] = placeholder
            masked_keys.append(k)
        else:
            masked[k] = v

    return MaskResult(original=dict(env), masked=masked, masked_keys=sorted(masked_keys))
