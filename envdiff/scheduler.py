"""scheduler.py — schedule periodic env diff checks and emit alerts on change.

Provides a simple polling scheduler that runs a diff pipeline at a fixed
interval and invokes a callback whenever the result changes.  Useful for
long-running processes (e.g. a sidecar container) that need to watch
multiple env files and react to drift without the filesystem-event overhead
of the lower-level EnvWatcher.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence

from envdiff.differ import diff_files
from envdiff.comparator import DiffResult


@dataclass
class ScheduleEntry:
    """A single scheduled comparison job."""

    file_a: str
    file_b: str
    interval: float  # seconds between checks
    label: str = ""
    exclude: Sequence[str] = field(default_factory=list)
    prefix: Optional[str] = None

    # runtime state (not part of public API)
    _last_result: Optional[DiffResult] = field(default=None, init=False, repr=False)
    _next_run: float = field(default=0.0, init=False, repr=False)


AlertCallback = Callable[[ScheduleEntry, DiffResult], None]


class EnvScheduler:
    """Poll one or more env-file pairs at configurable intervals.

    Usage::

        def on_change(entry, result):
            print(f"{entry.label}: diff detected — {result.summary()}")

        scheduler = EnvScheduler(on_change=on_change)
        scheduler.add(".env.staging", ".env.prod", interval=60, label="staging-vs-prod")
        scheduler.start()
        # ... later ...
        scheduler.stop()
    """

    def __init__(
        self,
        on_change: Optional[AlertCallback] = None,
        on_error: Optional[Callable[[ScheduleEntry, Exception], None]] = None,
    ) -> None:
        self._entries: List[ScheduleEntry] = []
        self._on_change = on_change
        self._on_error = on_error
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(
        self,
        file_a: str,
        file_b: str,
        interval: float = 30.0,
        label: str = "",
        exclude: Sequence[str] = (),
        prefix: Optional[str] = None,
    ) -> "EnvScheduler":
        """Register a new comparison job.  Returns *self* for chaining."""
        entry = ScheduleEntry(
            file_a=file_a,
            file_b=file_b,
            interval=interval,
            label=label or f"{file_a} vs {file_b}",
            exclude=list(exclude),
            prefix=prefix,
        )
        self._entries.append(entry)
        return self

    def start(self, daemon: bool = True) -> None:
        """Start the background polling thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=daemon)
        self._thread.start()

    def stop(self, timeout: float = 5.0) -> None:
        """Signal the polling thread to stop and wait for it to finish."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)

    def run_once(self) -> None:
        """Execute a single pass over all due entries (blocking, no thread)."""
        now = time.monotonic()
        for entry in self._entries:
            if now >= entry._next_run:
                self._check(entry)
                entry._next_run = now + entry.interval

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _loop(self) -> None:
        """Main loop executed in the background thread."""
        while not self._stop_event.is_set():
            self.run_once()
            self._stop_event.wait(timeout=1.0)

    def _check(self, entry: ScheduleEntry) -> None:
        """Run a diff for *entry* and fire the callback on change or first run."""
        try:
            result = diff_files(
                entry.file_a,
                entry.file_b,
                exclude=entry.exclude,
                prefix=entry.prefix,
            )
        except Exception as exc:  # noqa: BLE001
            if self._on_error:
                self._on_error(entry, exc)
            return

        changed = entry._last_result is None or _results_differ(
            entry._last_result, result
        )
        entry._last_result = result

        if changed and self._on_change:
            self._on_change(entry, result)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _results_differ(a: DiffResult, b: DiffResult) -> bool:
    """Return True when two DiffResult objects represent different states."""
    return (
        set(a.missing_in_b) != set(b.missing_in_b)
        or set(a.missing_in_a) != set(b.missing_in_a)
        or a.mismatches != b.mismatches
    )
