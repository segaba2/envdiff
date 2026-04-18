"""Validate .env files against a set of required keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class ValidationResult:
    missing: List[str] = field(default_factory=list)
    extra: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.missing and not self.extra

    def summary(self) -> str:
        parts = []
        if self.missing:
            parts.append(f"Missing keys ({len(self.missing)}): {', '.join(sorted(self.missing))}")
        if self.extra:
            parts.append(f"Extra keys ({len(self.extra)}): {', '.join(sorted(self.extra))}")
        return "; ".join(parts) if parts else "All keys valid."


def validate(
    env: Dict[str, str],
    required: Set[str],
    *,
    allow_extra: bool = True,
) -> ValidationResult:
    """Check *env* against *required* keys.

    Args:
        env: Parsed environment mapping.
        required: Set of keys that must be present.
        allow_extra: When False, keys in *env* not in *required* are flagged.

    Returns:
        A :class:`ValidationResult` describing any issues found.
    """
    env_keys: Set[str] = set(env.keys())
    missing = sorted(required - env_keys)
    extra = sorted(env_keys - required) if not allow_extra else []
    return ValidationResult(missing=missing, extra=extra)


def validate_from_template(
    env: Dict[str, str],
    template: Dict[str, str],
    *,
    allow_extra: bool = True,
) -> ValidationResult:
    """Validate *env* using a template file as the source of required keys."""
    return validate(env, set(template.keys()), allow_extra=allow_extra)
