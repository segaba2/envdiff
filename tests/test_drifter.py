"""Tests for envdiff.drifter."""
import json
import pytest
from pathlib import Path
from envdiff.snapshotter import Snapshot
from envdiff.drifter import detect_drift, detect_drift_from_file, DriftResult


@pytest.fixture
def env_file(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


@pytest.fixture
def base_snapshot(tmp_path, env_file):
    path = env_file("base.env", "KEY_A=hello\nKEY_B=world\nKEY_C=same\n")
    snap = Snapshot.take(path)
    snap_path = str(tmp_path / "snap.json")
    snap.save(snap_path)
    return snap, snap_path, path


def test_no_drift_identical(base_snapshot, env_file):
    snap, _, base_path = base_snapshot
    live = env_file("live.env", "KEY_A=hello\nKEY_B=world\nKEY_C=same\n")
    result = detect_drift(snap, live)
    assert not result.has_drift
    assert result.summary() == "No drift detected."


def test_added_key_detected(base_snapshot, env_file):
    snap, _, _ = base_snapshot
    live = env_file("live.env", "KEY_A=hello\nKEY_B=world\nKEY_C=same\nKEY_D=new\n")
    result = detect_drift(snap, live)
    assert result.has_drift
    assert "KEY_D" in result.added
    assert not result.removed


def test_removed_key_detected(base_snapshot, env_file):
    snap, _, _ = base_snapshot
    live = env_file("live.env", "KEY_A=hello\nKEY_C=same\n")
    result = detect_drift(snap, live)
    assert "KEY_B" in result.removed
    assert not result.added


def test_changed_value_detected(base_snapshot, env_file):
    snap, _, _ = base_snapshot
    live = env_file("live.env", "KEY_A=hello\nKEY_B=changed\nKEY_C=same\n")
    result = detect_drift(snap, live)
    assert "KEY_B" in result.changed
    assert result.changed["KEY_B"] == ("world", "changed")


def test_summary_lists_counts(base_snapshot, env_file):
    snap, _, _ = base_snapshot
    live = env_file("live.env", "KEY_A=hello\nKEY_B=changed\nKEY_D=extra\n")
    result = detect_drift(snap, live)
    summary = result.summary()
    assert "added" in summary
    assert "removed" in summary
    assert "changed" in summary


def test_detect_drift_from_file(base_snapshot, env_file):
    _, snap_path, _ = base_snapshot
    live = env_file("live.env", "KEY_A=hello\nKEY_B=world\nKEY_C=different\n")
    result = detect_drift_from_file(snap_path, live)
    assert isinstance(result, DriftResult)
    assert "KEY_C" in result.changed
