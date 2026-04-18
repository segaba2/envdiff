"""Generate .env.example files from existing .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envdiff.annotator import _looks_secret


@dataclass
class TemplateResult:
    keys: List[str]
    output: Dict[str, str]

    def summary(self) -> str:
        return f"{len(self.keys)} key(s) written to template"


def _placeholder(key: str, value: str) -> str:
    """Return a safe placeholder for a key."""
    if not value:
        return ""
    if _looks_secret(key):
        return ""
    # preserve non-secret, non-empty values as hints
    return value


def build_template(env: Dict[str, str]) -> TemplateResult:
    """Build a template dict from a parsed env mapping."""
    output: Dict[str, str] = {}
    for key, value in env.items():
        output[key] = _placeholder(key, value)
    return TemplateResult(keys=list(output.keys()), output=output)


def render_template(result: TemplateResult) -> str:
    """Render a TemplateResult to a .env.example string."""
    lines: List[str] = []
    for key, value in result.output.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def write_template(env: Dict[str, str], dest: Path) -> TemplateResult:
    """Build and write a template file to *dest*."""
    result = build_template(env)
    dest.write_text(render_template(result), encoding="utf-8")
    return result
