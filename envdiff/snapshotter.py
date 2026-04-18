"""Snapshot .env files to JSON for later comparison."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Optional

from envdiff.parser import parse_env_file


class Snapshot:
    def __init__(self, path: str, env: Dict[str, str], taken_at: float):
        self.path = path
        self.env = env
        self.taken_at = taken_at

    @property
    def summary(self) -> str:
        return f"{self.path}: {len(self.env)} keys, taken at {self.taken_at:.0f}"

    def to_dict(self) -> dict:
        return {"path": self.path, "env": self.env, "taken_at": self.taken_at}

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(data["path"], data["env"], data["taken_at"])


def take(env_path: str) -> Snapshot:
    """Parse an env file and capture a timestamped snapshot."""
    env = parse_env_file(env_path)
    return Snapshot(path=env_path, env=env, taken_at=time.time())


def save(snapshot: Snapshot, dest: str) -> None:
    """Write a snapshot to a JSON file."""
    Path(dest).write_text(json.dumps(snapshot.to_dict(), indent=2))


def load(src: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    data = json.loads(Path(src).read_text())
    return Snapshot.from_dict(data)


def diff_snapshots(old: Snapshot, new: Snapshot) -> Dict[str, dict]:
    """Return keys that changed, were added, or removed between two snapshots."""
    result: Dict[str, dict] = {}
    all_keys = set(old.env) | set(new.env)
    for key in sorted(all_keys):
        old_val = old.env.get(key)
        new_val = new.env.get(key)
        if old_val == new_val:
            continue
        status = "added" if old_val is None else "removed" if new_val is None else "changed"
        result[key] = {"status": status, "old": old_val, "new": new_val}
    return result
