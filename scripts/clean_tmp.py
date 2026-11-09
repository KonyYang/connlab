"""Preview managed pytest retention; --delete applies it. Generic tmp is never swept."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__:
    from .pytest_artifacts import cleanup, configured_root
else:
    from pytest_artifacts import cleanup, configured_root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", "--tmp-dir", dest="root", type=Path, default=configured_root())
    parser.add_argument("--retention-days", type=float, default=7)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--delete", action="store_true", help="Delete eligible completed managed runs.")
    action.add_argument("--dry-run", action="store_true", help="Preview only (the default).")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = cleanup(args.root, dry_run=not args.delete, retention_days=args.retention_days)
    except ValueError as error:
        parser.error(str(error))
    for message in result.warnings:
        print(f"WARNING: {message}", file=sys.stderr)
    if not args.quiet:
        for path in result.candidates:
            print(f"{'DELETED' if path in result.deleted else 'CANDIDATE'} {path}")
    print(f"Managed pytest retention: {len(result.candidates)} eligible, {len(result.deleted)} deleted, "
          f"{len(result.warnings)} preserved/skipped diagnostics; {'apply' if args.delete else 'dry-run'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
