"""interpolator.py – expand variable references inside .env values.

Supports the common ``$VAR`` and ``${VAR}`` syntax found in many shells and
frameworks.  References that cannot be resolved are left unchanged so that
callers can decide how to handle missing variables.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Matches ${VAR} or $VAR (greedy, stops at non-identifier chars)
_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolateResult:
    """Outcome of an interpolation pass over an env mapping."""

    resolved: Dict[str, str] = field(default_factory=dict)
    """Final key→value mapping after substitution."""

    unresolved_refs: Dict[str, List[str]] = field(default_factory=dict)
    """Keys whose values still contain at least one unresolvable reference.
    Maps key → list of variable names that were not found."""

    def has_unresolved(self) -> bool:
        """Return True when any value could not be fully expanded."""
        return bool(self.unresolved_refs)

    def summary(self) -> str:
        """Human-readable one-liner describing the result."""
        total = len(self.resolved)
        bad = len(self.unresolved_refs)
        if bad == 0:
            return f"All {total} keys interpolated successfully."
        return (
            f"{total - bad}/{total} keys interpolated; "
            f"{bad} key(s) have unresolved references: "
            + ", ".join(sorted(self.unresolved_refs))
        )


def _expand_value(
    value: str,
    env: Dict[str, str],
    max_depth: int = 10,
) -> tuple[str, List[str]]:
    """Recursively expand ``$VAR`` / ``${VAR}`` references in *value*.

    Parameters
    ----------
    value:
        The raw string that may contain variable references.
    env:
        The current env mapping used as the lookup table.
    max_depth:
        Guard against circular references; expansion stops after this many
        recursive passes.

    Returns
    -------
    tuple[str, list[str]]
        The expanded string and a (possibly empty) list of variable names that
        could not be resolved.
    """
    missing: List[str] = []

    for _ in range(max_depth):
        new_value, subs = _single_pass(value, env, missing)
        if not subs or new_value == value:
            break
        value = new_value

    # Collect any remaining unresolved refs in the final string
    for m in _REF_RE.finditer(value):
        name = m.group(1) or m.group(2)
        if name not in env and name not in missing:
            missing.append(name)

    return value, missing


def _single_pass(
    value: str,
    env: Dict[str, str],
    missing: List[str],
) -> tuple[str, int]:
    """Perform one substitution pass; return (new_value, substitution_count)."""
    subs = 0

    def replacer(m: re.Match) -> str:  # type: ignore[type-arg]
        nonlocal subs
        name = m.group(1) or m.group(2)
        if name in env:
            subs += 1
            return env[name]
        return m.group(0)  # leave untouched

    new_value = _REF_RE.sub(replacer, value)
    return new_value, subs


def interpolate(
    env: Dict[str, str],
    extra: Optional[Dict[str, str]] = None,
) -> InterpolateResult:
    """Expand all variable references in *env* using the mapping itself.

    Parameters
    ----------
    env:
        The parsed key→value mapping to interpolate in-place (a copy is made).
    extra:
        Optional additional variables (e.g. OS environment) consulted *after*
        the env mapping when resolving references.

    Returns
    -------
    InterpolateResult
    """
    # Build lookup table: env values take precedence over extras
    lookup: Dict[str, str] = {}
    if extra:
        lookup.update(extra)
    lookup.update(env)  # env wins

    resolved: Dict[str, str] = {}
    unresolved_refs: Dict[str, List[str]] = {}

    for key, raw_value in env.items():
        expanded, missing = _expand_value(raw_value, lookup)
        resolved[key] = expanded
        if missing:
            unresolved_refs[key] = missing

    return InterpolateResult(resolved=resolved, unresolved_refs=unresolved_refs)
