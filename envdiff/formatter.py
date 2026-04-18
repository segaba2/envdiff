"""Output formatters for envdiff comparison results."""

from typing import Dict
from envdiff.comparator import DiffResult

ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{code}{text}{ANSI_RESET}"


def format_text(result: DiffResult, env_a: str, env_b: str, use_color: bool = True) -> str:
    """Format a DiffResult as a human-readable text report."""
    lines = []

    header = f"envdiff: {env_a} vs {env_b}"
    lines.append(_color(header, ANSI_BOLD, use_color))
    lines.append("-" * len(header))

    if not result.missing_in_a and not result.missing_in_b and not result.mismatched:
        lines.append(_color("No differences found.", ANSI_GREEN, use_color))
        return "\n".join(lines)

    for key in sorted(result.missing_in_a):
        lines.append(_color(f"  + {key}  (missing in {env_a})", ANSI_GREEN, use_color))

    for key in sorted(result.missing_in_b):
        lines.append(_color(f"  - {key}  (missing in {env_b})", ANSI_RED, use_color))

    for key in sorted(result.mismatched):
        val_a, val_b = result.mismatched[key]
        lines.append(_color(f"  ~ {key}", ANSI_YELLOW, use_color))
        lines.append(f"      {env_a}: {val_a}")
        lines.append(f"      {env_b}: {val_b}")

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def format_json(result: DiffResult, env_a: str, env_b: str) -> str:
    """Format a DiffResult as a JSON string."""
    import json

    data: Dict = {
        "has_diff": result.has_diff(),
        "missing_in_a": sorted(result.missing_in_a),
        "missing_in_b": sorted(result.missing_in_b),
        "mismatched": {
            k: {env_a: v[0], env_b: v[1]}
            for k, v in sorted(result.mismatched.items())
        },
    }
    return json.dumps(data, indent=2)
