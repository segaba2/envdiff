"""Type-casting inference for .env values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any


_TRUE_VALS = {"true", "yes", "1", "on"}
_FALSE_VALS = {"false", "no", "0", "off"}


def _infer_type(value: str) -> str:
    """Return a type label for *value*."""
    if value == "":
        return "empty"
    if value.lower() in _TRUE_VALS | _FALSE_VALS:
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    return "str"


def _cast(value: str) -> Any:
    """Return *value* converted to its inferred Python type."""
    t = _infer_type(value)
    if t == "empty":
        return ""
    if t == "bool":
        return value.lower() in _TRUE_VALS
    if t == "int":
        return int(value)
    if t == "float":
        return float(value)
    return value


@dataclass
class CastResult:
    types: Dict[str, str] = field(default_factory=dict)
    values: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        counts: Dict[str, int] = {}
        for t in self.types.values():
            counts[t] = counts.get(t, 0) + 1
        parts = ", ".join(f"{t}={n}" for t, n in sorted(counts.items()))
        return f"{len(self.types)} keys cast ({parts})"


def cast(env: Dict[str, str]) -> CastResult:
    """Infer and cast every value in *env*."""
    result = CastResult()
    for key, value in env.items():
        result.types[key] = _infer_type(value)
        result.values[key] = _cast(value)
    return result
