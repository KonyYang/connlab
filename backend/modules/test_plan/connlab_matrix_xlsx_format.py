"""Pure schema helpers for ConnLab Matrix XLSX round-trips."""

from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Iterable, Mapping


METADATA_SHEET_NAME = "__ConnLab_Metadata"
METADATA_SCHEMA = "connlab.matrix.xlsx"
METADATA_VERSION = "1"


def visible_matrix_payload(
    *,
    group_labels: Iterable[str],
    rows: Iterable[Mapping[str, Any]],
    sample_sizes: Iterable[str],
    time_displays: Iterable[str],
    fees: Iterable[str],
) -> dict[str, Any]:
    """Return the canonical user-visible Matrix content used for stale checks."""
    return {
        "group_labels": [str(value or "") for value in group_labels],
        "rows": [
            {
                "test_item": str(row.get("test_item") or ""),
                "section": str(row.get("section") or ""),
                "test_method": str(row.get("test_method") or ""),
                "condition": str(row.get("condition") or ""),
                "requirement": str(row.get("requirement") or ""),
                "steps": [str(value or "") for value in row.get("steps", ())],
                "note": str(row.get("note") or ""),
            }
            for row in rows
        ],
        "sample_sizes": [str(value or "") for value in sample_sizes],
        "time_displays": [str(value or "") for value in time_displays],
        "fees": [str(value or "") for value in fees],
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def visible_matrix_fingerprint(payload: Mapping[str, Any]) -> str:
    return canonical_fingerprint(payload)


def canonical_fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(canonical_json(payload).encode("utf-8")).hexdigest()
