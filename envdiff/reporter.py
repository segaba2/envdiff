"""Report generation for envdiff comparisons."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from envdiff.comparator import DiffResult
from envdiff.formatter import format_json, format_text

OutputFormat = Literal["text", "json"]


def render(result: DiffResult, fmt: OutputFormat = "text", color: bool = True) -> str:
    """Render a DiffResult to a string in the requested format."""
    if fmt == "json":
        return format_json(result)
    return format_text(result, color=color)


def write_report(
    result: DiffResult,
    output: Path,
    fmt: OutputFormat = "text",
) -> None:
    """Write a rendered report to *output* file (no ANSI color codes)."""
    content = render(result, fmt=fmt, color=False)
    output.write_text(content, encoding="utf-8")


def print_report(
    result: DiffResult,
    fmt: OutputFormat = "text",
    color: bool = True,
) -> None:
    """Print a rendered report to stdout."""
    print(render(result, fmt=fmt, color=color))


def exit_code(result: DiffResult) -> int:
    """Return 0 when there are no differences, 1 otherwise."""
    from envdiff.comparator import has_diff

    return 1 if has_diff(result) else 0
