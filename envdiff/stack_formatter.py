"""stack_formatter.py – text and JSON rendering for StackResult."""
from __future__ import annotations

import json
from typing import Optional

from envdiff.stacker import StackResult


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_text(result: StackResult, use_color: bool = True) -> str:
    if not result.entries:
        return "No keys found in stack.\n"

    lines = []
    for entry in result.entries:
        marker = ""
        if entry.overridden_by:
            marker = _color(" [overridden]", "33", use_color)
        key_part = _color(entry.key, "36", use_color)
        src_part = _color(entry.source, "90", use_color)
        lines.append(f"{key_part}={entry.value}{marker}  ({src_part})")

    header = _color(result.summary(), "1", use_color)
    return header + "\n" + "\n".join(lines) + "\n"


def format_json(result: StackResult) -> str:
    payload = {
        "summary": result.summary(),
        "files": result.files,
        "entries": [e.to_dict() for e in result.entries],
    }
    return json.dumps(payload, indent=2)
