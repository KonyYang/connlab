"""Tests for the source-faithful Unit Price Reference snapshot loader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import pytest

from backend.modules.fee_evaluation.fee_reference_snapshot import (
    FeeReferenceSnapshotValidationError,
    load_fee_reference_snapshot,
)


_SOURCE_HASH = "sha256:fb788038631aa0a12f1a052b630513718d9fa1bb64bae647e897e18529ef8a5d"


def _row(source_row: int) -> dict[str, object]:
    return {
        "source_row": source_row,
        "english_description": f"Test {source_row}",
        "chinese_description": f"测试 {source_row}",
        "base_fee_text": "100",
        "unit_price_text": "10/reading",
        "applicable_standard": "Standard",
        "range_condition": "Range",
        "chamber_or_note": "Note",
    }


def _rows(start: int, end: int) -> list[dict[str, object]]:
    return [_row(source_row) for source_row in range(start, end + 1)]


def _policy(source_row: int) -> dict[str, object]:
    return {
        "source_row": source_row,
        "policy_type": "discount_principles",
        "text": "Complete discount policy text.",
    }


def test_load_fee_reference_snapshot_requires_exact_authority_rows(tmp_path: Path) -> None:
    path = _write_snapshot(tmp_path, rows=_rows(4, 47), policies=[_policy(49)])

    snapshot = load_fee_reference_snapshot(path)

    assert snapshot.source.source_file_name == "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls"
    assert snapshot.source.source_sheet == "Unit Price Reference"
    assert snapshot.source.source_hash == _SOURCE_HASH
    assert tuple(row.source_row for row in snapshot.rows) == tuple(range(4, 48))
    assert tuple(policy.source_row for policy in snapshot.policies) == (49,)


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        (_rows(5, 47), "Missing effective source rows: 4"),
        (_rows(4, 47) + [_row(47)], "Duplicate source row: 47"),
        (_rows(4, 48), "Unexpected effective source rows: 48"),
    ],
)
def test_load_fee_reference_snapshot_rejects_invalid_row_coverage(
    tmp_path: Path,
    rows: list[dict[str, object]],
    message: str,
) -> None:
    path = _write_snapshot(tmp_path, rows=rows, policies=[_policy(49)])

    with pytest.raises(FeeReferenceSnapshotValidationError, match=message):
        load_fee_reference_snapshot(path)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda payload: payload["source"].update({"source_sheet": "Testing Prices"}), "source sheet"),
        (lambda payload: payload["source"].update({"source_hash": "sha256:" + "0" * 64}), "source hash"),
        (lambda payload: payload.update({"policies": []}), "Missing policy rows: 49"),
        (lambda payload: payload["rows"][0].update({"english_description": ""}), "English description"),
    ],
)
def test_load_fee_reference_snapshot_rejects_invalid_authority_metadata(
    tmp_path: Path,
    mutate: Callable[[dict[str, object]], object],
    message: str,
) -> None:
    payload = _snapshot_payload(rows=_rows(4, 47), policies=[_policy(49)])
    mutate(payload)
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(FeeReferenceSnapshotValidationError, match=message):
        load_fee_reference_snapshot(path)


def _write_snapshot(
    tmp_path: Path,
    *,
    rows: list[dict[str, object]],
    policies: list[dict[str, object]],
) -> Path:
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(_snapshot_payload(rows=rows, policies=policies)), encoding="utf-8")
    return path


def _snapshot_payload(
    *,
    rows: list[dict[str, object]],
    policies: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "source": {
            "source_file_name": "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls",
            "source_sheet": "Unit Price Reference",
            "source_hash": _SOURCE_HASH,
            "captured_at": "2026-07-16T00:00:00+08:00",
        },
        "rows": rows,
        "policies": policies,
    }

