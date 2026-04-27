"""Migrate keys between .env files using a rename map and value transforms."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class MigrateResult:
    migrated: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    dropped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        return bool(self.errors)

    def summary(self) -> str:
        parts = [f"migrated={len(self.migrated)}"]
        if self.skipped:
            parts.append(f"skipped={len(self.skipped)}")
        if self.dropped:
            parts.append(f"dropped={len(self.dropped)}")
        if self.errors:
            parts.append(f"errors={len(self.errors)}")
        return ", ".join(parts)


def migrate(
    env: Dict[str, str],
    rename_map: Optional[Dict[str, str]] = None,
    drop_keys: Optional[List[str]] = None,
    transforms: Optional[Dict[str, Callable[[str], str]]] = None,
    keep_unmapped: bool = True,
) -> MigrateResult:
    """Apply renames, drops, and value transforms to produce a migrated env dict."""
    rename_map = rename_map or {}
    drop_keys = set(drop_keys or [])
    transforms = transforms or {}

    result = MigrateResult()

    for old_key, value in env.items():
        if old_key in drop_keys:
            result.dropped.append(old_key)
            continue

        new_key = rename_map.get(old_key, old_key if keep_unmapped else None)
        if new_key is None:
            result.skipped.append(old_key)
            continue

        transform_fn = transforms.get(new_key) or transforms.get(old_key)
        if transform_fn is not None:
            try:
                value = transform_fn(value)
            except Exception as exc:  # noqa: BLE001
                result.errors.append(f"{old_key}: {exc}")
                continue

        result.migrated[new_key] = value

    return result
