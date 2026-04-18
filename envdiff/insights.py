"""High-level insight report combining profiler, linter, annotator, and scorer."""
from dataclasses import dataclass, field
from typing import List, Dict, Any

from envdiff.profiler import profile as run_profile
from envdiff.linter import lint_file
from envdiff.annotator import annotate, secret_keys, blank_keys
from envdiff.scorer import score as run_score, ScoreReport


@dataclass
class InsightReport:
    path: str
    score: ScoreReport
    warnings: List[str] = field(default_factory=list)
    tags: Dict[str, List[str]] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [f"[{self.path}]", self.score.summary()]
        if self.warnings:
            lines.append("Warnings:")
            for w in self.warnings:
                lines.append(f"  ! {w}")
        return "\n".join(lines)


def _build_warnings(env: dict, tags: Dict[str, List[str]]) -> List[str]:
    warnings: List[str] = []
    secrets = secret_keys(tags)
    blanks = blank_keys(tags)
    exposed = [k for k in secrets if env.get(k, "") not in ("", "REDACTED")]
    if exposed:
        warnings.append(f"{len(exposed)} secret key(s) have plaintext values")
    if blanks:
        warnings.append(f"{len(blanks)} key(s) have blank values: {', '.join(sorted(blanks))}")
    url_keys = [k for k, t in tags.items() if "url" in t]
    if url_keys:
        warnings.append(f"{len(url_keys)} URL value(s) detected — verify accessibility")
    return warnings


def analyse(path: str) -> InsightReport:
    from envdiff.parser import parse_env_file
    env = parse_env_file(path)
    profile = run_profile(env)
    lint = lint_file(path)
    tags = annotate(env)
    sc = run_score(profile, lint, env)
    warnings = _build_warnings(env, tags)
    return InsightReport(path=path, score=sc, warnings=warnings, tags=tags)
