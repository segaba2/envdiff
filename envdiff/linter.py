"""Lint .env files for common style and correctness issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import re


@dataclass
class LintIssue:
    line: int
    key: str | None
    code: str
    message: str


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok:
            return "No lint issues found."
        lines = [f"{len(self.issues)} lint issue(s) found:"]
        for iss in self.issues:
            loc = f"line {iss.line}" + (f" [{iss.key}]" if iss.key else "")
            lines.append(f"  {loc}  {iss.code}: {iss.message}")
        return "\n".join(lines)


_UPPER_KEY_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_TRAILING_SPACE_RE = re.compile(r'[ \t]+$')


def lint_lines(lines: List[str]) -> LintResult:
    result = LintResult()
    seen_keys: dict[str, int] = {}

    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.rstrip('\n')

        if _TRAILING_SPACE_RE.search(stripped):
            result.issues.append(LintIssue(lineno, None, 'W001', 'Trailing whitespace'))

        if not stripped or stripped.lstrip().startswith('#'):
            continue

        if '=' not in stripped:
            result.issues.append(LintIssue(lineno, None, 'E001', 'Missing "=" separator'))
            continue

        key, _, value = stripped.partition('=')
        key = key.strip()

        if not _UPPER_KEY_RE.match(key):
            result.issues.append(LintIssue(lineno, key, 'W002', 'Key should be UPPER_SNAKE_CASE'))

        if key in seen_keys:
            result.issues.append(LintIssue(lineno, key, 'E002',
                f'Duplicate key (first seen on line {seen_keys[key]})'))
        else:
            seen_keys[key] = lineno

        if value != value.strip():
            result.issues.append(LintIssue(lineno, key, 'W003', 'Value has surrounding whitespace'))

    return result


def lint_file(path: str) -> LintResult:
    with open(path, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()
    return lint_lines(lines)
