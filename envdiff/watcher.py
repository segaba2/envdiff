"""File-system watcher: re-run diff when watched .env files change."""
import time
import os
from pathlib import Path
from typing import Callable, Optional


class EnvWatcher:
    """Poll two env file paths and invoke a callback when either changes."""

    def __init__(
        self,
        path_a: str,
        path_b: str,
        callback: Callable[[str, str], None],
        interval: float = 1.0,
    ) -> None:
        self.path_a = Path(path_a)
        self.path_b = Path(path_b)
        self.callback = callback
        self.interval = interval
        self._mtimes: dict = {}
        self._running = False

    def _mtime(self, path: Path) -> Optional[float]:
        try:
            return os.path.getmtime(path)
        except FileNotFoundError:
            return None

    def _snapshot(self) -> dict:
        return {
            str(self.path_a): self._mtime(self.path_a),
            str(self.path_b): self._mtime(self.path_b),
        }

    def _changed(self, new: dict) -> bool:
        return new != self._mtimes

    def start(self) -> None:
        """Block and poll until stop() is called."""
        self._mtimes = self._snapshot()
        self._running = True
        while self._running:
            time.sleep(self.interval)
            current = self._snapshot()
            if self._changed(current):
                self._mtimes = current
                self.callback(str(self.path_a), str(self.path_b))

    def stop(self) -> None:
        """Signal the polling loop to exit."""
        self._running = False
