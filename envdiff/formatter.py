"""Format a DiffResult as human-readable text or JSON."""
from __future__ import annotations
import json
from envdiff.comparator import DiffResult
from envdiff.sorter import sort_keys, group_by_status

_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"


def _color(text: str, code: str, *, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{code}{text}{_RESET}"


def format_text(result: DiffResult, *, use_color: bool = True, sort_by: str = "status") -> str:  # type: ignore[assignment]
    lines: list[str] = []
    groups = group_by_status(result) if sort_by == "status" else None
    keys = sort_keys(result, by=sort_by) if sort_by != "status" else [  # type: ignore[arg-type]
        k for g in ("missing_in_b", "missing_in_a", "mismatch", "ok") for k in (groups or {}).get(g, [])
    ]

    for key in keys:
        if key in result.missing_in_b:
            lines.append(_color(f"  - {key}: missing in B", _RED, use_color=use_color))
        elif key in result.missing_in_a:
            lines.append(_color(f"  - {key}: missing in A", _CYAN, use_color=use_color))
        elif key in result.mismatches:
            a_val, b_val = result.mismatches[key]
            lines.append(_color(f"  ~ {key}: {a_val!r} → {b_val!r}", _YELLOW, use_color=use_color))
        else:
            lines.append(_color(f"  ✓ {key}", _GREEN, use_color=use_color))

    if not lines:
        return _color("No differences found.", _GREEN, use_color=use_color)
    return "\n".join(lines)


def format_json(result: DiffResult) -> str:
    payload = {
        "missing_in_a": sorted(result.missing_in_a),
        "missing_in_b": sorted(result.missing_in_b),
        "mismatches": {
            k: {"a": v[0], "b": v[1]}
            for k, v in sorted(result.mismatches.items())
        },
        "common": sorted(result.common),
        "has_diff": result.has_diff(),
    }
    return json.dumps(payload, indent=2)
