"""Profile .env files to produce summary statistics."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ProfileResult:
    total_keys: int = 0
    blank_values: List[str] = field(default_factory=list)
    duplicate_values: Dict[str, List[str]] = field(default_factory=dict)
    longest_key: str = ""
    longest_value_key: str = ""

    def summary(self) -> str:
        lines = [
            f"Total keys      : {self.total_keys}",
            f"Blank values    : {len(self.blank_values)}",
            f"Duplicate values: {len(self.duplicate_values)}",
            f"Longest key     : {self.longest_key}",
            f"Longest value @ : {self.longest_value_key}",
        ]
        return "\n".join(lines)


def profile(env: Dict[str, str]) -> ProfileResult:
    """Analyse a parsed env dict and return a ProfileResult."""
    result = ProfileResult(total_keys=len(env))

    # blank values
    result.blank_values = [k for k, v in env.items() if v == ""]

    # duplicate values  (value -> [keys])
    value_map: Dict[str, List[str]] = {}
    for k, v in env.items():
        if v:
            value_map.setdefault(v, []).append(k)
    result.duplicate_values = {v: ks for v, ks in value_map.items() if len(ks) > 1}

    # longest key / longest value
    if env:
        result.longest_key = max(env.keys(), key=len)
        result.longest_value_key = max(env.keys(), key=lambda k: len(env[k]))

    return result


def profile_file(path: str) -> ProfileResult:
    """Parse *path* and return its ProfileResult."""
    from envdiff.parser import parse_env_file
    return profile(parse_env_file(path))
