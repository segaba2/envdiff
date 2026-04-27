"""Archive and restore .env snapshots to/from a compressed bundle."""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ArchiveResult:
    path: str
    files: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if not self.ok:
            return f"Archive failed: {self.error}"
        names = ", ".join(self.files)
        return f"Archived {len(self.files)} file(s) to {self.path}: {names}"


@dataclass
class RestoreResult:
    destination: str
    files: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if not self.ok:
            return f"Restore failed: {self.error}"
        return f"Restored {len(self.files)} file(s) to {self.destination}"


def archive(env_files: List[str], output: str, label: str = "") -> ArchiveResult:
    """Pack one or more .env files into a zip archive with metadata."""
    out_path = Path(output)
    archived: List[str] = []
    try:
        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            meta: Dict[str, object] = {"label": label, "files": []}
            for src in env_files:
                p = Path(src)
                if not p.exists():
                    return ArchiveResult(path=output, error=f"File not found: {src}")
                zf.write(p, arcname=p.name)
                archived.append(p.name)
                meta["files"].append(p.name)  # type: ignore[union-attr]
            zf.writestr("_meta.json", json.dumps(meta, indent=2))
    except OSError as exc:
        return ArchiveResult(path=output, error=str(exc))
    return ArchiveResult(path=output, files=archived)


def restore(archive_path: str, destination: str) -> RestoreResult:
    """Unpack an archive created by :func:`archive` into *destination*."""
    dest = Path(destination)
    try:
        dest.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path, "r") as zf:
            names = [n for n in zf.namelist() if n != "_meta.json"]
            zf.extractall(dest, members=names)
    except (OSError, zipfile.BadZipFile) as exc:
        return RestoreResult(destination=destination, error=str(exc))
    return RestoreResult(destination=destination, files=names)
