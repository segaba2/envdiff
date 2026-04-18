"""Compare parsed .env dictionaries and report differences."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DiffResult:
    """Holds the comparison result between two env files."""

    missing_in_b: List[str] = field(default_factory=list)
    missing_in_a: List[str] = field(default_factory=list)
    mismatched: Dict[str, tuple] = field(default_factory=dict)

    @property
    def has_diff(self) -> bool:
        return bool(self.missing_in_b or self.missing_in_a or self.mismatched)

    def summary(self, label_a: str = "A", label_b: str = "B") -> str:
        lines = []
        for key in sorted(self.missing_in_b):
            lines.append(f"  MISSING in {label_b}: {key}")
        for key in sorted(self.missing_in_a):
            lines.append(f"  MISSING in {label_a}: {key}")
        for key in sorted(self.mismatched):
            val_a, val_b = self.mismatched[key]
            lines.append(f"  MISMATCH {key}: {label_a}={val_a!r} vs {label_b}={val_b!r}")
        return "\n".join(lines) if lines else "No differences found."


def compare_envs(
    env_a: Dict[str, Optional[str]],
    env_b: Dict[str, Optional[str]],
) -> DiffResult:
    """Compare two env dicts and return a DiffResult."""
    result = DiffResult()

    keys_a = set(env_a.keys())
    keys_b = set(env_b.keys())

    result.missing_in_b = sorted(keys_a - keys_b)
    result.missing_in_a = sorted(keys_b - keys_a)

    for key in keys_a & keys_b:
        if env_a[key] != env_b[key]:
            result.mismatched[key] = (env_a[key], env_b[key])

    return result
