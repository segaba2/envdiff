"""Tests for envdiff.watcher — polling-based file change detection."""
import time
import threading
from pathlib import Path

import pytest

from envdiff.watcher import EnvWatcher


@pytest.fixture()
def env_pair(tmp_path: Path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("FOO=1\n")
    b.write_text("FOO=1\n")
    return a, b


def test_callback_triggered_on_change(env_pair):
    a, b = env_pair
    calls = []

    def cb(pa, pb):
        calls.append((pa, pb))

    watcher = EnvWatcher(str(a), str(b), cb, interval=0.05)

    t = threading.Thread(target=watcher.start, daemon=True)
    t.start()
    time.sleep(0.1)

    b.write_text("FOO=2\n")  # trigger change
    time.sleep(0.2)
    watcher.stop()
    t.join(timeout=1)

    assert len(calls) >= 1
    assert calls[0] == (str(a), str(b))


def test_no_callback_without_change(env_pair):
    a, b = env_pair
    calls = []

    watcher = EnvWatcher(str(a), str(b), lambda pa, pb: calls.append(1), interval=0.05)
    t = threading.Thread(target=watcher.start, daemon=True)
    t.start()
    time.sleep(0.2)
    watcher.stop()
    t.join(timeout=1)

    assert calls == []


def test_stop_terminates_loop(env_pair):
    a, b = env_pair
    watcher = EnvWatcher(str(a), str(b), lambda *_: None, interval=0.05)
    t = threading.Thread(target=watcher.start, daemon=True)
    t.start()
    time.sleep(0.1)
    watcher.stop()
    t.join(timeout=1)
    assert not t.is_alive()
