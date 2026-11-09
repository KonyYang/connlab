from __future__ import annotations

import os
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

from scripts.pytest_artifacts import cleanup, configured_root, start_run


def test_each_run_gets_a_distinct_directory_and_keeps_other_runs(tmp_path: Path) -> None:
    root = tmp_path / "managed"
    first = start_run(root)
    second = start_run(root)
    try:
        first.scratch.mkdir()
        (first.scratch / "original.txt").write_text("keep", encoding="utf-8")
        assert first.scratch != second.scratch
        assert first.scratch.parent.parent == root
        assert (first.scratch / "original.txt").read_text(encoding="utf-8") == "keep"
    finally:
        first.finish()
        second.finish()


def test_only_completed_old_managed_runs_are_deleted(tmp_path: Path) -> None:
    root = tmp_path / "managed"
    old = start_run(root)
    old.scratch.mkdir()
    (old.scratch / "data.txt").write_text("disposable", encoding="utf-8")
    old.finish()
    active = start_run(root)
    unrelated = root / "acceptance-evidence"
    unrelated.mkdir()
    evidence = unrelated / "report.txt"
    evidence.write_text("retain", encoding="utf-8")
    future = time.time() + 8 * 86400
    try:
        preview = cleanup(root, now=future)
        assert preview.candidates == [old.scratch.parent]
        assert old.scratch.parent.exists()
        result = cleanup(root, dry_run=False, now=future)
        assert result.deleted == [old.scratch.parent]
        assert active.scratch.parent.exists()
        assert evidence.read_text(encoding="utf-8") == "retain"
    finally:
        active.finish()


def test_unmanaged_root_is_never_adopted_or_cleaned(tmp_path: Path) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    data = root / "business.txt"
    data.write_text("retain", encoding="utf-8")
    with pytest.raises(ValueError, match="unmanaged"):
        start_run(root)
    result = cleanup(root, dry_run=False, now=time.time() + 30 * 86400)
    assert not result.deleted
    assert result.warnings
    assert data.read_text(encoding="utf-8") == "retain"


def test_default_is_on_d_even_for_a_c_checkout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONNLAB_PYTEST_ARTIFACT_ROOT", raising=False)
    assert str(configured_root()).replace("\\", "/") == "D:/ConnLabTestArtifacts/pytest"


def test_recent_completion_or_new_file_preserves_the_run(tmp_path: Path) -> None:
    root = tmp_path / "managed"
    recent = start_run(root)
    recent.finish()
    assert not cleanup(root, dry_run=False, now=time.time() + 6 * 86400).deleted
    recent.scratch.mkdir()
    file = recent.scratch / "later.txt"
    file.write_text("new", encoding="utf-8")
    now = time.time() + 8 * 86400
    os.utime(file, (now, now))
    assert not cleanup(root, dry_run=False, now=now).deleted


def test_dead_process_without_completion_is_preserved(tmp_path: Path) -> None:
    root = tmp_path / "managed"
    script = "from scripts.pytest_artifacts import start_run; import os,sys; from pathlib import Path; start_run(Path(sys.argv[1])); os._exit(0)"
    subprocess.run([sys.executable, "-c", script, str(root)], check=True, timeout=15)
    result = cleanup(root, dry_run=False, now=time.time() + 30 * 86400)
    assert not result.deleted
    assert len(list(root.glob("run-*"))) == 1
    assert result.warnings


@pytest.mark.parametrize("target", [".run.json", ".finished.json"])
def test_wrong_owner_and_invalid_completion_preserve_files(tmp_path: Path, target: str) -> None:
    root = tmp_path / "managed"
    run = start_run(root)
    run.finish()
    marker = run.scratch.parent / target
    document = json.loads(marker.read_text(encoding="utf-8"))
    document["root_id"] = "another-root"
    marker.write_text(json.dumps(document), encoding="utf-8")
    result = cleanup(root, dry_run=False, now=time.time() + 30 * 86400)
    assert not result.deleted
    assert marker.exists()
    assert result.warnings


