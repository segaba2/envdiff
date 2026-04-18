"""Score an env file's overall health based on profiler, annotator, and linter results."""
from dataclasses import dataclass, field
from typing import List

from envdiff.profiler import ProfileResult
from envdiff.linter import LintResult
from envdiff.annotator import annotate


@dataclass
class ScoreReport:
    total: int
    penalties: List[str] = field(default_factory=list)
    score: int = 100

    def summary(self) -> str:
        grade = _grade(self.score)
        lines = [f"Health score: {self.score}/100 ({grade})"]
        for p in self.penalties:
            lines.append(f"  - {p}")
        return "\n".join(lines)


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def score(profile: ProfileResult, lint: LintResult, env: dict) -> ScoreReport:
    penalties: List[str] = []
    deductions = 0

    if profile.total == 0:
        return ScoreReport(total=0, penalties=["Empty file"], score=0)

    blank_ratio = profile.blank_values / profile.total
    if blank_ratio > 0.3:
        deductions += 20
        penalties.append(f"{profile.blank_values} blank values ({blank_ratio:.0%} of keys)")
    elif blank_ratio > 0.1:
        deductions += 10
        penalties.append(f"{profile.blank_values} blank values")

    if profile.duplicate_values:
        deductions += 10
        penalties.append(f"{len(profile.duplicate_values)} duplicate value group(s)")

    if not lint.ok:
        issue_count = len(lint.issues)
        deduction = min(30, issue_count * 5)
        deductions += deduction
        penalties.append(f"{issue_count} lint issue(s) (-{deduction} pts)")

    annotations = annotate(env)
    secret_blank = [k for k, tags in annotations.items() if "secret" in tags and env.get(k) == ""]
    if secret_blank:
        deductions += 15
        penalties.append(f"{len(secret_blank)} blank secret key(s)")

    final = max(0, 100 - deductions)
    return ScoreReport(total=profile.total, penalties=penalties, score=final)
