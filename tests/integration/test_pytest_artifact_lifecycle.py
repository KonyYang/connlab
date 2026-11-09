from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from scripts.pytest_artifacts import start_run


REPOSITORY = Path(__file__).resolve().parents[2]


def fixture_checkout(checkout: Path, source: str | None = None) -> Path:
    checkout.mkdir()
    shutil.copyfile(REPOSITORY / "conftest.py", checkout / "conftest.py")
    (checkout / "scripts").mkdir()
    shutil.copyfile(REPOSITORY / "scripts/pytest_artifacts.py", checkout / "scripts/pytest_artifacts.py")
    (checkout / "test_fixture.py").write_text(
        source or "from pathlib import Path\n"
        "def test_location(tmp_path):\n"
        "    Path('location.txt').write_text(str(tmp_path), encoding='utf-8')\n",
        encoding="utf-8",
    )
    return checkout


def run_pytest_fixture(tmp_path: Path, *, explicit: bool = False) -> tuple[subprocess.CompletedProcess, Path, Path]:
    checkout = fixture_checkout(tmp_path / "checkout")
    root = tmp_path / "managed"
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
    if explicit:
        command.extend(["--basetemp", str(tmp_path / "explicit")])
    environment = {**os.environ, "CONNLAB_PYTEST_ARTIFACT_ROOT": str(root), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    result = subprocess.run(command, cwd=checkout, env=environment, capture_output=True, text=True, timeout=30)
    return result, checkout, root


def test_direct_pytest_manages_a_unique_finished_run(tmp_path: Path) -> None:
    result, checkout, root = run_pytest_fixture(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    actual = Path((checkout / "location.txt").read_text(encoding="utf-8"))
    assert actual.is_relative_to(root)
    runs = list(root.glob("run-*"))
    assert len(runs) == 1
    assert json.loads((runs[0] / ".finished.json").read_text(encoding="utf-8"))["ended_at"] > 0


def test_explicit_basetemp_does_not_initialize_or_sweep_managed_storage(tmp_path: Path) -> None:
    result, checkout, root = run_pytest_fixture(tmp_path, explicit=True)
    assert result.returncode == 0, result.stdout + result.stderr
    actual = Path((checkout / "location.txt").read_text(encoding="utf-8"))
    assert actual.is_relative_to(tmp_path / "explicit")
    assert not root.exists()


def age_finished_run(root: Path) -> Path:
    run = start_run(root)
    run.scratch.mkdir()
    (run.scratch / "payload.txt").write_text("disposable", encoding="utf-8")
    run.finish()
    finished = run.scratch.parent / ".finished.json"
    value = json.loads(finished.read_text(encoding="utf-8"))
    old = time.time() - 9 * 86400
    value["ended_at"] = old
    finished.write_text(json.dumps(value), encoding="utf-8")
    for path in sorted(run.scratch.parent.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        assert not path.is_symlink()
        os.utime(path, (old, old))
    os.utime(run.scratch.parent, (old, old))
    return run.scratch.parent


def test_automatic_retention_removes_only_owned_old_payloads(tmp_path: Path) -> None:
    root = tmp_path / "managed"
    old = age_finished_run(root)
    evidence = root / "retained-acceptance.txt"
    evidence.write_text("keep", encoding="utf-8")
    checkout = fixture_checkout(tmp_path / "checkout")
    environment = {**os.environ, "CONNLAB_PYTEST_ARTIFACT_ROOT": str(root), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                            cwd=checkout, env=environment, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not old.exists()
    assert evidence.read_text(encoding="utf-8") == "keep"


def test_cleanup_diagnostics_do_not_fail_the_test_session(tmp_path: Path) -> None:
    root = tmp_path / "managed"
    old = age_finished_run(root)
    (old / ".finished.json").write_text("not JSON", encoding="utf-8")
    checkout = fixture_checkout(tmp_path / "checkout")
    environment = {**os.environ, "CONNLAB_PYTEST_ARTIFACT_ROOT": str(root), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                            cwd=checkout, env=environment, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Preserved" in result.stderr
    assert old.exists()


def test_two_real_pytest_processes_do_not_clear_each_others_scratch(tmp_path: Path) -> None:
    root = tmp_path / "managed"
    first = fixture_checkout(tmp_path / "first", """
from pathlib import Path
import time
def test_hold(tmp_path):
    payload = tmp_path / 'keep.txt'
    payload.write_text('keep', encoding='utf-8')
    Path('location.txt').write_text(str(tmp_path), encoding='utf-8')
    deadline = time.monotonic() + 15
    while not Path('release').exists():
        assert time.monotonic() < deadline
        time.sleep(.02)
    assert payload.read_text(encoding='utf-8') == 'keep'
""")
    second = fixture_checkout(tmp_path / "second")
    environment = {**os.environ, "CONNLAB_PYTEST_ARTIFACT_ROOT": str(root), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
    process = subprocess.Popen(command, cwd=first, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 10
        while not (first / "location.txt").exists():
            assert process.poll() is None
            assert time.monotonic() < deadline
            time.sleep(.02)
        one = Path((first / "location.txt").read_text(encoding="utf-8"))
        result = subprocess.run(command, cwd=second, env=environment, capture_output=True, text=True, timeout=15)
        assert result.returncode == 0, result.stdout + result.stderr
        two = Path((second / "location.txt").read_text(encoding="utf-8"))
        assert one != two
        assert one.is_relative_to(root) and two.is_relative_to(root)
        assert (one / "keep.txt").read_text(encoding="utf-8") == "keep"
    finally:
        (first / "release").touch()
        stdout, stderr = process.communicate(timeout=20)
    assert process.returncode == 0, stdout + stderr
    assert len(list(root.glob("run-*/.finished.json"))) == 2


def test_cleaner_cli_defaults_to_preview_and_applies_only_with_delete(tmp_path: Path) -> None:
    root = tmp_path / "managed"
    old = age_finished_run(root)
    legacy = tmp_path / "legacy"
    legacy.mkdir()
    keep = legacy / "evidence.txt"
    keep.write_text("keep", encoding="utf-8")
    command = [sys.executable, str(REPOSITORY / "scripts/clean_tmp.py"), "--root", str(root)]
    preview = subprocess.run(command, capture_output=True, text=True, timeout=15)
    assert preview.returncode == 0
    assert "1 eligible, 0 deleted" in preview.stdout
    assert old.exists()
    applied = subprocess.run([*command, "--delete"], capture_output=True, text=True, timeout=15)
    assert applied.returncode == 0
    assert "1 eligible, 1 deleted" in applied.stdout
    assert not old.exists()
    refused = subprocess.run([*command[:-1], str(legacy), "--delete"], capture_output=True, text=True, timeout=15)
    assert refused.returncode == 0
    assert "WARNING" in refused.stderr
    assert keep.read_text(encoding="utf-8") == "keep"
