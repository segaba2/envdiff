"""Detect drift between a saved snapshot and a live .env file."""
from dataclasses import dataclass, field
from typing import Dict, List
from envdiff.snapshotter import Snapshot
from envdiff.parser import parse_env_file


@dataclass
class DriftResult:
    snapshot_file: str
    live_file: str
    added: List[str] = field(default_factory=list)      # in live, not in snapshot
    removed: List[str] = field(default_factory=list)    # in snapshot, not in live
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    @property
    def has_drift(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        if not self.has_drift:
            return "No drift detected."
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        return "Drift detected: " + ", ".join(parts) + "."


def detect_drift(snapshot: Snapshot, live_path: str) -> DriftResult:
    """Compare a Snapshot against the current state of a live .env file."""
    live_env = parse_env_file(live_path)
    snap_env = snapshot.data

    snap_keys = set(snap_env)
    live_keys = set(live_env)

    added = sorted(live_keys - snap_keys)
    removed = sorted(snap_keys - live_keys)
    changed = {
        k: (snap_env[k], live_env[k])
        for k in snap_keys & live_keys
        if snap_env[k] != live_env[k]
    }

    return DriftResult(
        snapshot_file=snapshot.source_file,
        live_file=live_path,
        added=added,
        removed=removed,
        changed=changed,
    )


def detect_drift_from_file(snapshot_path: str, live_path: str) -> DriftResult:
    """Load a snapshot from disk and compare against a live .env file."""
    snapshot = Snapshot.load(snapshot_path)
    return detect_drift(snapshot, live_path)
