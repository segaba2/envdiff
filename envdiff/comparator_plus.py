"""Extended comparator: value-type awareness and case-insensitive comparison."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SmartDiffEntry:
    key: str
    value_a: Optional[str]
    value_b: Optional[str]
    status: str          # 'match' | 'mismatch' | 'missing_a' | 'missing_b'
    case_only: bool = False   # True when values differ only in case
    type_mismatch: bool = False  # True when inferred types differ

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value_a": self.value_a,
            "value_b": self.value_b,
            "status": self.status,
            "case_only": self.case_only,
            "type_mismatch": self.type_mismatch,
        }


@dataclass
class SmartDiffResult:
    entries: List[SmartDiffEntry] = field(default_factory=list)

    def has_diff(self) -> bool:
        return any(e.status != "match" for e in self.entries)

    def case_only_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.case_only]

    def type_mismatch_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.type_mismatch]

    def summary(self) -> str:
        total = len(self.entries)
        mismatches = sum(1 for e in self.entries if e.status == "mismatch")
        missing_a = sum(1 for e in self.entries if e.status == "missing_a")
        missing_b = sum(1 for e in self.entries if e.status == "missing_b")
        case_only = len(self.case_only_keys())
        return (
            f"{total} keys | mismatches={mismatches} "
            f"missing_a={missing_a} missing_b={missing_b} "
            f"case_only={case_only}"
        )


def _infer_type(value: Optional[str]) -> str:
    if value is None:
        return "null"
    if value.lower() in ("true", "false"):
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


def smart_compare(
    env_a: Dict[str, str],
    env_b: Dict[str, str],
) -> SmartDiffResult:
    """Compare two env dicts with case and type awareness."""
    all_keys = sorted(set(env_a) | set(env_b))
    entries: List[SmartDiffEntry] = []

    for key in all_keys:
        if key not in env_a:
            entries.append(SmartDiffEntry(key=key, value_a=None, value_b=env_b[key], status="missing_a"))
        elif key not in env_b:
            entries.append(SmartDiffEntry(key=key, value_a=env_a[key], value_b=None, status="missing_b"))
        else:
            va, vb = env_a[key], env_b[key]
            if va == vb:
                entries.append(SmartDiffEntry(key=key, value_a=va, value_b=vb, status="match"))
            else:
                case_only = va.lower() == vb.lower()
                type_mismatch = _infer_type(va) != _infer_type(vb)
                entries.append(SmartDiffEntry(
                    key=key, value_a=va, value_b=vb,
                    status="mismatch",
                    case_only=case_only,
                    type_mismatch=type_mismatch,
                ))

    return SmartDiffResult(entries=entries)
