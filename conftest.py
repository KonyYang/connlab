"""Managed pytest storage, with compact scratch for Windows path-budget tests."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile

import pytest

from scripts.pytest_artifacts import DEFAULT_ROOT, cleanup, configured_root, start_run


_EXPLICIT_BASETEMP = pytest.StashKey[bool]()


def _start(root: Path):
    for message in cleanup(root, dry_run=False).warnings:
        print(f"[ConnLab pytest artifacts] {message}", file=sys.stderr)
    try:
        return start_run(root)
    except (OSError, ValueError) as error:
        raise pytest.UsageError(f"Cannot initialize pytest artifact storage at {root}: {error}") from error


def _finish(run) -> None:
    try:
        run.finish()
    except (OSError, ValueError) as error:
        print(f"[ConnLab pytest artifacts] Completion not recorded; run retained: {error}", file=sys.stderr)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    explicit = config.option.basetemp is not None
    config.stash[_EXPLICIT_BASETEMP] = explicit
    if explicit:
        return
    run = _start(configured_root())
    config.option.basetemp = str(run.scratch)
    # This lease outlives session fixtures and every other configure hook.
    config.add_cleanup(lambda: _finish(run))


@pytest.fixture(scope="session")
def _portable_scratch(pytestconfig):
    if pytestconfig.stash[_EXPLICIT_BASETEMP]:
        yield None
        return
    default = DEFAULT_ROOT.parent / "p" if os.name == "nt" else Path(tempfile.gettempdir()) / "connlab-pytest"
    root = Path(os.environ.get("CONNLAB_PYTEST_PORTABLE_ROOT", str(default)))
    run = _start(root)
    try:
        run.scratch.mkdir()
        yield run.scratch
    finally:
        _finish(run)


@pytest.fixture
def portable_tmp_path(_portable_scratch, tmp_path_factory) -> Path:
    """Keep controlled Windows boundary cases independent of evidence-root length."""
    if _portable_scratch is None:
        return tmp_path_factory.mktemp("portable")
    return Path(tempfile.mkdtemp(prefix="w", dir=_portable_scratch))
