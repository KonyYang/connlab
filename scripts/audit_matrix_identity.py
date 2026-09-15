"""Run the Matrix identity integrity audit against one or more SQLite files."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from backend.infrastructure.storage.matrix_identity_integrity_audit import (
    audit_matrix_identity_database,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only audit of Matrix draft and confirmed-authority identities."
    )
    parser.add_argument(
        "database",
        type=Path,
        nargs="+",
        help="SQLite database path. The file is opened in read-only mode.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return exit code 2 when an error-severity finding exists.",
    )
    args = parser.parse_args()

    reports = [audit_matrix_identity_database(path) for path in args.database]
    payload = []
    for report in reports:
        item = asdict(report)
        item["database_path"] = str(report.database_path)
        item["finding_counts"] = report.finding_counts
        payload.append(item)
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    if args.strict and any(report.finding_counts["error"] for report in reports):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
