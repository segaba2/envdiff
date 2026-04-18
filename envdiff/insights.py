"""High-level insight analysis combining profiler, annotator, and redactor."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.profiler import profile
from envdiff.annotator import annotate
from envdiff.redactor import redact


@dataclass
class InsightReport:
    total_keys: int
    blank_count: int
    duplicate_value_count: int
    secret_count: int
    redacted_keys: List[str]
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Total keys   : {self.total_keys}",
            f"Blank values : {self.blank_count}",
            f"Duplicates   : {self.duplicate_value_count}",
            f"Secrets      : {self.secret_count}",
        ]
        if self.warnings:
            lines.append("Warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")
        return "\n".join(lines)


def _build_warnings(
    blank_count: int,
    duplicate_value_count: int,
    secret_count: int,
) -> List[str]:
    warnings: List[str] = []
    if blank_count > 0:
        warnings.append(f"{blank_count} key(s) have blank values.")
    if duplicate_value_count > 0:
        warnings.append(f"{duplicate_value_count} duplicate value(s) detected.")
    if secret_count == 0:
        warnings.append("No secret keys found — verify sensitive data is not stored as plain keys.")
    return warnings


def analyse(env: Dict[str, str]) -> InsightReport:
    """Run profiler, annotator, and redactor and return a combined InsightReport."""
    prof = profile(env)
    tags = annotate(env)
    red = redact(env)

    secret_count = sum(1 for t in tags.values() if "secret" in t)

    warnings = _build_warnings(
        blank_count=prof.blank_values,
        duplicate_value_count=len(prof.duplicate_values),
        secret_count=secret_count,
    )

    return InsightReport(
        total_keys=prof.total_keys,
        blank_count=prof.blank_values,
        duplicate_value_count=len(prof.duplicate_values),
        secret_count=secret_count,
        redacted_keys=red.redacted_keys,
        warnings=warnings,
    )
