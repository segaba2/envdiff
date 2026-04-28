"""Clone an env file to a new target, optionally overriding or masking values."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.annotator import _looks_secret


@dataclass
class CloneResult:
    source: str
    target: str
    env: Dict[str, str]
    overridden: List[str] = field(default_factory=list)
    masked: List[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = [
            f"source={self.source}",
            f"target={self.target}",
            f"keys={len(self.env)}",
        ]
        if self.overridden:
            parts.append(f"overridden={len(self.overridden)}")
        if self.masked:
            parts.append(f"masked={len(self.masked)}")
        return " ".join(parts)


def clone(
    env: Dict[str, str],
    source: str,
    target: str,
    overrides: Optional[Dict[str, str]] = None,
    mask_secrets: bool = False,
    mask_placeholder: str = "CHANGE_ME",
) -> CloneResult:
    """Return a CloneResult with a copy of *env* ready to write to *target*.

    Parameters
    ----------
    env:              Parsed key/value mapping from the source file.
    source:           Label / path of the source file.
    target:           Label / path of the destination file.
    overrides:        Key/value pairs that replace source values in the clone.
    mask_secrets:     When True, values for keys that look like secrets are
                      replaced with *mask_placeholder*.
    mask_placeholder: Replacement string used when masking secrets.
    """
    overrides = overrides or {}
    result: Dict[str, str] = {}
    overridden: List[str] = []
    masked: List[str] = []

    for key, value in env.items():
        if key in overrides:
            result[key] = overrides[key]
            overridden.append(key)
        elif mask_secrets and _looks_secret(key):
            result[key] = mask_placeholder
            masked.append(key)
        else:
            result[key] = value

    # Overrides may introduce brand-new keys not present in the source.
    for key, value in overrides.items():
        if key not in env:
            result[key] = value
            overridden.append(key)

    return CloneResult(
        source=source,
        target=target,
        env=result,
        overridden=sorted(overridden),
        masked=sorted(masked),
    )


def clone_to_file(
    env: Dict[str, str],
    source: str,
    target: Path,
    overrides: Optional[Dict[str, str]] = None,
    mask_secrets: bool = False,
    mask_placeholder: str = "CHANGE_ME",
) -> CloneResult:
    """Clone *env* and write the result to *target* as a .env file."""
    result = clone(
        env,
        source=source,
        target=str(target),
        overrides=overrides,
        mask_secrets=mask_secrets,
        mask_placeholder=mask_placeholder,
    )
    lines = [f"{k}={v}\n" for k, v in result.env.items()]
    target.write_text("".join(lines), encoding="utf-8")
    return result
