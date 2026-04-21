"""Apply key/value transformations to a parsed env dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformResult:
    transformed: Dict[str, str]
    applied: List[str] = field(default_factory=list)   # keys that changed
    skipped: List[str] = field(default_factory=list)   # keys not matched

    def summary(self) -> str:
        return (
            f"{len(self.applied)} key(s) transformed, "
            f"{len(self.skipped)} skipped"
        )


TransformFn = Callable[[str, str], Optional[str]]


def _upper_keys(env: Dict[str, str]) -> Dict[str, str]:
    """Return a copy with all keys uppercased."""
    return {k.upper(): v for k, v in env.items()}


def _strip_values(env: Dict[str, str]) -> Dict[str, str]:
    """Return a copy with all values stripped of surrounding whitespace."""
    return {k: v.strip() for k, v in env.items()}


def transform(
    env: Dict[str, str],
    *,
    upper_keys: bool = False,
    strip_values: bool = False,
    rename: Optional[Dict[str, str]] = None,
    value_fn: Optional[TransformFn] = None,
) -> TransformResult:
    """Apply one or more transformations to *env* and return a TransformResult."""
    result = dict(env)
    applied: List[str] = []
    skipped: List[str] = list(env.keys())

    if upper_keys:
        new: Dict[str, str] = {}
        for k, v in result.items():
            uk = k.upper()
            new[uk] = v
            if uk != k and k in skipped:
                skipped.remove(k)
                applied.append(uk)
        result = new

    if strip_values:
        for k, v in result.items():
            stripped = v.strip()
            if stripped != v:
                result[k] = stripped
                if k not in applied:
                    applied.append(k)
                if k in skipped:
                    skipped.remove(k)

    if rename:
        for old, new_name in rename.items():
            if old in result:
                result[new_name] = result.pop(old)
                applied.append(new_name)
                if old in skipped:
                    skipped.remove(old)

    if value_fn:
        for k in list(result.keys()):
            out = value_fn(k, result[k])
            if out is not None and out != result[k]:
                result[k] = out
                if k not in applied:
                    applied.append(k)
                if k in skipped:
                    skipped.remove(k)

    return TransformResult(transformed=result, applied=applied, skipped=skipped)
