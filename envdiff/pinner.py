"""Pin current env key-value pairs to a lockfile for drift detection."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class PinResult:
    pinned: Dict[str, str]
    source: str
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        if not self.has_changes():
            return f"[{self.source}] pin unchanged ({len(self.pinned)} keys)"
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.changed:
            parts.append(f"~{len(self.changed)} changed")
        return f"[{self.source}] pin updated: {', '.join(parts)}"


def pin(env_path: str, lockfile: str) -> PinResult:
    """Read env_path and write a JSON lockfile. Return what changed."""
    source = Path(env_path).name
    current = parse_env_file(env_path)

    lock_path = Path(lockfile)
    previous: Dict[str, str] = {}
    if lock_path.exists():
        try:
            previous = json.loads(lock_path.read_text(encoding="utf-8")).get("pins", {})
        except (json.JSONDecodeError, OSError):
            previous = {}

    added = [k for k in current if k not in previous]
    removed = [k for k in previous if k not in current]
    changed = [
        k for k in current
        if k in previous and current[k] != previous[k]
    ]

    lock_path.write_text(
        json.dumps({"source": env_path, "pins": current}, indent=2),
        encoding="utf-8",
    )

    return PinResult(
        pinned=current,
        source=source,
        added=added,
        removed=removed,
        changed=changed,
    )


def load_pins(lockfile: str) -> Dict[str, str]:
    """Load pinned key-value pairs from a lockfile."""
    path = Path(lockfile)
    if not path.exists():
        raise FileNotFoundError(f"Lockfile not found: {lockfile}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("pins", {})
