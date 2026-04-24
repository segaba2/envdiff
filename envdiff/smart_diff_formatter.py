"""Formatter for SmartDiffResult — text and JSON output."""
from __future__ import annotations
import json
from typing import List
from envdiff.comparator_plus import SmartDiffResult, SmartDiffEntry

_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"


def _color(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def _entry_line(entry: SmartDiffEntry, use_color: bool) -> str:
    if entry.status == "match":
        return _color(f"  {entry.key}={entry.value_a}", _GREEN, use_color)

    if entry.status == "missing_a":
        label = "[missing in A]"
        return _color(f"  {label} {entry.key}={entry.value_b}", _RED, use_color)

    if entry.status == "missing_b":
        label = "[missing in B]"
        return _color(f"  {label} {entry.key}={entry.value_a}", _RED, use_color)

    # mismatch
    tags: List[str] = []
    if entry.case_only:
        tags.append("case-only")
    if entry.type_mismatch:
        tags.append("type-mismatch")
    tag_str = f" ({', '.join(tags)})" if tags else ""
    color = _YELLOW if entry.case_only else _RED
    return _color(
        f"  [mismatch{tag_str}] {entry.key}: {entry.value_a!r} -> {entry.value_b!r}",
        color,
        use_color,
    )


def format_text(result: SmartDiffResult, use_color: bool = False) -> str:
    if not result.has_diff():
        return _color("No differences found.", _GREEN, use_color)
    lines = ["Differences:"]
    for entry in result.entries:
        if entry.status != "match":
            lines.append(_entry_line(entry, use_color))
    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def format_json(result: SmartDiffResult) -> str:
    payload = {
        "has_diff": result.has_diff(),
        "summary": result.summary(),
        "entries": [e.to_dict() for e in result.entries],
    }
    return json.dumps(payload, indent=2)
