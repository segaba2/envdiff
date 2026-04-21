"""Split a single .env file into multiple files grouped by key prefix."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file
from envdiff.grouper import _extract_prefix


@dataclass
class SplitResult:
    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    output_files: List[Path] = field(default_factory=list)
    ungrouped: Dict[str, str] = field(default_factory=dict)

    def summary(self) -> str:
        parts = [f"{len(self.groups)} group(s) split"]
        if self.ungrouped:
            parts.append(f"{len(self.ungrouped)} ungrouped key(s)")
        if self.output_files:
            parts.append(f"{len(self.output_files)} file(s) written")
        return ", ".join(parts)


def split(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    min_group_size: int = 1,
) -> SplitResult:
    """Group env keys by prefix and return a SplitResult."""
    groups: Dict[str, Dict[str, str]] = {}
    ungrouped: Dict[str, str] = {}

    for key, value in env.items():
        prefix = _extract_prefix(key)
        if prefixes is not None and prefix not in prefixes:
            ungrouped[key] = value
            continue
        if prefix is None:
            ungrouped[key] = value
        else:
            groups.setdefault(prefix, {})[key] = value

    # Move small groups to ungrouped
    small = [p for p, keys in groups.items() if len(keys) < min_group_size]
    for p in small:
        ungrouped.update(groups.pop(p))

    return SplitResult(groups=groups, ungrouped=ungrouped)


def split_to_files(
    source: Path,
    output_dir: Path,
    prefixes: Optional[List[str]] = None,
    min_group_size: int = 1,
    include_ungrouped: bool = True,
) -> SplitResult:
    """Parse *source*, split by prefix, write one file per group."""
    env = parse_env_file(source)
    result = split(env, prefixes=prefixes, min_group_size=min_group_size)

    output_dir.mkdir(parents=True, exist_ok=True)

    for prefix, keys in result.groups.items():
        out = output_dir / f"{prefix.lower()}.env"
        lines = [f"{k}={v}\n" for k, v in sorted(keys.items())]
        out.write_text("".join(lines))
        result.output_files.append(out)

    if include_ungrouped and result.ungrouped:
        out = output_dir / "ungrouped.env"
        lines = [f"{k}={v}\n" for k, v in sorted(result.ungrouped.items())]
        out.write_text("".join(lines))
        result.output_files.append(out)

    return result