def test_a_live_lease_protects_even_a_completed_run(tmp_path: Path) -> None:
    root = tmp_path / "managed"
    run = start_run(root)
    run.finish()
    script = """
import os, sys
f = open(sys.argv[1], 'r+b')
if os.name == 'nt':
    import msvcrt
    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
else:
    import fcntl
    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
print('ready', flush=True)
sys.stdin.readline()
f.close()
"""
    process = subprocess.Popen([sys.executable, "-u", "-c", script, str(run.scratch.parent / ".lease")],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    try:
        assert process.stdout.readline().strip() == "ready"
        locked = cleanup(root, dry_run=False, now=time.time() + 30 * 86400)
        assert not locked.deleted
        assert locked.warnings
    finally:
        process.communicate("done\n", timeout=15)
    assert cleanup(root, dry_run=False, now=time.time() + 30 * 86400).deleted == [run.scratch.parent]


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan")])
def test_invalid_retention_cannot_delete(tmp_path: Path, value: float) -> None:
    with pytest.raises(ValueError, match="Retention"):
        cleanup(tmp_path / "managed", dry_run=False, retention_days=value)


@pytest.mark.parametrize("root", [Path("relative"), Path(Path.cwd().anchor)])
def test_unsafe_root_is_rejected(root: Path) -> None:
    with pytest.raises(ValueError, match="absolute local"):
        start_run(root)
    assert cleanup(root, dry_run=False).warnings


def test_deletion_failure_is_diagnostic_and_other_runs_continue(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import shutil

    root = tmp_path / "managed"
    first, second = start_run(root), start_run(root)
    first.scratch.mkdir()
    second.scratch.mkdir()
    first.finish()
    second.finish()
    real_delete = shutil.rmtree

    def inaccessible(path):
        if path == first.scratch:
            raise PermissionError("isolated locked-file simulation")
        real_delete(path)

    monkeypatch.setattr(shutil, "rmtree", inaccessible)
    result = cleanup(root, dry_run=False, now=time.time() + 30 * 86400)
    assert result.deleted == [second.scratch.parent]
    assert any("isolated locked-file simulation" in warning for warning in result.warnings)
    assert first.scratch.parent.exists()


def test_windows_junctions_are_not_followed_or_deleted(tmp_path: Path) -> None:
    if os.name != "nt":
        pytest.skip("Windows junction acceptance")
    root = tmp_path / "managed"
    run = start_run(root)
    run.scratch.mkdir()
    outside = tmp_path / "business"
    outside.mkdir()
    file = outside / "keep.txt"
    file.write_text("do not delete", encoding="utf-8")
    junction = run.scratch / "linked"
    try:
        subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(outside)], check=True, capture_output=True)
        run.finish()
        result = cleanup(root, dry_run=False, now=time.time() + 30 * 86400)
        assert not result.deleted
        assert any("reparse" in warning for warning in result.warnings)
        assert file.read_text(encoding="utf-8") == "do not delete"
        with pytest.raises(ValueError, match="reparse"):
            start_run(junction / "nested")
    finally:
        # Remove only the known junction itself, never its external target.
        if junction.exists():
            junction.rmdir()
        run.finish()


def test_internal_pytest_current_links_do_not_prevent_retention(tmp_path: Path) -> None:
    root = tmp_path / "managed"
    run = start_run(root)
    run.scratch.mkdir()
    target = run.scratch / "test0"
    target.mkdir()
    link = run.scratch / "testcurrent"
    try:
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError as error:
            if os.name == "nt" and error.winerror in (5, 1314):
                pytest.skip(f"Host does not grant symlink creation: {error}")
            raise
        run.finish()
        result = cleanup(root, dry_run=False, now=time.time() + 30 * 86400)
        assert result.deleted == [run.scratch.parent]
    finally:
        run.finish()


def test_locked_payload_keeps_ownership_markers_so_next_cleanup_can_retry(tmp_path: Path) -> None:
    if os.name != "nt":
        pytest.skip("Windows open-file deletion semantics")
    root = tmp_path / "managed"
    run = start_run(root)
    run.scratch.mkdir()
    payload = run.scratch / "held.txt"
    payload.write_text("locked", encoding="utf-8")
    run.finish()
    with payload.open("rb"):
        result = cleanup(root, dry_run=False, now=time.time() + 30 * 86400)
        assert not result.deleted
        assert result.warnings
        assert (run.scratch.parent / ".run.json").exists()
        assert (run.scratch.parent / ".finished.json").exists()
        assert (run.scratch.parent / ".lease").exists()
    assert cleanup(root, dry_run=False, now=time.time() + 30 * 86400).deleted == [run.scratch.parent]


def test_changed_run_identity_cannot_be_marked_completed(tmp_path: Path) -> None:
    root = tmp_path / "managed"
    run = start_run(root)
    marker = run.scratch.parent / ".run.json"
    value = json.loads(marker.read_text(encoding="utf-8"))
    value["run_id"] = "another-run"
    marker.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="identity"):
        run.finish()
    assert not (run.scratch.parent / ".finished.json").exists()


def test_concurrent_first_sessions_wait_for_atomic_root_publication(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    if os.name != "nt":
        pytest.skip("Windows rename/lease initialization boundary")
    from concurrent.futures import ThreadPoolExecutor, TimeoutError
    import threading

    root = tmp_path / "managed"
    publishing, release = threading.Event(), threading.Event()
    real_rename = os.rename

    def delayed_publish(source, destination):
        if Path(destination).name == ".connlab-pytest-root.json":
            publishing.set()
            assert release.wait(5)
        return real_rename(source, destination)

    monkeypatch.setattr(os, "rename", delayed_publish)
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(start_run, root)
        try:
            assert publishing.wait(5)
            second = executor.submit(start_run, root)
            with pytest.raises(TimeoutError):
                second.result(timeout=.1)
        finally:
            release.set()
        runs = [first.result(timeout=5), second.result(timeout=5)]
        try:
            assert runs[0].scratch != runs[1].scratch
        finally:
            for run in runs:
                run.finish()
