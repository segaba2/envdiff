"""High-level insights combining profiler and annotator output."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.profiler import profile, ProfileResult
from envdiff.annotator import annotate


@dataclass
class InsightReport:
    profile: ProfileResult
    annotations: Dict[str, List[str]] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = [self.profile.summary()]
        if self.warnings:
            parts.append("Warnings:")
            parts.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(parts)


def _build_warnings(
    prof: ProfileResult,
    annotations: Dict[str, List[str]],
) -> List[str]:
    warnings: List[str] = []
    if prof.blank_values:
        warnings.append(f"{len(prof.blank_values)} key(s) have blank values: {', '.join(prof.blank_values)}")
    if prof.duplicate_values:
        for val, keys in prof.duplicate_values.items():
            warnings.append(f"Duplicate value shared by: {', '.join(keys)}")
    exposed = [k for k, tags in annotations.items() if "secret" in tags and "blank" not in tags]
    # secrets with numeric-only values are suspicious
    numeric_secrets = [
        k for k in exposed if "numeric" in annotations.get(k, [])
    ]
    if numeric_secrets:
        warnings.append(f"Numeric-only secret value(s): {', '.join(numeric_secrets)}")
    return warnings


def analyse(env: Dict[str, str]) -> InsightReport:
    """Run profiler + annotator and produce an InsightReport."""
    prof = profile(env)
    ann = annotate(env)
    warnings = _build_warnings(prof, ann)
    return InsightReport(profile=prof, annotations=ann, warnings=warnings)
