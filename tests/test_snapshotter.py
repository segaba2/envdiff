"""Tests for envdiff.snapshotter."""
import json
import time
import pytest
from pathlib import Path

from envdiff.snapshotter import Snapshot, take, save, load, diff_snapshots


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\n")
    return str(f)


def test_take_returns_snapshot(env_file):
    snap = take(env_file)
    assert snap.env["FOO"] == "bar"
    assert snap.env["BAZ"] == "qux"
    assert snap.path == env_file
    assert snap.taken_at <= time.time()


def test_snapshot_summary(env_file):
    snap = take(env_file)
    assert "2 keys" in snap.summary


def test_save_and_load_roundtrip(env_file, tmp_path):
    snap = take(env_file)
    dest = str(tmp_path / "snap.json")
    save(snap, dest)
    loaded = load(dest)
    assert loaded.env == snap.env
    assert loaded.path == snap.path
    assert abs(loaded.taken_at - snap.taken_at) < 0.01


def test_save_writes_valid_json(env_file, tmp_path):
    snap = take(env_file)
    dest = str(tmp_path / "snap.json")
    save(snap, dest)
    data = json.loads(Path(dest).read_text())
    assert "env" in data
    assert "taken_at" in data


def test_diff_snapshots_detects_change():
    old = Snapshot("a", {"FOO": "bar", "BAZ": "qux"}, 0.0)
    new = Snapshot("a", {"FOO": "baz", "BAZ": "qux"}, 1.0)
    diff = diff_snapshots(old, new)
    assert "FOO" in diff
    assert diff["FOO"]["status"] == "changed"
    assert "BAZ" not in diff


def test_diff_snapshots_detects_added():
    old = Snapshot("a", {}, 0.0)
    new = Snapshot("a", {"NEW": "val"}, 1.0)
    diff = diff_snapshots(old, new)
    assert diff["NEW"]["status"] == "added"
    assert diff["NEW"]["old"] is None


def test_diff_snapshots_detects_removed():
    old = Snapshot("a", {"GONE": "val"}, 0.0)
    new = Snapshot("a", {}, 1.0)
    diff = diff_snapshots(old, new)
    assert diff["GONE"]["status"] == "removed"
    assert diff["GONE"]["new"] is None


def test_diff_snapshots_no_changes():
    old = Snapshot("a", {"X": "1"}, 0.0)
    new = Snapshot("a", {"X": "1"}, 1.0)
    assert diff_snapshots(old, new) == {}
