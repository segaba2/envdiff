"""High-level insight report combining profiler, linter, annotator and grouper output."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.profiler import ProfileResult
from envdiff.linter import LintResult
from envdiff.annotator import annotate
from envdiff.grouper import group, GroupResult


@dataclass
class InsightReport:
    total_keys: int = 0
    blank_keys: int = 0
    secret_keys: int = 0
    groups: GroupResult = field(default_factory=GroupResult)
    lint_issue_count: int = 0
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Total keys  : {self.total_keys}",
            f"Blank values: {self.blank_keys}",
            f"Secret keys : {self.secret_keys}",
            f"Groups      : {self.groups.summary()}",
            f"Lint issues : {self.lint_issue_count}",
        ]
        if self.warnings:
            lines.append("Warnings:")
            lines.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(lines)


def _build_warnings(report: InsightReport) -> List[str]:
    warnings: List[str] = []
    if report.blank_keys > 0:
        warnings.append(f"{report.blank_keys} key(s) have blank values.")
    if report.lint_issue_count > 0:
        warnings.append(f"{report.lint_issue_count} lint issue(s) detected.")
    ratio = report.secret_keys / report.total_keys if report.total_keys else 0
    if ratio > 0.5:
        warnings.append("More than 50% of keys look like secrets — consider a secrets manager.")
    return warnings


def analyse(
    env: Dict[str, str],
    profile: ProfileResult | None = None,
    lint: LintResult | None = None,
) -> InsightReport:
    annotations = annotate(env)
    grp = group(env)

    secret_count = len([k for k, tags in annotations.items() if "secret" in tags])
    blank_count = len([v for v in env.values() if v == ""])
    lint_count = len(lint.issues) if lint else 0

    report = InsightReport(
        total_keys=len(env),
        blank_keys=blank_count,
        secret_keys=secret_count,
        groups=grp,
        lint_issue_count=lint_count,
    )
    report.warnings = _build_warnings(report)
    return report
