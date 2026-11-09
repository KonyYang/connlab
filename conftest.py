"""Keep default pytest scratch on D; explicit --basetemp remains caller-owned."""
from __future__ import annotations

import sys

import pytest

from scripts.pytest_artifacts import cleanup, configured_root, start_run


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    if config.option.basetemp is not None:
        return
    root = configured_root()
    for message in cleanup(root, dry_run=False).warnings:
        print(f"[ConnLab pytest artifacts] {message}", file=sys.stderr)
    try:
        run = start_run(root)
    except (OSError, ValueError) as error:
        raise pytest.UsageError(f"Cannot initialize pytest artifact storage at {root}: {error}") from error
    config.option.basetemp = str(run.scratch)

    def finish() -> None:
        try:
            run.finish()
        except (OSError, ValueError) as error:
            print(f"[ConnLab pytest artifacts] Completion not recorded; run retained: {error}", file=sys.stderr)

    # Registered before other configure hooks; pytest executes cleanups in reverse
    # order, so the lease survives session teardown and fixture finalization.
    config.add_cleanup(finish)
